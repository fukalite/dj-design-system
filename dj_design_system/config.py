"""Typed project and app-level settings dataclasses for dj-design-system.

This module imports only the Python standard library and ``dj_design_system.types``
so it can be imported safely at the top of any Django ``settings.py`` or ``apps.py``
before Django settings or the app registry are initialised.
"""

from __future__ import annotations

import dataclasses
import enum
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Final, Self

from dj_design_system.types import (
    CanvasBackground,
    DarkModeConfig,
    DocVariantConfig,
    DocVariantStrategy,
    FlattenStrategy,
    FrozenMapping,
    HtmlAttrsDict,
    HtmlAttrsInput,
    NavOrderSpec,
    NodeType,
    Theme,
    WebpackBundleSpec,
    coerce_bundle_tuple,
    coerce_canvas_background,
    coerce_str_tuple,
    freeze_html_attrs,
)


class _UnsetType(enum.Enum):
    """Sentinel type distinguishing omitted fields from explicit ``None`` values."""

    UNSET = "UNSET"

    def __repr__(self) -> str:
        return "UNSET"

    def __bool__(self) -> bool:
        return False


UNSET: Final[_UnsetType] = _UnsetType.UNSET


def _coerce_nav_order(
    value: Sequence[NodeType | str] | str,
    *,
    field_name: str,
) -> NavOrderSpec:
    if value == "alphabetical":
        return "alphabetical"
    if isinstance(value, (str, bytes, bytearray)):
        raise TypeError(
            f"{field_name} must be 'alphabetical' or a sequence of NodeType/slug entries."
        )
    if not isinstance(value, Sequence):
        raise TypeError(
            f"{field_name} must be 'alphabetical' or a sequence of NodeType/slug entries."
        )
    return tuple(value)


def _coerce_slug_sequence(
    value: Sequence[str] | set[str] | frozenset[str],
    *,
    field_name: str,
) -> tuple[str, ...]:
    if isinstance(value, (str, bytes, bytearray)):
        raise TypeError(
            f"{field_name} must be a sequence of strings, not a bare string."
        )
    if not isinstance(value, (Sequence, set, frozenset)):
        raise TypeError(f"{field_name} must be a sequence of strings.")
    return tuple(str(item) for item in value)


def _hydrate_themes(
    raw: Mapping[str, Theme | Mapping[str, Any]],
) -> FrozenMapping[str, Theme]:
    hydrated: dict[str, Theme] = {}
    for slug, entry in raw.items():
        if isinstance(entry, Theme):
            value = entry.value if entry.value else slug
            label = entry.label if entry.label else value.capitalize()
            if value != entry.value or label != entry.label:
                hydrated[slug] = dataclasses.replace(entry, value=value, label=label)
            else:
                hydrated[slug] = entry
        elif isinstance(entry, Mapping):
            raw_value = str(entry.get("value") or slug)
            raw_label = str(entry.get("label") or raw_value.capitalize())
            hydrated[slug] = Theme(
                value=raw_value,
                label=raw_label,
                html_attrs=entry.get("html_attrs", {}),
                css=entry.get("css", ()),
                js=entry.get("js", ()),
                css_bundles=entry.get("css_bundles", ()),
                js_bundles=entry.get("js_bundles", ()),
                canvas_background=entry.get("canvas_background"),
                dark_mode=entry.get("dark_mode"),
            )
        else:
            raise TypeError(
                f"Theme entry for {slug!r} must be a Theme or mapping, got {type(entry).__name__}."
            )
    return FrozenMapping(hydrated)


def _hydrate_backgrounds(
    raw: Mapping[str, CanvasBackground | Mapping[str, Any]],
) -> FrozenMapping[str, CanvasBackground]:
    hydrated: dict[str, CanvasBackground] = {}
    for slug, entry in raw.items():
        coerced = coerce_canvas_background(entry)
        if not isinstance(coerced, CanvasBackground):
            raise TypeError(
                f"Background entry for {slug!r} must be a CanvasBackground or mapping."
            )
        hydrated[slug] = coerced
    return FrozenMapping(hydrated)


def _hydrate_doc_variants(
    raw: Mapping[str, DocVariantConfig],
) -> FrozenMapping[str, DocVariantConfig]:
    hydrated: dict[str, DocVariantConfig] = {}
    for key, entry in raw.items():
        if not isinstance(entry, DocVariantConfig):
            raise TypeError(
                f"doc_variants entry for {key!r} must be a DocVariantConfig, got {type(entry).__name__}."
            )
        if not entry.key:
            hydrated[key] = dataclasses.replace(entry, key=key)
        else:
            hydrated[key] = entry
    return FrozenMapping(hydrated)


