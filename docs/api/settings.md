# Settings Reference

All configuration for Django Design System is defined in your Django `settings.py` file within the `DJ_DESIGN_SYSTEM` dictionary.

```python
DJ_DESIGN_SYSTEM = {
    "DESIGN_SYSTEM_NAME": "Django Design System",
    "ENABLE_GALLERY": True,
    # ... other settings
}
```

Below is a comprehensive list of all available settings and their default values.

## General Settings

### `DESIGN_SYSTEM_NAME`
**Type:** `str`  
**Default:** `"Django Design System"`  
The name of your design system, displayed in the gallery's navigation bar and page titles.

### `ENABLE_GALLERY`
**Type:** `bool`  
**Default:** `True`  
Whether the gallery UI is enabled. If `False`, the gallery views will return 404 Not Found.

### `GALLERY_IS_PUBLIC`
**Type:** `bool`  
**Default:** `True`  
If `True`, the gallery is accessible to anyone. If `False`, only logged-in staff users (`is_staff=True`) can view it.

### `GALLERY_INCLUDE_APPS`
**Type:** `list[str] | None`  
**Default:** `None`  
An optional allowlist of Django `app_label` strings to include in the gallery. When set, only components from these apps are displayed in navigation, search, and folder listings. Set to `["dj_design_system"]` to inspect the built-in `dds` component library in isolation (see [`example_project/settings_dds_gallery.py`](https://github.com/fukalite/dj-design-system/blob/main/example_project/settings_dds_gallery.py)).

### `GALLERY_EXCLUDE_APPS`
**Type:** `list[str]`  
**Default:** `[]`  
A list of Django `app_label` strings to exclude from gallery navigation, search, and folder listings when `GALLERY_INCLUDE_APPS` is `None`. Built-in framework components (`dj_design_system`) are excluded by default from consumer galleries.

> [!TIP]
> **Avoiding App Visibility Settings Conflicts**
> - **Mutual Exclusivity:** Prefer using either `GALLERY_INCLUDE_APPS` (allowlist) or `GALLERY_EXCLUDE_APPS` (denylist), never both simultaneously. When `GALLERY_INCLUDE_APPS` is configured, `GALLERY_EXCLUDE_APPS` is ignored.
> - **System Checks:** Run `python manage.py check` to catch configuration conflicts before deployment:
>   - `dj_design_system.E003` (Error): Raised if an app appears in both `GALLERY_INCLUDE_APPS` and `GALLERY_EXCLUDE_APPS`.
>   - `dj_design_system.W001` (Warning): Raised when both settings are specified, indicating that `GALLERY_EXCLUDE_APPS` is redundant.
>   - `dj_design_system.W002` (Warning): Raised if a configured app label is not present in `INSTALLED_APPS`.


### `GALLERY_NAV_ORDER`
**Type:** `list[NodeType] | str`  
**Default:** `[NodeType.FOLDER, NodeType.COMPONENT, NodeType.DOCUMENT]`  
Controls the sorting order of the gallery sidebar navigation. Can specify the order in which folders, components, and documents appear.

## Global Assets

### `GLOBAL_CSS`
**Type:** `list[str]`  
**Default:** `[]`  
A list of global CSS static file paths or external URLs to include in the gallery canvas and when using `{% global_stylesheets %}`. See [External asset URLs](#external-asset-urls).

### `GLOBAL_JS`
**Type:** `list[str]`  
**Default:** `[]`  
A list of global JavaScript static file paths or external URLs to include in the gallery canvas and when using `{% global_scripts %}`. See [External asset URLs](#external-asset-urls).

### `GALLERY_EXTRA_CSS`
**Type:** `list[str]`  
**Default:** `[]`  
A list of CSS static file paths or external URLs injected into the `<head>` of the gallery UI chrome (via `{% gallery_extra_stylesheets %}`). These stylesheets are rendered after all built-in and component stylesheets, making it the recommended mechanism for overriding `:root` `--dds-*` design tokens (colours, fonts, typography, surface backgrounds) without modifying gallery templates. See [External asset URLs](#external-asset-urls).

### `GLOBAL_CSS_BUNDLES`
**Type:** `list[tuple[str, ...]]`  
**Default:** `[]`  
A list of Webpack CSS bundles to load globally. Ignored if `django-webpack-loader` is not installed. Each entry is a tuple passed to `get_files`, e.g., `("main",)`.

### `GLOBAL_JS_BUNDLES`
**Type:** `list[tuple[str, ...]]`  
**Default:** `[]`  
A list of Webpack JavaScript bundles to load globally.

### External asset URLs
`GLOBAL_CSS`, `GLOBAL_JS`, `GALLERY_EXTRA_CSS`, `APP_CSS`, `APP_JS`, a theme's `css` and `js`, and component `Media` entries accept external URLs as well as static file paths. Entries starting with `http://`, `https://` or `//` (case-insensitive) are used as-is; anything else is resolved with Django's `static()`.

```python
"GLOBAL_CSS": [
    "https://fonts.googleapis.com/css2?family=Inter&display=swap",
    "myapp/base.css",
],
```

The [REST API](../rest-api.md) returns external URLs unchanged, except that protocol-relative (`//`) URLs take the request's scheme.

## Canvas Backgrounds

### `GALLERY_CANVAS_DEFAULT_BACKGROUND`
**Type:** `str`  
**Default:** `"light-grey"`  
The slug of the default background used for the component preview canvas.

### `GALLERY_CANVAS_BACKGROUNDS`
**Type:** `dict[str, dict]`  
**Default:** Built-in backgrounds (White, Light Grey, Dark Grey, Black, Checkerboard)  
A dictionary completely overriding the available canvas backgrounds. Each value must be a dictionary with `label` and `color` keys.

### `GALLERY_CANVAS_EXTRA_BACKGROUNDS`
**Type:** `dict[str, dict]`  
**Default:** `{}`  
A dictionary of backgrounds merged into `GALLERY_CANVAS_BACKGROUNDS`. Useful for adding custom backgrounds without removing the built-ins.

### `GALLERY_CANVAS_HTML_ATTRS`
**Type:** `dict`  
**Default:** `{}`  
Extra HTML attributes applied to the `<html>` and `<body>` tags of the canvas iframe globally. Example: `{"html": {"class": "govuk-template"}, "body": {"class": "govuk-template__body"}}`.

## Theming

### `GALLERY_THEMES`
**Type:** `dict[str, dict]`  
**Default:** `{"default": {"label": "Default", "html_attrs": {}, "css": [], "js": [], "css_bundles": [], "js_bundles": []}}`  
A dictionary of available themes. See the [Themes](../themes.md) documentation for more details. A theme's `css` and `js` lists accept [external URLs](#external-asset-urls).

Each theme dictionary supports:

- **`label`** (`str`): Display label rendered in the gallery toolbar's theme dropdown.
- **`canvas_background`** (`str | dict | None`): Dedicated background colour for the preview iframe when this theme is active. Can be a built-in slug (`"white"`, `"light-grey"`, `"dark-grey"`, `"black"`, `"checkerboard"`) or a custom dictionary (e.g. `{"label": "Midnight", "color": "#1a1a2e"}`).
- **`html_attrs`** (`dict`): HTML attributes injected into the `<html>` and `<body>` tags of the canvas iframe. Example: `{"html": {"class": "theme-light"}, "body": {"class": "brand-body"}}`.
- **`css`** (`list[str]`): Static CSS file paths or external URLs loaded when the theme is active.
- **`js`** (`list[str]`): Static JS file paths or external URLs loaded when the theme is active.
- **`css_bundles`** (`list[tuple[str, ...]]`): Webpack CSS bundle specifications.
- **`js_bundles`** (`list[tuple[str, ...]]`): Webpack JS bundle specifications.
- **`dark_mode`** (`dict | None`): Explicit dark mode configuration for the theme. When defined, the theme's `supports_dark_mode` property evaluates to `True`, enabling the consumer color scheme toggle button in the gallery topbar. Accepts:
  - `canvas_background` (`str | dict | None`): Background colour applied to the canvas when dark mode is active.
  - `html_attrs` (`dict`): Attributes merged into the canvas `<html>` and `<body>` tags when dark mode is active, overriding matching base keys.
  - `css` (`list[str]`): Additional stylesheets loaded when dark mode is active.
  - `js` (`list[str]`): Additional scripts loaded when dark mode is active.
  - `css_bundles` (`list[tuple[str, ...]]`): Additional Webpack CSS bundles loaded in dark mode.
  - `js_bundles` (`list[tuple[str, ...]]`): Additional Webpack JS bundles loaded in dark mode.

> [!NOTE]
> If `dark_mode` is omitted, the topbar color scheme toggle button is automatically disabled with the tooltip `"Consumer theme does not support dark mode"`. Previews render strictly in light mode (`ColorScheme.LIGHT`), guarding against host operating system dark mode settings unintentionally affecting light-only components.

Example:
```python
DJ_DESIGN_SYSTEM = {
    "GALLERY_THEMES": {
        "dds": {
            "label": "Django Design System",
            "canvas_background": "white",
            "html_attrs": {"html": {"class": "gallery-theme-light"}},
            "css": ["example_project/theme-dds-consumer.css"],
            "dark_mode": {
                "canvas_background": "dark-grey",
                "html_attrs": {"html": {"class": "gallery-theme-dark"}},
            },
        },
        "classic": {
            "label": "Classic (Light Only)",
            "canvas_background": "light-grey",
            "css": ["css/classic.css"],
        },
    },
    "GALLERY_DEFAULT_THEME": "dds",
}
```

### `GALLERY_DEFAULT_THEME`
**Type:** `str`  
**Default:** `"default"`  
The slug of the default theme selected when loading the gallery.

### `GALLERY_UI_THEMES`
**Type:** `dict[str, dict]`  
**Default:**
```python
{
    "desert": {
        "label": "Desert",
        "dark_mode": {},
    },
    "classic": {
        "label": "Classic",
    },
}
```
A dictionary of available gallery UI chrome themes governing the sidebar, topbar shell, documentation panes, and control widgets. See [Gallery UI Themes](../themes.md#configuring-gallery-ui-themes-gallery_ui_themes).

Each UI theme dictionary supports:

- **`label`** (`str`): Display label rendered in the sidebar footer UI theme dropdown.
- **`html_attrs`** (`dict`): Custom attributes injected into the gallery document.
- **`css`** (`list[str]`): Static CSS file paths or external URLs loaded for the gallery shell via `{% gallery_ui_theme_stylesheets %}`.
- **`js`** (`list[str]`): Static JS file paths or external URLs loaded for the gallery shell via `{% gallery_ui_theme_scripts %}`.
- **`css_bundles`** (`list[tuple[str, ...]]`): Optional Webpack CSS bundles for the gallery shell.
- **`js_bundles`** (`list[tuple[str, ...]]`): Optional Webpack JS bundles for the gallery shell.
- **`dark_mode`** (`dict | None`): Explicit dark mode configuration for the UI chrome theme. When omitted or `None`, dark mode is completely suppressed: the sidebar theme toggle is disabled with the tooltip `"<Theme> theme does not support dark mode"`, and all tokens lock to light mode (`color-scheme: light`). When defined, accepts `css`, `js`, `css_bundles`, `js_bundles`, and `html_attrs`.

### `GALLERY_DEFAULT_UI_THEME`
**Type:** `str`  
**Default:** `"desert"`  
The slug of the default gallery UI chrome theme.

### `GALLERY_CODEHILITE_STYLE`
**Type:** `str`  
**Default:** `"monokai"`  
Pygments style used for syntax highlighting in markdown fenced code blocks and canvas code previews. Set to `""` to disable highlighting.

## App-Specific Configuration

### `APP_THEMES`
**Type:** `dict[str, list[str]]`  
**Default:** `{}`  
Restrict the available themes for components in specific apps. Keys are app labels, values are lists of theme slugs.

### `APP_CSS`
**Type:** `dict[str, list[str] | str]`  
**Default:** `{}`  
App-specific CSS static file paths or [external URLs](#external-asset-urls) loaded when rendering components from that app.

### `APP_CSS_BUNDLES`
**Type:** `dict[str, list[tuple[str, ...]]]`  
**Default:** `{}`  
App-specific Webpack CSS bundles loaded when rendering components from that app.

### `APP_JS`
**Type:** `dict[str, list[str] | str]`  
**Default:** `{}`  
App-specific JavaScript static file paths or [external URLs](#external-asset-urls) loaded when rendering components from that app.

### `APP_JS_BUNDLES`
**Type:** `dict[str, list[tuple[str, ...]]]`  
**Default:** `{}`  
App-specific Webpack JavaScript bundles loaded when rendering components from that app.

### `APP_CANVAS_HTML_ATTRS`
**Type:** `dict[str, dict]`  
**Default:** `{}`  
App-specific HTML attributes applied to the `<html>` and `<body>` tags of the canvas iframe when rendering components from that app.

### `COMPONENT_DIRECTORIES`
**Type:** `dict[str, dict]`  
**Default:** `{}`  
Configure folder-based namespacing and navigation structure for your components. This replaces the deprecated `COMPONENT_NAMESPACES` setting. 
Keys are app labels, values are dictionaries mapping dotted directory paths to alias strings or configuration dicts. 

Example:
```python
from dj_design_system.types import FlattenStrategy

DJ_DESIGN_SYSTEM = {
    "COMPONENT_DIRECTORIES": {
        "myapp": {
            # Top-level components map to 'ui' prefix
            "": "ui",
            # button directory maps to 'btn' prefix (preserves subfolders)
            "button": "btn",
            # Flattens subfolders (e.g. cards__hero instead of cards__layouts__hero)
            "card": {
                "prefix": "cards",
                "flatten": FlattenStrategy.ALL,
                "label": "Custom Cards Label",
            },
            # Extract this folder to the root of the navigation gallery
            "promoted_features": {"promote_to_app": True, "label": "Promoted Features"},
        }
    }
}
```
Available configuration keys for a directory:
- `prefix` (str): The namespace prefix to use for components in this directory.
- `flatten` (FlattenStrategy | str): How to handle nested subfolders. Options are `FlattenStrategy.NONE` (default), `FlattenStrategy.ALL` (discard subfolders), or `FlattenStrategy.TREE` (flatten the subfolders recursively but prefix them uniquely). Can also be passed as strings: `"none"`, `"all"`, `"tree"`.
- `label` (str): Overrides the default human-readable label in the gallery navigation sidebar.
- `promote_to_app` (bool): Extracts this directory and displays it as a top-level App in the gallery sidebar, moving it out of its parent app's hierarchy.

### `COMPONENT_NAMESPACES` (Deprecated)
> [!WARNING]
> This setting is deprecated. Please migrate to `COMPONENT_DIRECTORIES`.
