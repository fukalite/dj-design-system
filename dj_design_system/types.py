from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any


class NodeType(enum.Enum):
    """Discriminates the kind of navigation node."""

    APP = "app"
    FOLDER = "folder"
    COMPONENT = "component"
    DOCUMENT = "document"


class TagType(enum.Enum):
    """The type of template tag a component should be registered as."""

    TAG = "tag"
    BLOCK = "block"


class CanvasMode(enum.Enum):
    """Rendering mode for a canvas instance."""

    BASIC = "basic"
    EXTENDED = "extended"


@dataclass
class Theme:
    """A typed configuration for a theme in the design system."""

    value: str
    label: str
    html_attrs: dict[str, Any] = field(default_factory=dict)
    css: list[str] = field(default_factory=list)
    js: list[str] = field(default_factory=list)
    css_bundles: list[tuple[str, ...]] = field(default_factory=list)
    js_bundles: list[tuple[str, ...]] = field(default_factory=list)

    def __getitem__(self, item: str) -> Any:
        try:
            return getattr(self, item)
        except AttributeError:
            raise KeyError(item)

    def get(self, item: str, default: Any = None) -> Any:
        return getattr(self, item, default)

    def keys(self):
        return ("value", "label", "html_attrs", "css", "js", "css_bundles", "js_bundles")

    def items(self):
        return [(k, getattr(self, k)) for k in self.keys()]
