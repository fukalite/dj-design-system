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

### `GALLERY_NAV_ORDER`
**Type:** `list[NodeType] | str`  
**Default:** `[NodeType.FOLDER, NodeType.COMPONENT, NodeType.DOCUMENT]`  
Controls the sorting order of the gallery sidebar navigation. Can specify the order in which folders, components, and documents appear.

## Global Assets

### `GLOBAL_CSS`
**Type:** `list[str]`  
**Default:** `[]`  
A list of global CSS static file paths to include in the gallery canvas and when using `{% global_stylesheets %}`.

### `GLOBAL_JS`
**Type:** `list[str]`  
**Default:** `[]`  
A list of global JavaScript static file paths to include in the gallery canvas and when using `{% global_scripts %}`.

### `GLOBAL_CSS_BUNDLES`
**Type:** `list[tuple[str, ...]]`  
**Default:** `[]`  
A list of Webpack CSS bundles to load globally. Ignored if `django-webpack-loader` is not installed. Each entry is a tuple passed to `get_files`, e.g., `("main",)`.

### `GLOBAL_JS_BUNDLES`
**Type:** `list[tuple[str, ...]]`  
**Default:** `[]`  
A list of Webpack JavaScript bundles to load globally.

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
A dictionary of available themes. See the [Themes](../themes.md) documentation for more details.

Themes can also include an optional `canvas_background` setting to specify a dedicated background colour for the preview iframe when that theme is active. This is highly recommended for dark themes. You can use a built-in slug or a custom dictionary.

Example:
```python
"dark": {
    "label": "Dark Theme",
    "canvas_background": "dark-grey",  # Complements the default light-grey background
    "html_attrs": {"html": {"data-theme": "dark"}},
}
```

### `GALLERY_DEFAULT_THEME`
**Type:** `str`  
**Default:** `"default"`  
The slug of the default theme selected when loading the gallery.

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
App-specific CSS static file paths loaded when rendering components from that app.

### `APP_CSS_BUNDLES`
**Type:** `dict[str, list[tuple[str, ...]]]`  
**Default:** `{}`  
App-specific Webpack CSS bundles loaded when rendering components from that app.

### `APP_JS`
**Type:** `dict[str, list[str] | str]`  
**Default:** `{}`  
App-specific JavaScript static file paths loaded when rendering components from that app.

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
