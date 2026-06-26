from django.conf import settings

from dj_design_system.services.media import coerce_path_list
from dj_design_system.types import NodeType, Theme


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
    "APP_THEMES": {},
    "APP_CSS": {},
    "APP_CSS_BUNDLES": {},
    "APP_JS": {},
    "APP_JS_BUNDLES": {},
    "APP_CANVAS_HTML_ATTRS": {},
    "COMPONENT_NAMESPACES": {},
}

# Settings whose values are normalised to a list of strings.
_PATH_LIST_SETTINGS = {"GLOBAL_CSS", "GLOBAL_JS"}


class DjangoDesignSystemSettings:
    DESIGN_SYSTEM_NAME: str
    ENABLE_GALLERY: bool
    GALLERY_IS_PUBLIC: bool
    GALLERY_NAV_ORDER: list[NodeType] | str
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
    APP_THEMES: dict[str, list[str]]
    APP_CSS: dict[str, list[str] | str]
    APP_CSS_BUNDLES: dict[str, list[tuple[str, ...]]]
    APP_JS: dict[str, list[str] | str]
    APP_JS_BUNDLES: dict[str, list[tuple[str, ...]]]
    APP_CANVAS_HTML_ATTRS: dict[str, dict]
    COMPONENT_NAMESPACES: dict[str, dict]

    def __getattr__(self, attr: str):
        django_settings = getattr(settings, "DJ_DESIGN_SYSTEM", {})

        if attr in django_settings:
            value = django_settings[attr]
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


def get_themes() -> list[Theme]:
    """Return the list of themes.

    Each theme dict contains 'value', 'label', 'html_attrs', 'css', 'js', 'css_bundles', 'js_bundles'.
    """
    themes = dds_settings.GALLERY_THEMES
    result = []
    for key, theme in themes.items():
        theme_data = Theme(
            value=key,
            label=theme.get("label", key.capitalize()),
            html_attrs=theme.get("html_attrs", {}),
            css=coerce_path_list(theme.get("css", [])),
            js=coerce_path_list(theme.get("js", [])),
            css_bundles=theme.get("css_bundles", []),
            js_bundles=theme.get("js_bundles", []),
            canvas_background=theme.get("canvas_background"),
        )
        result.append(theme_data)
    return result


def get_theme(identifier: str) -> Theme | None:
    """Return the theme matching the identifier, or None."""
    for theme in get_themes():
        if theme.value == identifier:
            return theme
    return None


def get_default_theme() -> Theme:
    """Return the default theme as a dict."""
    val = dds_settings.GALLERY_DEFAULT_THEME
    theme = get_theme(val)
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
