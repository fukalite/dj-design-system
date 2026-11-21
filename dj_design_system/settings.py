"""Legacy compatibility settings facade delegating to ``dj_design_system.services.config``."""

from __future__ import annotations

import warnings
from collections.abc import Mapping, Sequence
from typing import Any

from django.conf import settings

from dj_design_system.config import DesignSystemSettings
from dj_design_system.exceptions import RemovedInDjDS10Warning
from dj_design_system.services import config as config_service
from dj_design_system.services.media import coerce_path_list
from dj_design_system.types import (
    DocVariantConfig,
    DocVariantStrategy,
    FlattenStrategy,
    NodeType,
    Theme,
    WebpackBundleSpec,
)


BUILTIN_DOC_VARIANTS: dict[str, dict[str, Any]] = {
    "minimal": {
        "name": "basic",
        "label": "Minimal example",
        "strategy": DocVariantStrategy.MINIMAL.value,
        "show_in_docs": True,
    },
    "maximal": {
        "name": "maximal",
        "label": "All parameters",
        "strategy": DocVariantStrategy.MAXIMAL.value,
        "show_in_docs": True,
    },
    "defaults": {
        "name": "defaults",
        "label": "Default values",
        "strategy": DocVariantStrategy.DEFAULTS.value,
        "show_in_docs": False,
    },
    "all_slots": {
        "name": "all_slots",
        "label": "All slots",
        "strategy": DocVariantStrategy.ALL_SLOTS.value,
        "show_in_docs": False,
    },
}

BUILTIN_CANVAS_BACKGROUNDS: dict[str, dict[str, str]] = {
    "white": {"label": "White", "color": "#ffffff"},
    "light-grey": {"label": "Light Grey", "color": "#f0f0f0"},
    "dark-grey": {"label": "Dark Grey", "color": "#404040"},
    "black": {"label": "Black", "color": "#000000"},
    "checkerboard": {
        "label": "Checkerboard",
        "color": (
            "repeating-conic-gradient(#e0e0e0 0% 25%, transparent 0% 50%) "
            "0 0 / 20px 20px #ffffff"
        ),
    },
}

DEFAULTS: dict[str, Any] = {
    "DESIGN_SYSTEM_NAME": "Django Design System",
    "ENABLE_GALLERY": True,
    "GALLERY_IS_PUBLIC": True,
    "GALLERY_NAV_ORDER": [NodeType.FOLDER, NodeType.COMPONENT, NodeType.DOCUMENT],
    "GLOBAL_CSS": [],
    "GLOBAL_JS": [],
    "GLOBAL_CSS_BUNDLES": [],
    "GLOBAL_JS_BUNDLES": [],
    "GALLERY_CANVAS_BACKGROUNDS": BUILTIN_CANVAS_BACKGROUNDS,
    "GALLERY_CANVAS_EXTRA_BACKGROUNDS": {},
    "GALLERY_CANVAS_DEFAULT_BACKGROUND": "light-grey",
    "GALLERY_CANVAS_HTML_ATTRS": {},
    "GALLERY_CODEHILITE_STYLE": "monokai",
    "GALLERY_THEMES": {
        "default": {
            "label": "Default",
            "html_attrs": {},
            "css": [],
            "js": [],
            "css_bundles": [],
            "js_bundles": [],
        },
    },
    "GALLERY_DEFAULT_THEME": "default",
    "GALLERY_UI_THEMES": {
        "desert": {
            "label": "Desert",
            "dark_mode": {},
        },
        "classic": {
            "label": "Classic",
        },
    },
    "GALLERY_DEFAULT_UI_THEME": "desert",
    "GALLERY_INCLUDE_APPS": None,
    "GALLERY_EXCLUDE_APPS": [],
    "GALLERY_EXTRA_CSS": [],
    "GALLERY_DOC_VARIANTS": BUILTIN_DOC_VARIANTS,
    "APP_THEMES": {},
    "APP_CSS": {},
    "APP_CSS_BUNDLES": {},
    "APP_JS": {},
    "APP_JS_BUNDLES": {},
    "APP_CANVAS_HTML_ATTRS": {},
    "COMPONENT_DIRECTORIES": {},
    "COMPONENT_NAMESPACES": {},
}

