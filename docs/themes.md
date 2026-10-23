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

---

<a id="theming-the-gallery-ui-with-tier-2---dds--tokens"></a>
## Theming the Gallery UI with Tier 2 `--dds-*` Tokens

The built-in `dds` gallery UI uses a **CUBE CSS** `@layer` cascade (`@layer reset, tokens, global, composition, blocks, utilities;`) and a **3-Tier Design Token System** defined in `dj_design_system/static/dj_design_system/tokens.css`:

1. **Tier 1 (`--_dds-*`) — Private Primitives**: Internal palette and scale primitives defined on `:root`. Never reference or override `--_dds-*` variables in consumer stylesheets.
2. **Tier 2 (`--dds-*`) — Public Semantic Contract**: Public semantic tokens across six domains (`layer`/`surface`, `font`/`text`, `space`/`layout`, `state`, `control`, `status`) defined on `:root` and `.gallery-theme-dark`, plus contextual `[data-surface='<name>']` scopes (`stage`, `code`, `docs`, `sandbox`, `topbar`, `sidebar`, `popout`, `overlay`).
3. **Tier 3 (`--_<component>-*`) — Component-Scoped Tokens**: Private tokens scoped to individual `.dds-<component>` roots, mapped exclusively from Tier 2 `--dds-*` tokens.

### Customising Tier 2 `--dds-*` Tokens

To re-theme the gallery chrome or reuse `dds__*` components with your brand palette, override the public Tier 2 `--dds-*` tokens on `:root` and `.gallery-theme-dark` (see [`example_project/static/example_project/theme-dds-consumer.css`](../example_project/static/example_project/theme-dds-consumer.css)):

```css
:root {
  --dds-color-accent: #0f766e;
  --dds-color-accent-hover: #115e59;
  --dds-control-accent-color: var(--dds-color-accent);
  --dds-control-border-radius: var(--dds-radius-md);
  --dds-font-sans: 'Inter', system-ui, -apple-system, sans-serif;
  --dds-font-ui: var(--dds-font-sans);
  --dds-radius-md: 0.5rem;
  --dds-state-focus-border-color: var(--dds-color-accent);
  --dds-state-focus-outline-color: var(--dds-color-accent);
  --dds-state-selected-border-color: var(--dds-color-accent);
}

.gallery-theme-dark {
  --dds-color-accent: #2dd4bf;
  --dds-color-accent-hover: #5eead4;
  --dds-control-accent-color: var(--dds-color-accent);
  --dds-state-focus-border-color: var(--dds-color-accent);
  --dds-state-focus-outline-color: var(--dds-color-accent);
  --dds-state-selected-border-color: var(--dds-color-accent);
}
```

### Every Layout `<l-*>` Composition Primitives

`dj_design_system/static/dj_design_system/composition.css` provides 11 intrinsic **Every Layout** composition primitives in `@layer composition` that can be used as custom elements (`<l-*>`) or classes (`.l-*`):

- `<l-stack>` / `.l-stack` — vertical flow rhythm (`--stack-space`)
- `<l-cluster>` / `.l-cluster` — wrapping horizontal groups (`--cluster-space`, `--cluster-align`, `--cluster-justify`)
- `<l-sidebar>` / `.l-sidebar` — intrinsic sidebar + main content split (`--sidebar-width`, `--sidebar-content-min`, `--sidebar-space`)
- `<l-switcher>` / `.l-switcher` — container-width responsive row-to-column switching (`--switcher-threshold`, `--switcher-space`)
- `<l-box>` / `.l-box` — padded/bordered surface container (`--box-padding`, `--box-border-width`)
- `<l-center>` / `.l-center` — horizontally centred measure container (`--center-measure`, `--center-gutters`)
- `<l-cover>` / `.l-cover` — vertically centred hero/empty-state layout (`--cover-min-height`, `--cover-space`)
- `<l-frame>` / `.l-frame` — aspect-ratio media container (`--frame-ratio`)
- `<l-grid>` / `.l-grid` — auto-fit responsive card grid (`--grid-min`, `--grid-space`)
- `<l-reel>` / `.l-reel` — horizontal scrolling track (`--reel-space`, `--reel-item-width`)
- `<l-imposter>` / `.l-imposter` — positioned overlay/modal container (`--imposter-margin`)

