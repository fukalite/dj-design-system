# Themes and App-Specific Assets

This document describes how to configure and use themes, available themes per component, and app-specific static assets within the Django Design System.

---

## Configuring Themes

Themes allow you to customize the styling and attributes of your components inside the gallery sandbox, and provide a **Theme Manager** to style the actual frontend of your project.

Define your themes in your Django `settings.py` file under `dj_design_system`:

```python
dj_design_system = {
    "GALLERY_THEMES": {
        "default": {
            "label": "Default Theme",
            "html_attrs": {
                "html": {"data-theme": "default"},
                "body": {"class": "theme-default-body"},
            },
            "css": ["css/theme-default.css"],
            "js": ["js/theme-default.js"],
            "css_bundles": [],
            "js_bundles": [],
        },
        "dark": {
            "label": "Dark Theme",
            "canvas_background": "dark-grey",  # Recommended: Use a dark background to complement your theme
            "html_attrs": {
                "html": {"data-theme": "dark"},
                "body": {"class": "theme-dark-body"},
            },
            "css": ["css/theme-dark.css"],
            "js": ["js/theme-dark.js"],
            "css_bundles": [],
            "js_bundles": [],
        },
    },
    "GALLERY_DEFAULT_THEME": "default",
}
```

### Key properties of a theme configuration:
- **`label`**: The display label in the gallery toolbar's theme dropdown.
- **`canvas_background`**: An optional background for the preview iframe when this theme is active. It can be a built-in slug (e.g. `"dark"`, `"black"`) or a custom dictionary (e.g. `{"label": "Midnight", "color": "#1a1a2e"}`). This is highly recommended for dark themes.
- **`html_attrs`**: A dict of HTML attributes to inject into the `<html>` and `<body>` tags of the canvas iframe.
- **`css` / `js`**: Lists of static files to load when the theme is active.
- **`css_bundles` / `js_bundles`**: Lists of Webpack bundle arguments to pass to `webpack_loader.utils.get_files` (e.g. `[("main",)]` or `[("main", "MY_CONFIG")]`).

> **Demo Example**: Run `just demo` and navigate to the **Alert** or **Badge** components. Toggle the global theme switcher to "Dark Theme" to see the dark canvas background applied and the component colours seamlessly adapt to dark mode (the dark theme CSS is defined in `example_project/static/example_project/theme-dark.css`).

---

## App-Specific Assets and Canvas Attributes

If you have multiple Django apps under the same codebase, you can restrict or load specific static assets and body classes for components belonging to particular apps.

### Settings Configuration
Configure app-specific assets and canvas HTML attributes in `settings.py`:

```python
dj_design_system = {
    "APP_CSS": {
        "admin_portal": ["admin/css/portal.css"],
    },
    "APP_JS": {
        "admin_portal": ["admin/js/portal.js"],
    },
    "APP_CANVAS_HTML_ATTRS": {
        "admin_portal": {
            "body": {"class": "admin-portal-active"},
        },
    },
}
```

When a component from `admin_portal` is rendered in the sandbox canvas:
1. The global styles (`GLOBAL_CSS` / `GLOBAL_JS`) are loaded.
2. The active theme styles and attributes are applied.
3. The app-specific styles (`APP_CSS` / `APP_JS`) and `APP_CANVAS_HTML_ATTRS` are applied.
4. The component's own CSS/JS are loaded.

---

## Controlling Theme Availability (Cascade)

By default, all components are rendered in all configured `GALLERY_THEMES`. You can restrict which themes are supported by a component or an entire app via the cascade.

### Cascade Rules (High to Low Priority):

1. **Component Meta**: Declare `available_themes` list in the component's inner `Meta` class:
   ```python
   class InfoCardComponent(BaseComponent):
       class Meta:
           available_themes = ["dark"]
   ```
   *In this case, the theme selector in the gallery sandbox toolbar will lock/disable or only show "Dark Theme".*

2. **App-wide defaults (`APP_THEMES`)**: Restrict all components in a specific Django app via `settings.py`:
   ```python
   dj_design_system = {
       "APP_THEMES": {
           "public_site": ["default", "light"],
           "admin_portal": ["default", "dark"],
       }
   }
   ```

3. **Global fallback**: If none of the above are defined, the component supports all themes defined in `GALLERY_THEMES`.

---

## Frontend Integration (Theme Manager)

The global stylesheet and script templatetags can act as a **Theme Manager** in your actual templates:

```django
{% load design_components %}

{# Dynamically loads global, theme, and app-specific styles #}
{% global_stylesheets app_label=request.resolver_match.app_name theme=request.session.user_theme %}

{# Dynamically loads global, theme, and app-specific scripts #}
{% global_scripts app_label=request.resolver_match.app_name theme=request.session.user_theme %}
```

This single tag intelligently renders the correct cascade of `link` and `script` tags (resolving Webpack bundles and static files without duplicate loading), maintaining perfect parity with the gallery sandbox canvas.