def _validate_directory_path(path: str) -> None:
    if path == "":
        raise ValueError(
            "AppSettings.directories does not accept the empty string key ''; "
            "set prefix, flatten, label, order, or nav_order directly on AppSettings."
        )
    if "/" in path or "\\" in path:
        raise ValueError(
            f"Directory path {path!r} must use dot notation rather than path separators."
        )
    segments = path.split(".")
    if any(not segment for segment in segments):
        raise ValueError(
            f"Directory path {path!r} must not contain leading, trailing, or empty segments."
        )


DDS_DEFAULT_THEMES: FrozenMapping[str, Theme] = FrozenMapping(
    {
        "default": Theme(value="default", label="Default"),
    }
)

DDS_DEFAULT_UI_THEMES: FrozenMapping[str, Theme] = FrozenMapping(
    {
        "desert": Theme(
            value="desert",
            label="Desert",
            dark_mode=DarkModeConfig(),
        ),
        "classic": Theme(value="classic", label="Classic"),
    }
)

DDS_DEFAULT_CANVAS_BACKGROUNDS: FrozenMapping[str, CanvasBackground] = FrozenMapping(
    {
        "white": CanvasBackground(label="White", color="#ffffff"),
        "light-grey": CanvasBackground(label="Light Grey", color="#f0f0f0"),
        "dark-grey": CanvasBackground(label="Dark Grey", color="#404040"),
        "black": CanvasBackground(label="Black", color="#000000"),
        "checkerboard": CanvasBackground(
            label="Checkerboard",
            color=(
                "repeating-conic-gradient(#e0e0e0 0% 25%, transparent 0% 50%) "
                "0 0 / 20px 20px #ffffff"
            ),
        ),
    }
)

DDS_DEFAULT_DOC_VARIANTS: FrozenMapping[str, DocVariantConfig] = FrozenMapping(
    {
        "minimal": DocVariantConfig(
            key="minimal",
            name="basic",
            label="Minimal example",
            strategy=DocVariantStrategy.MINIMAL,
            show_in_docs=True,
        ),
        "maximal": DocVariantConfig(
            key="maximal",
            name="maximal",
            label="All parameters",
            strategy=DocVariantStrategy.MAXIMAL,
            show_in_docs=True,
        ),
        "defaults": DocVariantConfig(
            key="defaults",
            name="defaults",
            label="Default values",
            strategy=DocVariantStrategy.DEFAULTS,
            show_in_docs=False,
        ),
        "all_slots": DocVariantConfig(
            key="all_slots",
            name="all_slots",
            label="All slots",
            strategy=DocVariantStrategy.ALL_SLOTS,
            show_in_docs=False,
        ),
    }
)

DDS_DEFAULT_NAV_ORDER: tuple[NodeType, ...] = (
    NodeType.FOLDER,
    NodeType.COMPONENT,
    NodeType.DOCUMENT,
)


@dataclass(frozen=True)
class DirectorySettings:
    """Configuration for a component subfolder within an app."""

    prefix: str | None = None
    flatten: FlattenStrategy | None = None
    label: str | None = None
    promote_to_app: bool = False
    order: int | None = None
    nav_order: Sequence[NodeType | str] | str | None = None

    def __post_init__(self) -> None:
        if self.nav_order is not None:
            object.__setattr__(
                self,
                "nav_order",
                _coerce_nav_order(self.nav_order, field_name="nav_order"),
            )

    def replace(self, **changes: Any) -> Self:
        """Return a new ``DirectorySettings`` with the given fields replaced."""
        return dataclasses.replace(self, **changes)


