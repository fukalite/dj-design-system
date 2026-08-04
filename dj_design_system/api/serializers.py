import logging
from typing import Any, Iterable

from django.core.serializers.json import DjangoJSONEncoder
from django.utils.encoding import force_str
from django.utils.functional import Promise

from dj_design_system.data import CanvasSpec, ComponentInfo
from dj_design_system.parameters.base import _get_type_name
from dj_design_system.services.canvas import coerce_single, resolve_component
from dj_design_system.services.registry import (
    ComponentDoesNotExist,
    ComponentRegistry,
    MultipleComponentsFound,
)


logger = logging.getLogger(__name__)


class ComponentListSerializer:
    """Serializer for a list of component metadata, including parameters and slots."""

    def __init__(self, components: Iterable[ComponentInfo]) -> None:
        self.components = list(components)

    @property
    def data(self) -> list[dict[str, Any]]:
        return [self.serialize_component(c) for c in self.components]

    def serialize_default(self, value: Any) -> Any:
        """Safely and efficiently serialize default values to JSON-compatible formats."""
        if value is None:
            return None
        if isinstance(value, Promise):
            return force_str(value)
        if isinstance(value, (str, int, float, bool)):
            return value
        if hasattr(value, "pk"):  # e.g., Django Model
            return getattr(value, "pk")
        if callable(value):
            return getattr(value, "__name__", str(value))
        if isinstance(value, (list, tuple, set)):
            return [self.serialize_default(item) for item in value]
        if isinstance(value, dict):
            return {str(k): self.serialize_default(v) for k, v in value.items()}
        try:
            return DjangoJSONEncoder().default(value)
        except TypeError:
            return force_str(value)

    def serialize_choices(self, choices: Any) -> Any:
        """Normalize and resolve callable, grouped, or lazy choices."""
        if hasattr(choices, "choices"):
            choices = choices.choices
        if callable(choices):
            try:
                choices = choices()
            except Exception as exc:
                logger.warning("Failed to evaluate choices callable: %s", exc)
                return None

        if choices is None:
            return None

        if isinstance(choices, dict):
            return {force_str(k): self.serialize_default(v) for k, v in choices.items()}

        if isinstance(choices, (list, tuple)):
            serialized = []
            for item in choices:
                if isinstance(item, (list, tuple)) and len(item) == 2:
                    key, val = item
                    # Handle grouped choices: (group_label, choices_list)
                    if isinstance(val, (list, tuple)):
                        serialized.append([force_str(key), self.serialize_choices(val)])
                    else:
                        serialized.append([self.serialize_default(key), force_str(val)])
                else:
                    serialized.append(self.serialize_default(item))
            return serialized

        return self.serialize_default(choices)

    def serialize_component(self, component: ComponentInfo) -> dict[str, Any]:
        component_class = component.component_class

        parameters = {}
        for param_name, spec in component_class.get_params().items():
            param_type = getattr(spec, "type", str)
            parameters[param_name] = {
                "type": _get_type_name(param_type),
                "required": getattr(spec, "required", True),
                "default": self.serialize_default(getattr(spec, "default", None)),
                "choices": self.serialize_choices(getattr(spec, "choices", None)),
                "description": str(
                    getattr(spec, "description", "")
                ),  # Resolve lazy descriptions
            }

        slots = {}
        if hasattr(component_class, "has_slots") and component_class.has_slots():
            for slot_name, slot in component_class.get_slots().items():
                slots[slot_name] = {
                    "required": getattr(slot, "required", True),
                    "default": self.serialize_default(getattr(slot, "default", None)),
                    "description": str(getattr(slot, "description", "")),
                }

        return {
            "name": component.name,
            "qualified_name": component.qualified_name,
            "app_label": component.app_label,
            "relative_path": component.relative_path,
            "tag_type": component.tag_type.value,
            "parameters": parameters,
            "slots": slots,
        }


