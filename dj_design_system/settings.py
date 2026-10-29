from collections.abc import Mapping, Sequence
from typing import Any

from django.conf import settings

from dj_design_system.services.media import coerce_path_list
from dj_design_system.types import (
    DarkModeConfig,
    DocVariantConfig,
    DocVariantStrategy,
    NodeType,
    Theme,
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


# Built-in canvas backgrounds keyed by slug.  Each entry is a dict with
# ``label`` and ``color`` (a CSS <background> value).  Projects can replace
# this entirely via ``GALLERY_CANVAS_BACKGROUNDS`` or merge extra entries
# via ``GALLERY_CANVAS_EXTRA_BACKGROUNDS``.
BUILTIN_CANVAS_BACKGROUNDS: dict[str, dict] = {
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


DEFAULTS: dict = {
    "DESIGN_SYSTEM_NAME": "Django Design System",
    "ENABLE_GALLERY": True,
    "GALLERY_IS_PUBLIC": True,
    "GALLERY_NAV_ORDER": [NodeType.FOLDER, NodeType.COMPONENT, NodeType.DOCUMENT],
    "GLOBAL_CSS": [],
    "GLOBAL_JS": [],
    # Each entry is a tuple of positional args passed to webpack_loader's
    # ``get_files(bundle_name, extension, config)``:
    #   ("main",)              → get_files("main", extension=..., config="DEFAULT")
    #   ("main", "MY_CONFIG") → get_files("main", extension=..., config="MY_CONFIG")
    # Ignored when webpack_loader is not installed.
    "GLOBAL_CSS_BUNDLES": [],
    "GLOBAL_JS_BUNDLES": [],
    "GALLERY_CANVAS_BACKGROUNDS": BUILTIN_CANVAS_BACKGROUNDS,
    "GALLERY_CANVAS_EXTRA_BACKGROUNDS": {},
    "GALLERY_CANVAS_DEFAULT_BACKGROUND": "light-grey",
    # Extra HTML attributes for the canvas iframe's <html> and <body> tags.
    # Example: {"html": {"class": "govuk-template"}, "body": {"class": "govuk-template__body"}}
    "GALLERY_CANVAS_HTML_ATTRS": {},
    # Pygments style used for syntax highlighting in markdown fenced code
    # blocks and canvas code previews. Set to "" to disable highlighting.
    "GALLERY_CODEHILITE_STYLE": "monokai",
    # Theme configuration
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
    # Gallery UI chrome theme configuration (sidebar, topbar, documentation panes)
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
    # App labels explicitly included in the gallery. When configured (a list of
    # app labels), only components from these apps appear in the gallery.
    # When None (the default), all discovered apps appear except those in
    # GALLERY_EXCLUDE_APPS and the framework's own built-in components.
    "GALLERY_INCLUDE_APPS": None,
    # App labels hidden from the gallery (navigation, search, index count,
    # node URLs and the REST API). Hidden components still work as tags.
    "GALLERY_EXCLUDE_APPS": [],
    # Additional stylesheets injected into the gallery UI chrome (to override :root tokens, custom fonts, etc.)
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

# Settings whose values are normalised to a list of strings.
_PATH_LIST_SETTINGS = {"GLOBAL_CSS", "GLOBAL_JS", "GALLERY_EXTRA_CSS"}


class DjangoDesignSystemSettings:
    DESIGN_SYSTEM_NAME: str
    ENABLE_GALLERY: bool
    GALLERY_IS_PUBLIC: bool
    GALLERY_NAV_ORDER: list[NodeType | str] | str
    GLOBAL_CSS: list[str]
    GLOBAL_JS: list[str]
    GLOBAL_CSS_BUNDLES: list[tuple[str, ...]]
    GLOBAL_JS_BUNDLES: list[tuple[str, ...]]
    GALLERY_CANVAS_DEFAULT_BACKGROUND: str
    GALLERY_CANVAS_BACKGROUNDS: dict[str, dict]
    GALLERY_CANVAS_EXTRA_BACKGROUNDS: dict[str, dict]
    GALLERY_CANVAS_HTML_ATTRS: dict
    GALLERY_CODEHILITE_STYLE: str
    GALLERY_THEMES: dict[str, dict]
    GALLERY_DEFAULT_THEME: str
    GALLERY_UI_THEMES: dict[str, dict]
    GALLERY_DEFAULT_UI_THEME: str
    GALLERY_INCLUDE_APPS: list[str] | None
    GALLERY_EXCLUDE_APPS: list[str]
    GALLERY_EXTRA_CSS: list[str]
    GALLERY_DOC_VARIANTS: Mapping[str, Any] | Sequence[Any]
    APP_THEMES: dict[str, list[str]]
    APP_CSS: dict[str, list[str] | str]
    APP_CSS_BUNDLES: dict[str, list[tuple[str, ...]]]
    APP_JS: dict[str, list[str] | str]
    APP_JS_BUNDLES: dict[str, list[tuple[str, ...]]]
    APP_CANVAS_HTML_ATTRS: dict[str, dict]
    COMPONENT_DIRECTORIES: dict[str, dict]
    COMPONENT_NAMESPACES: dict[str, dict]

    def __getattr__(self, attr: str):
        django_settings = getattr(settings, "DJ_DESIGN_SYSTEM", {})

        if attr in django_settings:
            value = django_settings[attr]
            if attr == "COMPONENT_NAMESPACES" and value:
                import warnings

                warnings.warn(
                    "COMPONENT_NAMESPACES is deprecated and will be removed in a future release. "
                    "Please migrate to COMPONENT_DIRECTORIES.",
                    DeprecationWarning,
                    stacklevel=2,
                )
        else:
            # Check if present in defaults
            if attr not in DEFAULTS:
                raise AttributeError(f"No value set for DJ_DESIGN_SYSTEM['{attr}']")
            value = DEFAULTS[attr]

        if attr in _PATH_LIST_SETTINGS:
            return coerce_path_list(value)
        return value


dds_settings = DjangoDesignSystemSettings()


def get_backgrounds() -> list[dict]:
    """Return the merged list of canvas backgrounds.

    ``GALLERY_CANVAS_EXTRA_BACKGROUNDS`` entries are merged into (and can
    override) ``GALLERY_CANVAS_BACKGROUNDS``.  Each returned dict has
    ``value``, ``label``, and ``color`` keys.
    """
    merged = {
        **dds_settings.GALLERY_CANVAS_BACKGROUNDS,
        **dds_settings.GALLERY_CANVAS_EXTRA_BACKGROUNDS,
    }
    return [{"value": key, **entry} for key, entry in merged.items()]


def get_default_background() -> dict:
    """Return the default background as a ``{"value", "label", "color"}`` dict."""
    value = dds_settings.GALLERY_CANVAS_DEFAULT_BACKGROUND
    backgrounds = get_backgrounds()
    for bg in backgrounds:
        if bg["value"] == value:
            return bg
    # Fallback to first configured background, then hard-coded light grey.
    if backgrounds:
        return backgrounds[0]
    return {"value": "light-grey", "label": "Light Grey", "color": "#f0f0f0"}


def _parse_theme_dict(key: str, theme: dict) -> Theme:
    """Parse a theme dictionary into a typed Theme instance."""
    raw_dark_mode = theme.get("dark_mode")
    dark_mode_obj: DarkModeConfig | None = None
    if isinstance(raw_dark_mode, dict):
        dark_mode_obj = DarkModeConfig(
            html_attrs=raw_dark_mode.get("html_attrs", {}),
            css=coerce_path_list(raw_dark_mode.get("css", [])),
            js=coerce_path_list(raw_dark_mode.get("js", [])),
            css_bundles=raw_dark_mode.get("css_bundles", []),
            js_bundles=raw_dark_mode.get("js_bundles", []),
            canvas_background=raw_dark_mode.get("canvas_background"),
        )
    elif isinstance(raw_dark_mode, DarkModeConfig):
        dark_mode_obj = raw_dark_mode

    return Theme(
        value=key,
        label=theme.get("label", key.capitalize()),
        html_attrs=theme.get("html_attrs", {}),
        css=coerce_path_list(theme.get("css", [])),
        js=coerce_path_list(theme.get("js", [])),
        css_bundles=theme.get("css_bundles", []),
        js_bundles=theme.get("js_bundles", []),
        canvas_background=theme.get("canvas_background"),
        dark_mode=dark_mode_obj,
    )


def get_themes() -> list[Theme]:
    """Return the list of themes.

    Each theme dict contains 'value', 'label', 'html_attrs', 'css', 'js', 'css_bundles', 'js_bundles'.
    """
    themes = dds_settings.GALLERY_THEMES
    return [_parse_theme_dict(key, theme) for key, theme in themes.items()]


def get_gallery_ui_themes() -> list[Theme]:
    """Return the list of configured gallery UI themes."""
    ui_themes = getattr(dds_settings, "GALLERY_UI_THEMES", None) or {}
    return [_parse_theme_dict(key, theme) for key, theme in ui_themes.items()]


def get_gallery_ui_theme(identifier: str) -> Theme | None:
    """Return the gallery UI theme matching the identifier, or None."""
    for theme in get_gallery_ui_themes():
        if theme.value == identifier:
            return theme
    return None


def get_default_gallery_ui_theme() -> Theme:
    """Return the default gallery UI theme."""
    val = getattr(dds_settings, "GALLERY_DEFAULT_UI_THEME", "desert")
    theme = get_gallery_ui_theme(identifier=val)
    if theme:
        return theme
    themes = get_gallery_ui_themes()
    if themes:
        return themes[0]
    return Theme(
        value="desert",
        label="Desert",
        dark_mode=DarkModeConfig(),
    )


def get_theme(identifier: str) -> Theme | None:
    """Return the theme matching the identifier, or None."""
    for theme in get_themes():
        if theme.value == identifier:
            return theme
    return None


def get_default_theme() -> Theme:
    """Return the default theme as a dict."""
    val = dds_settings.GALLERY_DEFAULT_THEME
    theme = get_theme(identifier=val)
    if theme:
        return theme
    themes = get_themes()
    if themes:
        return themes[0]
    return Theme(
        value="default",
        label="Default",
        html_attrs={},
        css=[],
        js=[],
        css_bundles=[],
        js_bundles=[],
    )


def get_app_static(app_label: str) -> tuple[list[str], list[str]]:
    """Return a tuple of (css_paths, js_paths) for the given app_label."""
    app_css = (dds_settings.APP_CSS or {}).get(app_label, [])
    app_js = (dds_settings.APP_JS or {}).get(app_label, [])
    return coerce_path_list(app_css), coerce_path_list(app_js)


def get_app_html_attrs(app_label: str) -> dict:
    """Return app-specific canvas HTML attributes."""
    return (dds_settings.APP_CANVAS_HTML_ATTRS or {}).get(app_label, {})


def _coerce_doc_variant_strategy(
    *,
    raw_strategy: str | DocVariantStrategy | None,
    default: DocVariantStrategy,
) -> DocVariantStrategy:
    """Coerce a raw strategy value into a DocVariantStrategy enum."""
    if isinstance(raw_strategy, DocVariantStrategy):
        return raw_strategy
    if isinstance(raw_strategy, str):
        try:
            return DocVariantStrategy(raw_strategy)
        except ValueError:
            return default
    return default


def _parse_doc_variant_entry(
    *,
    key: str,
    raw_entry: Any,
    base_entry: Mapping[str, Any] | None = None,
) -> DocVariantConfig:
    """Parse a single GALLERY_DOC_VARIANTS entry into a DocVariantConfig."""
    if isinstance(raw_entry, DocVariantConfig):
        return raw_entry

    base = dict(base_entry) if base_entry else {}
    default_strategy = _coerce_doc_variant_strategy(
        raw_strategy=base.get("strategy", key),
        default=(
            DocVariantStrategy.CUSTOM
            if key not in BUILTIN_DOC_VARIANTS
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


def _doc_variant_to_dict(*, doc_variant: DocVariantConfig) -> dict[str, Any]:
    """Serialize a DocVariantConfig into a dictionary for layered merging."""
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


def resolve_doc_variants(
    *,
    raw_setting: Mapping[str, Any] | Sequence[Any] | None = None,
    base_variants: Sequence[DocVariantConfig] | None = None,
) -> list[DocVariantConfig]:
    """Resolve documentation variants by applying *raw_setting* over *base_variants*."""
    if base_variants is None:
        base_list = [
            _parse_doc_variant_entry(
                key=key,
                raw_entry=base_entry,
                base_entry=base_entry,
            )
            for key, base_entry in BUILTIN_DOC_VARIANTS.items()
        ]
    else:
        base_list = list(base_variants)

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


def get_doc_variants() -> list[DocVariantConfig]:
    """Return normalized standard documentation variant configurations."""
    raw_setting = getattr(dds_settings, "GALLERY_DOC_VARIANTS", BUILTIN_DOC_VARIANTS)
    return resolve_doc_variants(raw_setting=raw_setting)


def get_doc_variant_by_key(*, key: str) -> DocVariantConfig | None:
    """Return the DocVariantConfig matching the given key, or None."""
    for doc_variant in get_doc_variants():
        if doc_variant.key == key:
            return doc_variant
    return None