@dataclass(frozen=True)
class AppSettings:
    """Per-app defaults (on ``AppConfig.design_system``) or project overrides (in ``DesignSystemSettings.apps``)."""

    label: str | None | _UnsetType = UNSET
    order: int | _UnsetType = UNSET
    nav_order: Sequence[NodeType | str] | str | _UnsetType = UNSET
    prefix: str | None | _UnsetType = UNSET
    flatten: FlattenStrategy | _UnsetType = UNSET
    short_names: bool | _UnsetType = UNSET
    themes: Sequence[str] | set[str] | frozenset[str] | None | _UnsetType = UNSET
    css: str | Sequence[str] | _UnsetType = UNSET
    extra_css: str | Sequence[str] | _UnsetType = UNSET
    js: str | Sequence[str] | _UnsetType = UNSET
    extra_js: str | Sequence[str] | _UnsetType = UNSET
    css_bundles: Sequence[WebpackBundleSpec] | _UnsetType = UNSET
    js_bundles: Sequence[WebpackBundleSpec] | _UnsetType = UNSET
    canvas_html_attrs: HtmlAttrsInput | None | _UnsetType = UNSET
    directories: Mapping[str, DirectorySettings | None] | None | _UnsetType = UNSET

    def __post_init__(self) -> None:
        if self.nav_order is not UNSET:
            object.__setattr__(
                self,
                "nav_order",
                _coerce_nav_order(self.nav_order, field_name="nav_order"),
            )
        if self.themes is not UNSET and self.themes is not None:
            object.__setattr__(
                self,
                "themes",
                _coerce_slug_sequence(self.themes, field_name="themes"),
            )
        if self.css is not UNSET:
            object.__setattr__(
                self, "css", coerce_str_tuple(self.css, field_name="css")
            )
        if self.extra_css is not UNSET:
            object.__setattr__(
                self,
                "extra_css",
                coerce_str_tuple(self.extra_css, field_name="extra_css"),
            )
        if self.js is not UNSET:
            object.__setattr__(self, "js", coerce_str_tuple(self.js, field_name="js"))
        if self.extra_js is not UNSET:
            object.__setattr__(
                self,
                "extra_js",
                coerce_str_tuple(self.extra_js, field_name="extra_js"),
            )
        if self.css_bundles is not UNSET:
            object.__setattr__(
                self,
                "css_bundles",
                coerce_bundle_tuple(self.css_bundles, field_name="css_bundles"),
            )
        if self.js_bundles is not UNSET:
            object.__setattr__(
                self,
                "js_bundles",
                coerce_bundle_tuple(self.js_bundles, field_name="js_bundles"),
            )
        if self.canvas_html_attrs is not UNSET and self.canvas_html_attrs is not None:
            object.__setattr__(
                self, "canvas_html_attrs", freeze_html_attrs(self.canvas_html_attrs)
            )
        if self.directories is not UNSET and self.directories is not None:
            if not isinstance(self.directories, Mapping):
                raise TypeError("directories must be a mapping or None.")
            frozen_dirs: dict[str, DirectorySettings | None] = {}
            for path, entry in self.directories.items():
                if not isinstance(path, str):
                    raise TypeError(f"Directory key must be a string, got {path!r}.")
                _validate_directory_path(path)
                if entry is not None and not isinstance(entry, DirectorySettings):
                    raise TypeError(
                        f"Directory entry for {path!r} must be DirectorySettings or None."
                    )
                frozen_dirs[path] = entry
            object.__setattr__(self, "directories", FrozenMapping(frozen_dirs))

    def replace(self, **changes: Any) -> Self:
        """Return a new ``AppSettings`` with the given fields replaced."""
        return dataclasses.replace(self, **changes)


@dataclass(frozen=True)
class CanvasSettings:
    """Preview canvas iframe backgrounds and document-level HTML attributes."""

    backgrounds: Mapping[str, CanvasBackground] = field(
        default_factory=lambda: DDS_DEFAULT_CANVAS_BACKGROUNDS
    )
    default_background: str = "light-grey"
    html_attrs: HtmlAttrsInput = field(default_factory=FrozenMapping)

    def __post_init__(self) -> None:
        if self.backgrounds is not DDS_DEFAULT_CANVAS_BACKGROUNDS:
            if not isinstance(self.backgrounds, Mapping):
                raise TypeError("backgrounds must be a mapping.")
            object.__setattr__(
                self, "backgrounds", _hydrate_backgrounds(self.backgrounds)
            )
        object.__setattr__(self, "html_attrs", freeze_html_attrs(self.html_attrs))

    def replace(self, **changes: Any) -> Self:
        """Return a new ``CanvasSettings`` with the given fields replaced."""
        return dataclasses.replace(self, **changes)


@dataclass(frozen=True)
class GallerySettings:
    """Gallery UI, access control, app visibility, navigation, and documentation settings."""

    enabled: bool = True
    is_public: bool = True
    app_order: Sequence[str] = ()
    nav_order: Sequence[NodeType | str] | str = DDS_DEFAULT_NAV_ORDER
    codehilite_style: str | None = "monokai"
    ui_themes: Mapping[str, Theme] = field(
        default_factory=lambda: DDS_DEFAULT_UI_THEMES
    )
    default_ui_theme: str = "desert"
    include_apps: Sequence[str] | set[str] | frozenset[str] | None = None
    exclude_apps: Sequence[str] | set[str] | frozenset[str] = ()
    extra_css: str | Sequence[str] = ()
    doc_variants: Mapping[str, DocVariantConfig] = field(
        default_factory=lambda: DDS_DEFAULT_DOC_VARIANTS
    )

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "app_order",
            _coerce_slug_sequence(self.app_order, field_name="app_order"),
        )
        object.__setattr__(
            self,
            "nav_order",
            _coerce_nav_order(self.nav_order, field_name="nav_order"),
        )
        if self.ui_themes is not DDS_DEFAULT_UI_THEMES:
            if not isinstance(self.ui_themes, Mapping):
                raise TypeError("ui_themes must be a mapping.")
            object.__setattr__(self, "ui_themes", _hydrate_themes(self.ui_themes))
        if self.include_apps is not None and isinstance(
            self.include_apps, (list, tuple, set, frozenset)
        ):
            object.__setattr__(
                self,
                "include_apps",
                tuple(str(item) for item in self.include_apps),
            )
        if isinstance(self.exclude_apps, (list, tuple, set, frozenset)):
            object.__setattr__(
                self,
                "exclude_apps",
                tuple(str(item) for item in self.exclude_apps),
            )
        object.__setattr__(
            self,
            "extra_css",
            coerce_str_tuple(self.extra_css, field_name="extra_css"),
        )
        if self.doc_variants is not DDS_DEFAULT_DOC_VARIANTS:
            if not isinstance(self.doc_variants, Mapping):
                raise TypeError("doc_variants must be a mapping.")
            object.__setattr__(
                self, "doc_variants", _hydrate_doc_variants(self.doc_variants)
            )

    def replace(self, **changes: Any) -> Self:
        """Return a new ``GallerySettings`` with the given fields replaced."""
        return dataclasses.replace(self, **changes)


