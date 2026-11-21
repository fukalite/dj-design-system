"""Legacy flat ``DJ_DESIGN_SYSTEM`` dictionary adapter (0.10.x compatibility)."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from dj_design_system.config import (
    DDS_DEFAULT_CANVAS_BACKGROUNDS,
    DDS_DEFAULT_DOC_VARIANTS,
    DDS_DEFAULT_NAV_ORDER,
    DDS_DEFAULT_THEMES,
    DDS_DEFAULT_UI_THEMES,
    AppSettings,
    CanvasSettings,
    DesignSystemSettings,
    DirectorySettings,
    GallerySettings,
)
from dj_design_system.types import DocVariantConfig, FlattenStrategy, NodeType


def _is_non_bool_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _parse_legacy_flatten(raw_value: Any) -> FlattenStrategy:
    if raw_value is True:
        return FlattenStrategy.ALL
    if raw_value is False or raw_value is None:
        return FlattenStrategy.NONE
    if isinstance(raw_value, FlattenStrategy):
        return raw_value
    if isinstance(raw_value, str):
        try:
            return FlattenStrategy(raw_value)
        except ValueError:
            return FlattenStrategy.NONE
    return FlattenStrategy.NONE


def _parse_legacy_directory_entry(raw_entry: Any) -> DirectorySettings:
    if isinstance(raw_entry, DirectorySettings):
        return raw_entry
    if isinstance(raw_entry, str):
        return DirectorySettings(prefix=raw_entry, flatten=FlattenStrategy.NONE)
    if not isinstance(raw_entry, Mapping):
        return DirectorySettings()

    has_prefix = "prefix" in raw_entry or "namespace" in raw_entry
    has_flatten = "flatten" in raw_entry
    prefix = raw_entry.get("prefix")
    if prefix is None and "namespace" in raw_entry:
        prefix = raw_entry.get("namespace")

    flatten: FlattenStrategy | None = None
    if has_flatten:
        flatten = _parse_legacy_flatten(raw_entry.get("flatten"))
    elif has_prefix:
        flatten = FlattenStrategy.NONE

    raw_order = raw_entry.get("order")
    order = raw_order if _is_non_bool_int(raw_order) else None

    return DirectorySettings(
        prefix=prefix,
        flatten=flatten,
        label=raw_entry.get("label"),
        promote_to_app=bool(raw_entry.get("promote_to_app", False)),
        order=order,
        nav_order=raw_entry.get("nav_order"),
    )


def _adapt_legacy_nav_order(raw_value: Any) -> Any:
    if raw_value == "alphabetical" or not isinstance(raw_value, (list, tuple)):
        return raw_value
    adapted: list[NodeType | str] = []
    for item in raw_value:
        if isinstance(item, NodeType):
            adapted.append(item)
        elif isinstance(item, str):
            try:
                adapted.append(NodeType(item))
            except ValueError:
                adapted.append(item)
        else:
            adapted.append(item)
    return tuple(adapted)


def _adapt_legacy_app_settings(
    *,
    app_label: str,
    app_themes: Mapping[str, Any],
    app_css: Mapping[str, Any],
    app_js: Mapping[str, Any],
    app_css_bundles: Mapping[str, Any],
    app_js_bundles: Mapping[str, Any],
    app_canvas_html_attrs: Mapping[str, Any],
    component_directories: Mapping[str, Any],
    component_namespaces: Mapping[str, Any],
) -> AppSettings:
    kwargs: dict[str, Any] = {}

    if app_label in app_themes:
        raw_theme_val = app_themes[app_label]
        if raw_theme_val is None:
            kwargs["themes"] = None
        elif isinstance(raw_theme_val, str):
            kwargs["themes"] = (raw_theme_val,)
        else:
            kwargs["themes"] = tuple(raw_theme_val)

    if app_label in app_css and app_css[app_label] is not None:
        kwargs["css"] = app_css[app_label]
    if app_label in app_js and app_js[app_label] is not None:
        kwargs["js"] = app_js[app_label]
    if app_label in app_css_bundles and app_css_bundles[app_label] is not None:
        kwargs["css_bundles"] = app_css_bundles[app_label]
    if app_label in app_js_bundles and app_js_bundles[app_label] is not None:
        kwargs["js_bundles"] = app_js_bundles[app_label]
    if app_label in app_canvas_html_attrs:
        kwargs["canvas_html_attrs"] = app_canvas_html_attrs[app_label]

    raw_dirs = component_directories.get(app_label)
    if raw_dirs is None:
        raw_dirs = component_namespaces.get(app_label)

    if isinstance(raw_dirs, Mapping):
        sub_dirs: dict[str, DirectorySettings] = {}
        for path, entry in raw_dirs.items():
            if path == "":
                if isinstance(entry, str):
                    kwargs["prefix"] = entry
                    kwargs["flatten"] = FlattenStrategy.NONE
                elif isinstance(entry, Mapping):
                    has_prefix = "prefix" in entry or "namespace" in entry
                    prefix = entry.get("prefix")
                    if prefix is None and "namespace" in entry:
                        prefix = entry.get("namespace")
                    if has_prefix:
                        kwargs["prefix"] = prefix
                    if "flatten" in entry:
                        kwargs["flatten"] = _parse_legacy_flatten(entry.get("flatten"))
                    if "label" in entry:
                        kwargs["label"] = entry.get("label")
                    raw_order = entry.get("order")
                    if _is_non_bool_int(raw_order):
                        kwargs["order"] = raw_order
                    if "nav_order" in entry and entry.get("nav_order") is not None:
                        kwargs["nav_order"] = _adapt_legacy_nav_order(
                            entry.get("nav_order")
                        )
            elif isinstance(path, str):
                sub_dirs[path] = _parse_legacy_directory_entry(entry)
        if sub_dirs:
            kwargs["directories"] = sub_dirs

    return AppSettings(**kwargs)


def adapt_legacy_settings(
    *,
    raw: Mapping[str, Any],
    resolve_doc_variants_fn: Any,
) -> DesignSystemSettings:
    """Adapt a legacy flat ``DJ_DESIGN_SYSTEM`` dictionary into ``DesignSystemSettings``."""
    raw_bg_base = (
        raw["GALLERY_CANVAS_BACKGROUNDS"]
        if "GALLERY_CANVAS_BACKGROUNDS" in raw
        else DDS_DEFAULT_CANVAS_BACKGROUNDS
    )
    merged_bgs: dict[str, Any] = dict(raw_bg_base or {})
    extra_bgs = raw.get("GALLERY_CANVAS_EXTRA_BACKGROUNDS")
    if isinstance(extra_bgs, Mapping):
        merged_bgs.update(extra_bgs)

    canvas = CanvasSettings(
        backgrounds=merged_bgs,
        default_background=raw.get("GALLERY_CANVAS_DEFAULT_BACKGROUND", "light-grey"),
        html_attrs=raw.get("GALLERY_CANVAS_HTML_ATTRS") or {},
    )

    if "GALLERY_DOC_VARIANTS" in raw:
        resolved_variants = resolve_doc_variants_fn(
            raw_setting=raw["GALLERY_DOC_VARIANTS"]
        )
        doc_variants: Mapping[str, DocVariantConfig] = {
            dv.key: dv for dv in resolved_variants
        }
    else:
        doc_variants = DDS_DEFAULT_DOC_VARIANTS

    raw_ui_themes = (
        raw["GALLERY_UI_THEMES"]
        if "GALLERY_UI_THEMES" in raw
        else DDS_DEFAULT_UI_THEMES
    )
    if raw_ui_themes is None:
        raw_ui_themes = {}

    raw_include_apps = raw.get("GALLERY_INCLUDE_APPS", None)
    raw_exclude_apps = raw.get("GALLERY_EXCLUDE_APPS", ())
    if raw_exclude_apps is None:
        raw_exclude_apps = ()

    gallery = GallerySettings(
        enabled=bool(raw.get("ENABLE_GALLERY", True)),
        is_public=bool(raw.get("GALLERY_IS_PUBLIC", True)),
        nav_order=_adapt_legacy_nav_order(
            raw.get("GALLERY_NAV_ORDER", DDS_DEFAULT_NAV_ORDER)
        ),
        codehilite_style=raw.get("GALLERY_CODEHILITE_STYLE", "monokai"),
        ui_themes=raw_ui_themes,
        default_ui_theme=raw.get("GALLERY_DEFAULT_UI_THEME", "desert"),
        include_apps=raw_include_apps,
        exclude_apps=raw_exclude_apps,
        extra_css=raw.get("GALLERY_EXTRA_CSS") or (),
        doc_variants=doc_variants,
    )

    raw_themes = (
        raw["GALLERY_THEMES"] if "GALLERY_THEMES" in raw else DDS_DEFAULT_THEMES
    )
    if raw_themes is None:
        raw_themes = {}

    app_themes = raw.get("APP_THEMES") or {}
    app_css = raw.get("APP_CSS") or {}
    app_js = raw.get("APP_JS") or {}
    app_css_bundles = raw.get("APP_CSS_BUNDLES") or {}
    app_js_bundles = raw.get("APP_JS_BUNDLES") or {}
    app_canvas_html_attrs = raw.get("APP_CANVAS_HTML_ATTRS") or {}
    component_directories = raw.get("COMPONENT_DIRECTORIES") or {}
    component_namespaces = raw.get("COMPONENT_NAMESPACES") or {}

    all_app_labels: set[str] = set()
    for mapping in (
        app_themes,
        app_css,
        app_js,
        app_css_bundles,
        app_js_bundles,
        app_canvas_html_attrs,
        component_directories,
        component_namespaces,
    ):
        if isinstance(mapping, Mapping):
            all_app_labels.update(k for k in mapping if isinstance(k, str) and k)

    adapted_apps = {
        label: _adapt_legacy_app_settings(
            app_label=label,
            app_themes=app_themes,
            app_css=app_css,
            app_js=app_js,
            app_css_bundles=app_css_bundles,
            app_js_bundles=app_js_bundles,
            app_canvas_html_attrs=app_canvas_html_attrs,
            component_directories=component_directories,
            component_namespaces=component_namespaces,
        )
        for label in sorted(all_app_labels)
    }

    return DesignSystemSettings(
        name=raw.get("DESIGN_SYSTEM_NAME", "Django Design System"),
        css=raw.get("GLOBAL_CSS") or (),
        js=raw.get("GLOBAL_JS") or (),
        css_bundles=raw.get("GLOBAL_CSS_BUNDLES") or (),
        js_bundles=raw.get("GLOBAL_JS_BUNDLES") or (),
        themes=raw_themes,
        default_theme=raw.get("GALLERY_DEFAULT_THEME", "default"),
        gallery=gallery,
        canvas=canvas,
        apps=adapted_apps,
    )