_PATH_LIST_SETTINGS = {"GLOBAL_CSS", "GLOBAL_JS", "GALLERY_EXTRA_CSS"}


def _read_typed_setting(attr: str) -> Any:
    cfg = config_service.get_config()
    if attr == "DESIGN_SYSTEM_NAME":
        return cfg.name
    if attr == "ENABLE_GALLERY":
        return cfg.gallery.enabled
    if attr == "GALLERY_IS_PUBLIC":
        return cfg.gallery.is_public
    if attr == "GALLERY_NAV_ORDER":
        return (
            cfg.gallery.nav_order
            if isinstance(cfg.gallery.nav_order, str)
            else list(cfg.gallery.nav_order)
        )
    if attr == "GLOBAL_CSS":
        return list(cfg.css)
    if attr == "GLOBAL_JS":
        return list(cfg.js)
    if attr == "GLOBAL_CSS_BUNDLES":
        return list(cfg.css_bundles)
    if attr == "GLOBAL_JS_BUNDLES":
        return list(cfg.js_bundles)
    if attr == "GALLERY_CANVAS_DEFAULT_BACKGROUND":
        return cfg.canvas.default_background
    if attr == "GALLERY_CANVAS_BACKGROUNDS":
        return {
            slug: {"label": bg.label, "color": bg.color}
            for slug, bg in cfg.canvas.backgrounds.items()
        }
    if attr == "GALLERY_CANVAS_EXTRA_BACKGROUNDS":
        return {}
    if attr == "GALLERY_CANVAS_HTML_ATTRS":
        return {
            k: dict(v)
            for k, v in cfg.canvas.html_attrs.items()
            if isinstance(v, Mapping)
        }
    if attr == "GALLERY_CODEHILITE_STYLE":
        return cfg.gallery.codehilite_style or ""
    if attr == "GALLERY_THEMES":
        return dict(cfg.themes)
    if attr == "GALLERY_DEFAULT_THEME":
        return cfg.default_theme
    if attr == "GALLERY_UI_THEMES":
        return dict(cfg.gallery.ui_themes)
    if attr == "GALLERY_DEFAULT_UI_THEME":
        return cfg.gallery.default_ui_theme
    if attr == "GALLERY_INCLUDE_APPS":
        if cfg.gallery.include_apps is None:
            return None
        if isinstance(cfg.gallery.include_apps, (list, tuple)):
            return list(cfg.gallery.include_apps)
        return cfg.gallery.include_apps
    if attr == "GALLERY_EXCLUDE_APPS":
        if isinstance(cfg.gallery.exclude_apps, (list, tuple)):
            return list(cfg.gallery.exclude_apps)
        return cfg.gallery.exclude_apps
    if attr == "GALLERY_EXTRA_CSS":
        return list(cfg.gallery.extra_css)
    if attr == "GALLERY_DOC_VARIANTS":
        return dict(cfg.gallery.doc_variants)

    all_apps = config_service.get_all_app_settings()
    if attr == "APP_THEMES":
        return {
            label: list(app.themes)
            for label, app in all_apps.items()
            if app.themes is not None
        }
    if attr == "APP_CSS":
        return {label: list(app.css) for label, app in all_apps.items() if app.css}
    if attr == "APP_JS":
        return {label: list(app.js) for label, app in all_apps.items() if app.js}
    if attr == "APP_CSS_BUNDLES":
        return {
            label: list(app.css_bundles)
            for label, app in all_apps.items()
            if app.css_bundles
        }
    if attr == "APP_JS_BUNDLES":
        return {
            label: list(app.js_bundles)
            for label, app in all_apps.items()
            if app.js_bundles
        }
    if attr == "APP_CANVAS_HTML_ATTRS":
        return {
            label: {k: dict(v) for k, v in app.canvas_html_attrs.items()}
            for label, app in all_apps.items()
            if app.canvas_html_attrs
        }
    if attr == "COMPONENT_DIRECTORIES":
        result: dict[str, dict[str, Any]] = {}
        for label, app in all_apps.items():
            entry: dict[str, Any] = {}
            if (
                app.prefix is not None
                or app.label is not None
                or app.flatten != FlattenStrategy.NONE
            ):
                root_entry: dict[str, Any] = {}
                if app.prefix is not None:
                    root_entry["prefix"] = app.prefix
                    root_entry["flatten"] = app.flatten
                elif app.flatten != FlattenStrategy.NONE:
                    root_entry["flatten"] = app.flatten
                if app.label is not None:
                    root_entry["label"] = app.label
                entry[""] = root_entry
            for path, dir_cfg in app.directories.items():
                dir_entry: dict[str, Any] = {}
                if dir_cfg.prefix is not None:
                    dir_entry["prefix"] = dir_cfg.prefix
                if dir_cfg.flatten is not None:
                    dir_entry["flatten"] = dir_cfg.flatten
                if dir_cfg.label is not None:
                    dir_entry["label"] = dir_cfg.label
                if dir_cfg.promote_to_app:
                    dir_entry["promote_to_app"] = True
                entry[path] = dir_entry
            if entry:
                result[label] = entry
        return result
    if attr == "COMPONENT_NAMESPACES":
        return {}
    raise AttributeError(f"No value set for DJ_DESIGN_SYSTEM['{attr}']")


