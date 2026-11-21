"""Typed configuration resolution service, 4-tier merging, and caching."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from django.apps import apps
from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured

from dj_design_system.config import (
    DDS_DEFAULT_DOC_VARIANTS,
    DDS_DEFAULT_NAV_ORDER,
    UNSET,
    AppSettings,
    CanvasBackground,
    CanvasSettings,
    DesignSystemSettings,
    DirectorySettings,
    GallerySettings,
    _UnsetType,
)
from dj_design_system.constants import BUILTIN_APP_LABEL, BUILTIN_PREFIX
from dj_design_system.types import (
    DarkModeConfig,
    DocVariantConfig,
    DocVariantStrategy,
    FlattenStrategy,
    FrozenMapping,
    NavOrderSpec,
    Theme,
    WebpackBundleSpec,
)


_DEFAULT_CONFIG: DesignSystemSettings = DesignSystemSettings()
_APP_SETTINGS_CACHE: (
    tuple[DesignSystemSettings, dict[str, ResolvedAppSettings]] | None
) = None


@dataclass(frozen=True)
class ResolvedDirectorySettings:
    """Resolved subfolder configuration with no sentinel values."""

    prefix: str | None = None
    flatten: FlattenStrategy | None = None
    label: str | None = None
    promote_to_app: bool = False
    order: int | None = None
    nav_order: NavOrderSpec | None = None


@dataclass(frozen=True)
class ResolvedAppSettings:
    """Resolved per-app configuration across built-in, project, app, and override tiers."""

    app_label: str
    label: str | None = None
    order: int | None = None
    nav_order: NavOrderSpec = DDS_DEFAULT_NAV_ORDER
    prefix: str | None = None
    flatten: FlattenStrategy = FlattenStrategy.NONE
    short_names: bool = True
    themes: tuple[str, ...] | None = None
    css: tuple[str, ...] = ()
    js: tuple[str, ...] = ()
    css_bundles: tuple[WebpackBundleSpec, ...] = ()
    js_bundles: tuple[WebpackBundleSpec, ...] = ()
    canvas_html_attrs: FrozenMapping[str, FrozenMapping[str, str]] = field(
        default_factory=FrozenMapping
    )
    directories: FrozenMapping[str, ResolvedDirectorySettings] = field(
        default_factory=FrozenMapping
    )


def _coerce_doc_variant_strategy(
    *,
    raw_strategy: str | DocVariantStrategy | None,
    default: DocVariantStrategy,
) -> DocVariantStrategy:
    if isinstance(raw_strategy, DocVariantStrategy):
        return raw_strategy
    if isinstance(raw_strategy, str):
        try:
            return DocVariantStrategy(raw_strategy)
        except ValueError:
            return default
    return default


def _doc_variant_to_dict(*, doc_variant: DocVariantConfig) -> dict[str, Any]:
    return {
        "key": doc_variant.key,
        "name": doc_variant.name,
        "label": doc_variant.label,
        "strategy": doc_variant.strategy,
        "show_in_docs": doc_variant.show_in_docs,
        "kwargs": dict(doc_variant.kwargs),
        "param_factory": doc_variant.param_factory,
        "slot_factory": doc_variant.slot_factory,
    }


def _parse_doc_variant_entry(
    *,
    key: str,
    raw_entry: Any,
    base_entry: Mapping[str, Any] | None = None,
) -> DocVariantConfig:
    if isinstance(raw_entry, DocVariantConfig):
        return raw_entry

    base = dict(base_entry) if base_entry else {}
    default_strategy = _coerce_doc_variant_strategy(
        raw_strategy=base.get("strategy", key),
        default=(
            DocVariantStrategy.CUSTOM
            if key not in DDS_DEFAULT_DOC_VARIANTS
            else DocVariantStrategy.MINIMAL
        ),
    )
    default_name = str(base.get("name", key))
    default_label = str(base.get("label", key.replace("_", " ").capitalize()))

    if raw_entry is None or raw_entry is False:
        return DocVariantConfig(
            key=key,
            name=default_name,
            label=default_label,
            strategy=default_strategy,
            show_in_docs=False,
            kwargs=dict(base.get("kwargs", {})),
            param_factory=base.get("param_factory"),
            slot_factory=base.get("slot_factory"),
        )

    if raw_entry is True:
        return DocVariantConfig(
            key=key,
            name=default_name,
            label=default_label,
            strategy=default_strategy,
            show_in_docs=True,
            kwargs=dict(base.get("kwargs", {})),
            param_factory=base.get("param_factory"),
            slot_factory=base.get("slot_factory"),
        )

    if isinstance(raw_entry, Mapping):
        if len(raw_entry) == 0:
            return DocVariantConfig(
                key=key,
                name=default_name,
                label=default_label,
                strategy=default_strategy,
                show_in_docs=False,
                kwargs=dict(base.get("kwargs", {})),
                param_factory=base.get("param_factory"),
                slot_factory=base.get("slot_factory"),
            )

        merged = {**base, **raw_entry}
        strategy = _coerce_doc_variant_strategy(
            raw_strategy=merged.get("strategy"),
            default=default_strategy,
        )
        name = str(merged.get("name", default_name))
        label = str(
            merged.get(
                "label",
                base.get("label", name.replace("_", " ").capitalize()),
            )
        )
        show_in_docs = bool(merged.get("show_in_docs", True))
        kwargs = dict(merged.get("kwargs", {}))
        return DocVariantConfig(
            key=key,
            name=name,
            label=label,
            strategy=strategy,
            show_in_docs=show_in_docs,
            kwargs=kwargs,
            param_factory=merged.get("param_factory"),
            slot_factory=merged.get("slot_factory"),
        )

    return DocVariantConfig(
        key=key,
        name=default_name,
        label=default_label,
        strategy=default_strategy,
        show_in_docs=bool(base.get("show_in_docs", True)),
        kwargs=dict(base.get("kwargs", {})),
        param_factory=base.get("param_factory"),
        slot_factory=base.get("slot_factory"),
    )


def resolve_doc_variants(
    *,
    raw_setting: Mapping[str, Any] | Sequence[Any] | None = None,
    base_variants: Sequence[DocVariantConfig] | None = None,
) -> list[DocVariantConfig]:
    """Resolve documentation variants by applying *raw_setting* over *base_variants*."""
    base_list = (
        list(DDS_DEFAULT_DOC_VARIANTS.values())
        if base_variants is None
        else list(base_variants)
    )

    if raw_setting is None:
        return base_list

    if isinstance(raw_setting, Mapping):
        results: list[DocVariantConfig] = []
        seen_raw_keys: set[str] = set()
        for base_dv in base_list:
            matched_raw_key: str | None = None
            if base_dv.key in raw_setting:
                matched_raw_key = base_dv.key
            elif base_dv.name in raw_setting:
                matched_raw_key = base_dv.name

            if matched_raw_key is not None:
                seen_raw_keys.add(matched_raw_key)
                results.append(
                    _parse_doc_variant_entry(
                        key=base_dv.key,
                        raw_entry=raw_setting[matched_raw_key],
                        base_entry=_doc_variant_to_dict(doc_variant=base_dv),
                    )
                )
            else:
                results.append(base_dv)

        for key, raw_entry in raw_setting.items():
            if key in seen_raw_keys:
                continue
            results.append(
                _parse_doc_variant_entry(
                    key=key,
                    raw_entry=raw_entry,
                    base_entry=None,
                )
            )
        return results

    if isinstance(raw_setting, Sequence) and not isinstance(raw_setting, (str, bytes)):
        results = []
        matched_base_keys: set[str] = set()
        base_by_key = {dv.key: dv for dv in base_list}
        base_by_name = {dv.name: dv for dv in base_list}

        for item in raw_setting:
            if isinstance(item, DocVariantConfig):
                matched_dv = base_by_key.get(item.key) or base_by_name.get(item.name)
                if matched_dv is not None:
                    matched_base_keys.add(matched_dv.key)
                results.append(item)
            elif isinstance(item, str):
                matched_dv = base_by_key.get(item) or base_by_name.get(item)
                if matched_dv is not None:
                    matched_base_keys.add(matched_dv.key)
                    results.append(
                        _parse_doc_variant_entry(
                            key=matched_dv.key,
                            raw_entry=True,
                            base_entry=_doc_variant_to_dict(doc_variant=matched_dv),
                        )
                    )
                else:
                    results.append(
                        DocVariantConfig(
                            key=item,
                            name=item,
                            label=item.replace("_", " ").capitalize(),
                            strategy=DocVariantStrategy.CUSTOM,
                            show_in_docs=True,
                        )
                    )
            elif isinstance(item, Mapping):
                raw_key = str(item.get("key") or item.get("name") or "custom")
                matched_dv = base_by_key.get(raw_key) or base_by_name.get(raw_key)
                if matched_dv is not None:
                    matched_base_keys.add(matched_dv.key)
                    results.append(
                        _parse_doc_variant_entry(
                            key=matched_dv.key,
                            raw_entry=item,
                            base_entry=_doc_variant_to_dict(doc_variant=matched_dv),
                        )
                    )
                else:
                    results.append(
                        _parse_doc_variant_entry(
                            key=raw_key,
                            raw_entry=item,
                            base_entry=None,
                        )
                    )

        for base_dv in base_list:
            if base_dv.key not in matched_base_keys:
                results.append(
                    _parse_doc_variant_entry(
                        key=base_dv.key,
                        raw_entry=False,
                        base_entry=_doc_variant_to_dict(doc_variant=base_dv),
                    )
                )
        return results

    return base_list


def get_config() -> DesignSystemSettings:
    """Return the active ``DesignSystemSettings`` for the current Django settings."""
    raw = getattr(django_settings, "DJ_DESIGN_SYSTEM", None)
    if raw is None:
        return _DEFAULT_CONFIG

    if isinstance(raw, DesignSystemSettings):
        return raw

    raise ImproperlyConfigured(
        f"settings.DJ_DESIGN_SYSTEM must be a DesignSystemSettings instance or None; "
        f"got {type(raw).__name__}. Migrate legacy flat dict settings using "
        "dj-design-system v0.10.x before upgrading to v1.0.0."
    )


def get_gallery_settings() -> GallerySettings:
    """Return the active ``GallerySettings``."""
    return get_config().gallery


def get_canvas_settings() -> CanvasSettings:
    """Return the active ``CanvasSettings``."""
    return get_config().canvas


def _get_app_config_defaults(*, app_label: str) -> AppSettings | None:
    if not apps.apps_ready:
        return None
    try:
        app_config = apps.get_app_config(app_label)
    except LookupError:
        return None
    declared = getattr(app_config, "design_system", None)
    if isinstance(declared, AppSettings):
        return declared
    return None


def _resolve_scalar(
    *,
    project_val: Any,
    app_val: Any,
    default: Any,
) -> Any:
    if project_val is not UNSET:
        return project_val
    if app_val is not UNSET:
        return app_val
    return default


def _as_str_tuple(value: str | Sequence[str] | _UnsetType) -> tuple[str, ...]:
    if value is UNSET:
        return ()
    if isinstance(value, str):
        return (value,)
    return tuple(value)


def _merge_asset_tuples(
    *,
    app_base: str | Sequence[str] | _UnsetType,
    app_extra: str | Sequence[str] | _UnsetType,
    project_base: str | Sequence[str] | _UnsetType,
    project_extra: str | Sequence[str] | _UnsetType,
) -> tuple[str, ...]:
    if project_base is not UNSET:
        base = _as_str_tuple(project_base)
    else:
        base = _as_str_tuple(app_base) + _as_str_tuple(app_extra)

    extra = _as_str_tuple(project_extra)
    return tuple(dict.fromkeys(base + extra))


def _merge_canvas_html_attrs(
    *,
    app_attrs: Mapping[str, Any] | None | _UnsetType,
    project_attrs: Mapping[str, Any] | None | _UnsetType,
) -> FrozenMapping[str, FrozenMapping[str, str]]:
    merged: dict[str, dict[str, str]] = {}

    if app_attrs is not UNSET and app_attrs is not None:
        for section, pairs in app_attrs.items():
            cleaned = {k: str(v) for k, v in pairs.items() if v is not None}
            if cleaned:
                merged[section] = cleaned

    if project_attrs is None:
        return FrozenMapping()

    if project_attrs is not UNSET:
        for section, pairs in project_attrs.items():
            section_map = dict(merged.get(section, {}))
            for key, value in pairs.items():
                if value is None:
                    section_map.pop(key, None)
                else:
                    section_map[key] = str(value)
            if section_map:
                merged[section] = section_map
            else:
                merged.pop(section, None)

    return FrozenMapping(
        {section: FrozenMapping(pairs) for section, pairs in merged.items()}
    )


def _as_nav_order(value: Sequence[Any] | str | None) -> NavOrderSpec | None:
    if value is None:
        return None
    if value == "alphabetical":
        return "alphabetical"
    if isinstance(value, str):
        return (value,)
    return tuple(value)


def _merge_directories(
    *,
    app_dirs: Mapping[str, DirectorySettings | None] | None | _UnsetType,
    project_dirs: Mapping[str, DirectorySettings | None] | None | _UnsetType,
) -> FrozenMapping[str, ResolvedDirectorySettings]:
    merged: dict[str, DirectorySettings] = {}

    if app_dirs is not UNSET and app_dirs is not None:
        for path, entry in app_dirs.items():
            if entry is not None:
                merged[path] = entry

    if project_dirs is None:
        return FrozenMapping()

    if project_dirs is not UNSET:
        for path, entry in project_dirs.items():
            if entry is None:
                merged.pop(path, None)
            else:
                merged[path] = entry

    return FrozenMapping(
        {
            path: ResolvedDirectorySettings(
                prefix=entry.prefix,
                flatten=entry.flatten,
                label=entry.label,
                promote_to_app=entry.promote_to_app,
                order=entry.order,
                nav_order=_as_nav_order(entry.nav_order),
            )
            for path, entry in merged.items()
        }
    )


def _resolve_app_settings_uncached(
    *,
    app_label: str,
    config: DesignSystemSettings,
) -> ResolvedAppSettings:
    app_defaults = _get_app_config_defaults(app_label=app_label) or AppSettings()
    project_override = config.apps.get(app_label) or AppSettings()

    prefix = _resolve_scalar(
        project_val=project_override.prefix,
        app_val=app_defaults.prefix,
        default=None,
    )
    flatten = _resolve_scalar(
        project_val=project_override.flatten,
        app_val=app_defaults.flatten,
        default=FlattenStrategy.NONE,
    )
    short_names = _resolve_scalar(
        project_val=project_override.short_names,
        app_val=app_defaults.short_names,
        default=True,
    )

    if app_label == BUILTIN_APP_LABEL:
        prefix = BUILTIN_PREFIX
        flatten = FlattenStrategy.ALL
        short_names = False

    return ResolvedAppSettings(
        app_label=app_label,
        label=_resolve_scalar(
            project_val=project_override.label,
            app_val=app_defaults.label,
            default=None,
        ),
        order=_resolve_scalar(
            project_val=project_override.order,
            app_val=app_defaults.order,
            default=None,
        ),
        nav_order=_resolve_scalar(
            project_val=project_override.nav_order,
            app_val=app_defaults.nav_order,
            default=config.gallery.nav_order,
        ),
        prefix=prefix,
        flatten=flatten,
        short_names=short_names,
        themes=_resolve_scalar(
            project_val=project_override.themes,
            app_val=app_defaults.themes,
            default=None,
        ),
        css=_merge_asset_tuples(
            app_base=app_defaults.css,
            app_extra=app_defaults.extra_css,
            project_base=project_override.css,
            project_extra=project_override.extra_css,
        ),
        js=_merge_asset_tuples(
            app_base=app_defaults.js,
            app_extra=app_defaults.extra_js,
            project_base=project_override.js,
            project_extra=project_override.extra_js,
        ),
        css_bundles=_resolve_scalar(
            project_val=project_override.css_bundles,
            app_val=app_defaults.css_bundles,
            default=(),
        ),
        js_bundles=_resolve_scalar(
            project_val=project_override.js_bundles,
            app_val=app_defaults.js_bundles,
            default=(),
        ),
        canvas_html_attrs=_merge_canvas_html_attrs(
            app_attrs=app_defaults.canvas_html_attrs,
            project_attrs=project_override.canvas_html_attrs,
        ),
        directories=_merge_directories(
            app_dirs=app_defaults.directories,
            project_dirs=project_override.directories,
        ),
    )


def get_app_settings(*, app_label: str) -> ResolvedAppSettings:
    """Resolve effective settings for *app_label* across all tiers."""
    global _APP_SETTINGS_CACHE

    config = get_config()
    if apps.apps_ready:
        if _APP_SETTINGS_CACHE is not None and _APP_SETTINGS_CACHE[0] is config:
            cached = _APP_SETTINGS_CACHE[1].get(app_label)
            if cached is not None:
                return cached
        else:
            _APP_SETTINGS_CACHE = (config, {})

    resolved = _resolve_app_settings_uncached(app_label=app_label, config=config)

    if apps.apps_ready and _APP_SETTINGS_CACHE is not None:
        _APP_SETTINGS_CACHE[1][app_label] = resolved
    return resolved


def get_all_app_settings() -> FrozenMapping[str, ResolvedAppSettings]:
    """Resolve effective settings for every installed app and every app in ``DJ_DESIGN_SYSTEM.apps``."""
    config = get_config()
    labels: list[str] = []
    seen: set[str] = set()

    if apps.apps_ready:
        for app_config in apps.get_app_configs():
            if app_config.label not in seen:
                seen.add(app_config.label)
                labels.append(app_config.label)

    for label in config.apps:
        if label not in seen:
            seen.add(label)
            labels.append(label)

    return FrozenMapping({label: get_app_settings(app_label=label) for label in labels})


def get_themes() -> FrozenMapping[str, Theme]:
    """Return configured component themes keyed by slug."""
    themes = get_config().themes
    return themes if isinstance(themes, FrozenMapping) else FrozenMapping(themes)


def get_theme(*, identifier: str) -> Theme | None:
    """Return the component theme matching *identifier*, or ``None``."""
    return get_themes().get(identifier)


def get_default_theme() -> Theme:
    """Return the default component theme, falling back safely if missing."""
    config = get_config()
    themes = get_themes()
    if config.default_theme in themes:
        return themes[config.default_theme]
    if themes:
        return next(iter(themes.values()))
    return Theme(value="default", label="Default")


def get_gallery_ui_themes() -> FrozenMapping[str, Theme]:
    """Return configured gallery UI chrome themes keyed by slug."""
    themes = get_gallery_settings().ui_themes
    return themes if isinstance(themes, FrozenMapping) else FrozenMapping(themes)


def get_gallery_ui_theme(*, identifier: str) -> Theme | None:
    """Return the gallery UI theme matching *identifier*, or ``None``."""
    return get_gallery_ui_themes().get(identifier)


def get_default_gallery_ui_theme() -> Theme:
    """Return the default gallery UI theme, falling back safely if missing."""
    gallery = get_gallery_settings()
    themes = get_gallery_ui_themes()
    if gallery.default_ui_theme in themes:
        return themes[gallery.default_ui_theme]
    if themes:
        return next(iter(themes.values()))
    return Theme(value="desert", label="Desert", dark_mode=DarkModeConfig())


def get_backgrounds() -> FrozenMapping[str, CanvasBackground]:
    """Return configured canvas backgrounds keyed by slug."""
    backgrounds = get_canvas_settings().backgrounds
    return (
        backgrounds
        if isinstance(backgrounds, FrozenMapping)
        else FrozenMapping(backgrounds)
    )


def get_default_background() -> CanvasBackground:
    """Return the default canvas background, falling back safely if missing."""
    canvas = get_canvas_settings()
    backgrounds = get_backgrounds()
    if canvas.default_background in backgrounds:
        return backgrounds[canvas.default_background]
    if backgrounds:
        return next(iter(backgrounds.values()))
    return CanvasBackground(label="Light Grey", color="#f0f0f0")


def get_default_background_slug() -> str:
    """Return the slug of the resolved default canvas background."""
    canvas = get_canvas_settings()
    backgrounds = get_backgrounds()
    if canvas.default_background in backgrounds:
        return canvas.default_background
    if backgrounds:
        return next(iter(backgrounds.keys()))
    return "light-grey"


def get_doc_variants() -> tuple[DocVariantConfig, ...]:
    """Return configured documentation variants."""
    return tuple(get_gallery_settings().doc_variants.values())


def get_doc_variant(*, key: str) -> DocVariantConfig | None:
    """Return the documentation variant matching *key*, or ``None``."""
    return get_gallery_settings().doc_variants.get(key)


def clear_config_cache() -> None:
    """Invalidate configuration caches."""
    global _APP_SETTINGS_CACHE
    _APP_SETTINGS_CACHE = None
