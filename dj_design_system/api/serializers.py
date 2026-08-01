from typing import Any, Iterable

from dj_design_system.data import ComponentInfo


class ComponentSerializer:
    """Default serializer for component metadata."""
    
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