class DjangoDesignSystemSettings:
    """Read-through facade exposing legacy flat setting attribute names."""

    DESIGN_SYSTEM_NAME: str
    ENABLE_GALLERY: bool
    GALLERY_IS_PUBLIC: bool
    GALLERY_NAV_ORDER: list[NodeType | str] | str
    GLOBAL_CSS: list[str]
    GLOBAL_JS: list[str]
    GLOBAL_CSS_BUNDLES: list[WebpackBundleSpec]
    GLOBAL_JS_BUNDLES: list[WebpackBundleSpec]
    GALLERY_CANVAS_DEFAULT_BACKGROUND: str
    GALLERY_CANVAS_BACKGROUNDS: dict[str, dict[str, str]]
    GALLERY_CANVAS_EXTRA_BACKGROUNDS: dict[str, dict[str, str]]
    GALLERY_CANVAS_HTML_ATTRS: dict[str, Any]
    GALLERY_CODEHILITE_STYLE: str
    GALLERY_THEMES: dict[str, Any]
    GALLERY_DEFAULT_THEME: str
    GALLERY_UI_THEMES: dict[str, Any]
    GALLERY_DEFAULT_UI_THEME: str
    GALLERY_INCLUDE_APPS: list[str] | None
    GALLERY_EXCLUDE_APPS: list[str]
    GALLERY_EXTRA_CSS: list[str]
    GALLERY_DOC_VARIANTS: Mapping[str, Any] | Sequence[Any]
    APP_THEMES: dict[str, list[str]]
    APP_CSS: dict[str, list[str] | str]
    APP_CSS_BUNDLES: dict[str, list[WebpackBundleSpec]]
    APP_JS: dict[str, list[str] | str]
    APP_JS_BUNDLES: dict[str, list[WebpackBundleSpec]]
    APP_CANVAS_HTML_ATTRS: dict[str, dict[str, Any]]
    COMPONENT_DIRECTORIES: dict[str, dict[str, Any]]
    COMPONENT_NAMESPACES: dict[str, dict[str, Any]]

    def __getattr__(self, attr: str) -> Any:
        if attr not in DEFAULTS:
            raise AttributeError(f"No value set for DJ_DESIGN_SYSTEM['{attr}']")

        raw = getattr(settings, "DJ_DESIGN_SYSTEM", None)
        if isinstance(raw, DesignSystemSettings) or raw is None:
            return _read_typed_setting(attr)

        if isinstance(raw, Mapping):
            if attr == "COMPONENT_NAMESPACES":
                value = raw.get("COMPONENT_NAMESPACES", {})
                if value:
                    warnings.warn(
                        "COMPONENT_NAMESPACES is deprecated and will be removed in 1.0.0. "
                        "Please migrate to AppSettings(prefix=..., directories=...).",
                        RemovedInDjDS10Warning,
                        stacklevel=2,
                    )
                return value
            if attr in ("GALLERY_INCLUDE_APPS", "GALLERY_EXCLUDE_APPS") and attr in raw:
                return raw[attr]
            if attr == "GALLERY_CANVAS_EXTRA_BACKGROUNDS":
                return raw.get(attr) or {}
            if attr == "GALLERY_CANVAS_BACKGROUNDS" and attr in raw:
                return raw[attr]
            if attr in _PATH_LIST_SETTINGS and attr in raw:
                return coerce_path_list(raw[attr] or [])
            return _read_typed_setting(attr)

        return _read_typed_setting(attr)


