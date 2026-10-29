from __future__ import annotations

import enum
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


class DocVariantStrategy(str, enum.Enum):
    """Built-in parameter and slot generation strategies for standard documentation variants."""

    MINIMAL = "minimal"
    MAXIMAL = "maximal"
    DEFAULTS = "defaults"
    ALL_SLOTS = "all_slots"
    CUSTOM = "custom"


@dataclass(frozen=True)
class DocVariantConfig:
    """Normalized configuration for a standard documentation variant.

    Attributes:
        key: Identifier key in ``GALLERY_DOC_VARIANTS`` (e.g. ``"minimal"``, ``"maximal"``).
        name: Variant slug matched against ``GalleryConfig.variants`` (e.g. ``"basic"``, ``"maximal"``).
        label: Heading label displayed in the Usage documentation section.
        strategy: Built-in generation strategy used when the variant is not overridden in ``gallery.py``.
        show_in_docs: Whether this variant is included in component documentation by default.
        kwargs: Optional static parameter overrides for custom global variants.
        param_factory: Reserved hook for custom parameter value factory callables.
        slot_factory: Reserved hook for custom slot content factory callables.
    """

    key: str
    name: str
    label: str
    strategy: DocVariantStrategy = DocVariantStrategy.MINIMAL
    show_in_docs: bool = True
    kwargs: dict[str, Any] = field(default_factory=dict)
    param_factory: Callable[..., Any] | None = None
    slot_factory: Callable[..., Any] | None = None


class NodeType(str, enum.Enum):
    """Discriminates the kind of navigation node."""

    APP = "app"
    FOLDER = "folder"
    COMPONENT = "component"
    DOCUMENT = "document"
    VARIANT = "variant"


class TagType(str, enum.Enum):
    """The type of template tag a component should be registered as."""

    TAG = "tag"
    BLOCK = "block"


class CanvasMode(str, enum.Enum):
    """Rendering mode for a canvas instance."""

    BASIC = "basic"
    EXTENDED = "extended"


class FlattenStrategy(str, enum.Enum):
    """Strategy for flattening nested folder structures in component resolution."""

    NONE = "none"
    ALL = "all"
    LEAF = "leaf"


class ColorScheme(str, enum.Enum):
    """W3C color scheme values."""

    LIGHT = "light"
    DARK = "dark"


@dataclass(frozen=True)
class DarkModeConfig:
    """Explicit configuration for how a theme activates dark mode."""

    html_attrs: dict[str, Any] = field(default_factory=dict)
    css: list[str] = field(default_factory=list)
    js: list[str] = field(default_factory=list)
    css_bundles: list[tuple[str, ...]] = field(default_factory=list)
    js_bundles: list[tuple[str, ...]] = field(default_factory=list)
    canvas_background: str | dict | None = None


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
    canvas_background: str | dict | None = None
    dark_mode: DarkModeConfig | None = None

    @property
    def supports_dark_mode(self) -> bool:
        """Return True if this theme explicitly configures dark mode support."""
        return self.dark_mode is not None

    @property
    def has_dark_mode_assets(self) -> bool:
        """Return True if this theme's dark mode loads external CSS or JS assets."""
        return bool(
            self.dark_mode
            and (
                self.dark_mode.css
                or self.dark_mode.js
                or self.dark_mode.css_bundles
                or self.dark_mode.js_bundles
            )
        )

    @property
    def has_external_assets(self) -> bool:
        """Return True if this theme loads external CSS or JS assets."""
        return bool(
            self.css
            or self.js
            or self.css_bundles
            or self.js_bundles
            or self.has_dark_mode_assets
        )
