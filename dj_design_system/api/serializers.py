import logging
from typing import Any, Iterable

from dj_design_system.data import CanvasSpec, ComponentInfo

logger = logging.getLogger(__name__)


from dj_design_system.services.registry import ComponentRegistry, ComponentDoesNotExist, MultipleComponentsFound


class ComponentValidationError(Exception):
    """Raised when a component render request payload is invalid."""
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class ComponentNotFoundError(Exception):
    """Raised when a requested component cannot be found."""
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


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
                self.component_info = self.registry.get_by_name(name, app_label=app_label)
            else:
                # If no app_label, try looking it up (this might raise MultipleComponentsFound)
                from dj_design_system.services.canvas import _resolve_component
                self.component_info = _resolve_component(name, self.registry)
        except ValueError as exc:
            msg = str(exc)
            logger.error(f"Value error when resolving component '{name}': {msg}")
            if "not found" in msg.lower():
                raise ComponentNotFoundError(msg)
            raise ComponentValidationError(msg)
        except ComponentDoesNotExist:
            logger.error(f"Component '{name}' not found.")
            raise ComponentNotFoundError(f"Component '{name}' not found.")
        except MultipleComponentsFound:
            logger.error(f"Component '{name}' is ambiguous.")
            raise ComponentValidationError(f"Component '{name}' is ambiguous. Please provide 'app_label'.")
            
    def to_spec(self) -> CanvasSpec:
        if not self.component_info:
            raise RuntimeError("Must call validate() before to_spec()")
            
        return CanvasSpec(
            component_name=self.component_info.qualified_name,
            params=self.data.get("params", {}),
            positional_args=self.data.get("positional_args", []),
        )