dds_settings = DjangoDesignSystemSettings()


def get_backgrounds() -> list[dict[str, str]]:
    """Return the merged list of canvas backgrounds as ``{"value", "label", "color"}`` dicts."""
    return [
        {"value": slug, "label": bg.label, "color": bg.color}
        for slug, bg in config_service.get_backgrounds().items()
    ]


def get_default_background() -> dict[str, str]:
    """Return the default background as a ``{"value", "label", "color"}`` dict."""
    bg = config_service.get_default_background()
    slug = config_service.get_default_background_slug()
    return {"value": slug, "label": bg.label, "color": bg.color}


def get_themes() -> list[Theme]:
    """Return the list of configured component themes."""
    return list(config_service.get_themes().values())


def get_gallery_ui_themes() -> list[Theme]:
    """Return the list of configured gallery UI themes."""
    return list(config_service.get_gallery_ui_themes().values())


def get_gallery_ui_theme(identifier: str) -> Theme | None:
    """Return the gallery UI theme matching *identifier*, or ``None``."""
    return config_service.get_gallery_ui_theme(identifier=identifier)


def get_default_gallery_ui_theme() -> Theme:
    """Return the default gallery UI theme."""
    return config_service.get_default_gallery_ui_theme()


def get_theme(identifier: str) -> Theme | None:
    """Return the component theme matching *identifier*, or ``None``."""
    return config_service.get_theme(identifier=identifier)


def get_default_theme() -> Theme:
    """Return the default component theme."""
    return config_service.get_default_theme()


def get_app_static(app_label: str) -> tuple[list[str], list[str]]:
    """Return a tuple of ``(css_paths, js_paths)`` for *app_label*."""
    resolved = config_service.get_app_settings(app_label=app_label)
    return list(resolved.css), list(resolved.js)


def get_app_html_attrs(app_label: str) -> dict[str, dict[str, str]]:
    """Return app-specific canvas HTML attributes for *app_label*."""
    resolved = config_service.get_app_settings(app_label=app_label)
    return {
        section: dict(pairs) for section, pairs in resolved.canvas_html_attrs.items()
    }


def resolve_doc_variants(
    *,
    raw_setting: Mapping[str, Any] | Sequence[Any] | None = None,
    base_variants: Sequence[DocVariantConfig] | None = None,
) -> list[DocVariantConfig]:
    """Resolve documentation variants by applying *raw_setting* over *base_variants*."""
    return config_service.resolve_doc_variants(
        raw_setting=raw_setting,
        base_variants=base_variants,
    )


def get_doc_variants() -> list[DocVariantConfig]:
    """Return normalized standard documentation variant configurations."""
    return list(config_service.get_doc_variants())


def get_doc_variant_by_key(*, key: str) -> DocVariantConfig | None:
    """Return the ``DocVariantConfig`` matching *key*, or ``None``."""
    return config_service.get_doc_variant(key=key)
