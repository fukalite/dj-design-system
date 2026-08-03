import logging
from typing import Any, Iterable

from dj_design_system.data import CanvasSpec, ComponentInfo
from dj_design_system.exceptions import ComponentNotFoundError, ComponentValidationError
from dj_design_system.services.registry import (
    ComponentDoesNotExist,
    ComponentRegistry,
    MultipleComponentsFound,
)


logger = logging.getLogger(__name__)


class ComponentListSerializer:
    """Serializer for a list of component metadata."""

    def __init__(self, components: Iterable[ComponentInfo]) -> None:
        self.components = components

    def data(self) -> list[dict[str, Any]]:
        return [self.serialize_component(c) for c in self.components]

    def serialize_component(self, component: ComponentInfo) -> dict[str, Any]:
        return {
            "name": component.name,
            "app_label": component.app_label,
            "relative_path": component.relative_path,
            "tag_type": component.tag_type.value,
        }


class ComponentRenderRequestSerializer:
    """Serializer to validate a render request and build a CanvasSpec."""

    def __init__(self, data: dict[str, Any], registry: ComponentRegistry) -> None:
        self.data = data
        self.registry = registry
        self.component_info: ComponentInfo | None = None

    def validate(self) -> None:
        name = self.data.get("name")
        if not name:
            raise ComponentValidationError("Missing 'name' in payload.")

        app_label = self.data.get("app_label")

        try:
            if app_label:
                self.component_info = self.registry.get_by_name(
                    name, app_label=app_label
                )
            else:
                # If no app_label, try looking it up (this might raise MultipleComponentsFound)
                from dj_design_system.services.canvas import resolve_component

                self.component_info = resolve_component(name, self.registry)
        except ValueError as exc:
            msg = str(exc)
            logger.error("Value error when resolving component '%s': %s", name, msg)
            if "not found" in msg.lower():
                raise ComponentNotFoundError(msg)
            raise ComponentValidationError(msg)
        except ComponentDoesNotExist:
            logger.error("Component '%s' not found.", name)
            raise ComponentNotFoundError(f"Component '{name}' not found.")
        except MultipleComponentsFound:
            logger.error("Component '%s' is ambiguous.", name)
            raise ComponentValidationError(
                f"Component '{name}' is ambiguous. Please provide 'app_label'."
            )

    def to_spec(self) -> CanvasSpec:
        if not self.component_info:
            raise RuntimeError("Must call validate() before to_spec()")

        return CanvasSpec(
            component_name=self.component_info.qualified_name,
            params=self.data.get("params", {}),
            positional_args=self.data.get("positional_args", []),
        )