@dataclass(frozen=True)
class DesignSystemSettings:
    """Root typed configuration object assigned to ``settings.DJ_DESIGN_SYSTEM``."""

    name: str = "Django Design System"
    css: str | Sequence[str] = ()
    js: str | Sequence[str] = ()
    css_bundles: Sequence[WebpackBundleSpec] = ()
    js_bundles: Sequence[WebpackBundleSpec] = ()
    themes: Mapping[str, Theme] = field(default_factory=lambda: DDS_DEFAULT_THEMES)
    default_theme: str = "default"
    gallery: GallerySettings = field(default_factory=GallerySettings)
    canvas: CanvasSettings = field(default_factory=CanvasSettings)
    apps: Mapping[str, AppSettings] = field(default_factory=FrozenMapping)

    def __post_init__(self) -> None:
        object.__setattr__(self, "css", coerce_str_tuple(self.css, field_name="css"))
        object.__setattr__(self, "js", coerce_str_tuple(self.js, field_name="js"))
        object.__setattr__(
            self,
            "css_bundles",
            coerce_bundle_tuple(self.css_bundles, field_name="css_bundles"),
        )
        object.__setattr__(
            self,
            "js_bundles",
            coerce_bundle_tuple(self.js_bundles, field_name="js_bundles"),
        )
        if not isinstance(self.gallery, GallerySettings):
            raise TypeError(
                f"gallery must be a GallerySettings instance, got {type(self.gallery).__name__}."
            )
        if not isinstance(self.canvas, CanvasSettings):
            raise TypeError(
                f"canvas must be a CanvasSettings instance, got {type(self.canvas).__name__}."
            )
        if self.themes is not DDS_DEFAULT_THEMES:
            if not isinstance(self.themes, Mapping):
                raise TypeError("themes must be a mapping.")
            object.__setattr__(self, "themes", _hydrate_themes(self.themes))
        if not isinstance(self.apps, Mapping):
            raise TypeError("apps must be a mapping of app_label to AppSettings.")
        if self.apps:
            frozen_apps: dict[str, AppSettings] = {}
            for app_label, app_cfg in self.apps.items():
                if not isinstance(app_label, str) or not app_label:
                    raise ValueError(
                        f"apps key must be a non-empty string, got {app_label!r}."
                    )
                if not isinstance(app_cfg, AppSettings):
                    raise TypeError(
                        f"apps[{app_label!r}] must be an AppSettings instance, got {type(app_cfg).__name__}."
                    )
                frozen_apps[app_label] = app_cfg
            object.__setattr__(self, "apps", FrozenMapping(frozen_apps))
        elif not isinstance(self.apps, FrozenMapping):
            object.__setattr__(self, "apps", FrozenMapping())

    def replace(self, **changes: Any) -> Self:
        """Return a new ``DesignSystemSettings`` with the given fields replaced."""
        return dataclasses.replace(self, **changes)


__all__ = [
    "AppSettings",
    "CanvasBackground",
    "CanvasSettings",
    "DDS_DEFAULT_CANVAS_BACKGROUNDS",
    "DDS_DEFAULT_DOC_VARIANTS",
    "DDS_DEFAULT_NAV_ORDER",
    "DDS_DEFAULT_THEMES",
    "DDS_DEFAULT_UI_THEMES",
    "DarkModeConfig",
    "DesignSystemSettings",
    "DirectorySettings",
    "DocVariantConfig",
    "FlattenStrategy",
    "FrozenMapping",
    "GallerySettings",
    "HtmlAttrsDict",
    "NavOrderSpec",
    "NodeType",
    "Theme",
    "UNSET",
    "WebpackBundleSpec",
]