class ComponentRenderRequestSerializer:
    """Serializer to validate a render request and build a CanvasSpec."""

    def __init__(self, data: dict[str, Any], registry: ComponentRegistry) -> None:
        self.data = data
        self.registry = registry
        self.component_info: ComponentInfo | None = None
        self._errors: dict[str, list[str]] = {}
        self._is_valid: bool | None = None
        self._coerced_params: dict[str, Any] = {}
        self._coerced_positional_args: list[Any] = []

    def is_valid(self) -> bool:
        if self._is_valid is not None:
            return self._is_valid

        self._errors = {}
        name = self.data.get("name")
        if not name:
            self._errors["name"] = ["Missing 'name' in payload."]
            self._is_valid = False
            return False

        app_label = self.data.get("app_label")

        # Normalize fully qualified names (e.g., "myapp__button")
        if "__" in name:
            parts = name.split("__")
            extracted_app_label = parts[0]
            short_name = parts[-1]

            if app_label and app_label != extracted_app_label:
                logger.warning(
                    "Mismatched 'app_label' (%s) and qualified name prefix (%s)",
                    app_label,
                    extracted_app_label,
                )
                self._errors["name"] = [
                    "Mismatched 'app_label' and qualified name prefix."
                ]
                self._is_valid = False
                return False

            name = short_name
            app_label = extracted_app_label

        try:
            if app_label:
                self.component_info = self.registry.get_by_name(
                    name, app_label=app_label
                )
            else:
                self.component_info = resolve_component(name, self.registry)
        except ComponentDoesNotExist:
            self._errors["name"] = [f"Component '{name}' not found."]
        except MultipleComponentsFound:
            self._errors["name"] = [
                f"Component '{name}' is ambiguous. Please provide 'app_label'."
            ]
        except ValueError as exc:
            self._errors["name"] = [str(exc)]

        if self._errors:
            self._is_valid = False
            return False

        if self.component_info is None:
            self._is_valid = False
            return False

        # Coerce parameters and positional arguments
        component_class = self.component_info.component_class
        param_specs = component_class.get_params()
        positional_arg_names = component_class.get_positional_args()

        # Validate and normalize 'params'
        raw_params = self.data.get("params")
        if raw_params is None:
            raw_params = {}
        elif not isinstance(raw_params, dict):
            self._errors["params"] = ["'params' must be a JSON object (dictionary)."]
            self._is_valid = False
            return False

        # Validate and normalize 'positional_args'
        raw_positional = self.data.get("positional_args")
        if raw_positional is None:
            raw_positional = []
        elif not isinstance(raw_positional, list):
            self._errors["positional_args"] = [
                "'positional_args' must be a JSON array (list)."
            ]
            self._is_valid = False
            return False

        # Coerce named parameters
        self._coerced_params = {}
        for key, val in raw_params.items():
            if key in param_specs:
                try:
                    self._coerced_params[key] = coerce_single(
                        key, val, param_specs[key]
                    )
                except ValueError as exc:
                    self._errors.setdefault("params", []).append(str(exc))
            else:
                self._coerced_params[key] = val

        # Coerce positional arguments
        self._coerced_positional_args = []
        for i, val in enumerate(raw_positional):
            if i < len(positional_arg_names):
                arg_name = positional_arg_names[i]
                spec = param_specs.get(arg_name)
                if spec:
                    try:
                        self._coerced_positional_args.append(
                            coerce_single(arg_name, val, spec)
                        )
                    except ValueError as exc:
                        self._errors.setdefault("positional_args", []).append(str(exc))
                else:
                    self._coerced_positional_args.append(val)
            else:
                self._coerced_positional_args.append(val)

        self._is_valid = not bool(self._errors)
        return self._is_valid

    @property
    def errors(self) -> dict[str, list[str]]:
        if self._is_valid is None:
            self.is_valid()
        return self._errors

    def to_spec(self) -> CanvasSpec:
        if not self.component_info or not self._is_valid:
            raise RuntimeError(
                "Must call is_valid() and ensure it returns True before calling to_spec()"
            )

        return CanvasSpec(
            component_name=self.component_info.qualified_name,
            params=self._coerced_params,
            positional_args=tuple(self._coerced_positional_args),
        )
