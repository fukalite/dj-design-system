import logging
from typing import Any, Iterable

from dj_design_system.data import CanvasSpec, ComponentInfo
from dj_design_system.parameters.base import _get_type_name
from dj_design_system.services.canvas import resolve_component
from dj_design_system.services.registry import (
    ComponentDoesNotExist,
    ComponentRegistry,
    MultipleComponentsFound,
)


logger = logging.getLogger(__name__)


class ComponentListSerializer:
    """Serializer for a list of component metadata, including parameters and slots."""

    def __init__(self, components: Iterable[ComponentInfo]) -> None:
        self.components = components

    @property
    def data(self) -> list[dict[str, Any]]:
        return [self.serialize_component(c) for c in self.components]

    def serialize_default(self, value: Any) -> Any:
        """Safely serialize default values to JSON-compatible formats."""
        if value is None:
            return None
        if isinstance(value, (str, int, float, bool)):
            return value
        if hasattr(value, "pk"):  # e.g., Django Model
            return getattr(value, "pk")
        if callable(value):
            return getattr(value, "__name__", str(value))
        try:
            import json

            json.dumps(value)
            return value
        except (TypeError, OverflowError):
            return str(value)

    def serialize_component(self, component: ComponentInfo) -> dict[str, Any]:
        component_class = component.component_class

        # Introspect and serialize parameters (properties)
        parameters = {}
        for param_name, spec in component_class.get_params().items():
            param_type = getattr(spec, "type", str)
            parameters[param_name] = {
                "type": _get_type_name(param_type),
                "required": getattr(spec, "required", True),
                "default": self.serialize_default(getattr(spec, "default", None)),
                "choices": getattr(spec, "choices", None),
                "description": getattr(spec, "description", ""),
            }

        # Introspect and serialize slots if applicable
        slots = {}
        if hasattr(component_class, "has_slots") and component_class.has_slots():
            for slot_name, slot in component_class.get_slots().items():
                slots[slot_name] = {
                    "required": getattr(slot, "required", True),
                    "default": self.serialize_default(getattr(slot, "default", None)),
                    "description": getattr(slot, "description", ""),
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

        self._is_valid = not bool(self._errors)
        return self._is_valid

    @property
    def errors(self) -> dict[str, list[str]]:
        if self._is_valid is None:
            self.is_valid()
        return self._errors

    def to_spec(self) -> CanvasSpec:
        if not self.component_info:
            raise RuntimeError(
                "Must call is_valid() and ensure it returns True before calling to_spec()"
            )

        return CanvasSpec(
            component_name=self.component_info.qualified_name,
            params=self.data.get("params", {}),
            positional_args=self.data.get("positional_args", []),
        )
