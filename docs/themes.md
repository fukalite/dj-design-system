# Themes and App-Specific Assets

This document describes how to configure and use themes, explicit dark mode support, available themes per component, and app-specific static assets within the Django Design System.

---

## Two Distinct Theming Layers

The Django Design System cleanly decouples two independent layers of theming:

1. **Gallery UI Theme (Chrome)**:
   Controls the visual appearance of the gallery shell itself (sidebar navigation, header topbar, documentation panes, controls, and form inputs).
   - Supports **Light Mode**, **Dark Mode**, and **System Preference**.
   - Toggled via the theme button in the **sidebar footer** (`action="toggle-theme"` with sun/moon icon).
   - Governed by Tier 2 `--dds-*` semantic tokens on `:root` and `.gallery-theme-dark` in `tokens.css`.
   - Persisted via the `dds_gallery_theme` cookie and `localStorage` (or `_dds_gallery_theme` query parameter).
   - Dispatches a `dds:gallery-theme-change` DOM event.

2. **Consumer Component Themes and Dark Mode (Canvas Previews)**:
   Controls the stylesheets, scripts, HTML attributes, and canvas backgrounds applied to the **previewed components** inside iframe canvases and markdown preview blocks.
   - Configured via `GALLERY_THEMES` in `DJ_DESIGN_SYSTEM` settings.
   - If multiple themes are defined, a **Theme Selector** dropdown appears in the topbar (`_dds_theme`). If only a single theme is configured, the redundant dropdown is automatically omitted.
   - Each theme can explicitly declare a **`dark_mode`** configuration.
   - When the active theme configures `dark_mode`, an interactive **Color Scheme Toggle** (`action="toggle-consumer-color-scheme"`, sun/moon icon) appears in the topbar, allowing you to preview components in light or dark mode (`_dds_color_scheme`).
   - When the active theme does *not* configure `dark_mode`, the topbar toggle button is disabled with the tooltip `"Consumer theme does not support dark mode"`. Previews are strictly locked to light mode (`ColorScheme.LIGHT`), ensuring that host operating system dark mode settings do not unexpectedly alter components that lack dark mode styles.
   - Persisted via the `dds_color_scheme` cookie and `localStorage` (or `_dds_color_scheme` query parameter).
   - Dispatches a `dds:consumer-color-scheme-change` DOM event.

---

## Configuring Consumer Themes (`GALLERY_THEMES`)

Themes allow you to customize the styling and attributes of your components inside the gallery sandbox, and provide a **Theme Manager** to style the actual frontend of your project.

Define your themes in your Django `settings.py` file under `DJ_DESIGN_SYSTEM`:

```python
DJ_DESIGN_SYSTEM = {
    "GALLERY_THEMES": {
        "brand": {
            "label": "Brand Theme",
            "canvas_background": "white",
            "html_attrs": {
                "html": {"data-theme": "brand-light"},
                "body": {"class": "brand-theme-light"},
            },
            "css": ["css/brand.css"],
            "js": ["js/brand.js"],
            "css_bundles": [],
            "js_bundles": [],
            # Explicit dark mode support for this theme:
            "dark_mode": {
                "canvas_background": "dark-grey",
                "html_attrs": {
                    "html": {"data-theme": "brand-dark"},
                    "body": {"class": "brand-theme-dark"},
                },
                "css": ["css/brand-dark.css"],
                "js": [],
                "css_bundles": [],
                "js_bundles": [],
            },
        },
        "classic": {
            "label": "Classic (Light Only)",
            "canvas_background": "light-grey",
            "html_attrs": {
                "html": {"data-theme": "classic"},
            },
            "css": ["css/classic.css"],
            # No dark_mode defined: consumer color scheme toggle will be disabled when active
        },
    },
    "GALLERY_DEFAULT_THEME": "brand",
}
```

### Key Properties of a Theme Configuration

Each entry in `GALLERY_THEMES` is keyed by its unique slug identifier and accepts the following properties:

- **`label`**: The display label rendered in the gallery topbar theme dropdown. Defaults to capitalized key.
- **`canvas_background`**: An optional default background for the preview iframe when this theme is active. Can be a built-in slug (`"white"`, `"light-grey"`, `"dark-grey"`, `"black"`, `"checkerboard"`) or a custom dictionary (e.g. `{"label": "Midnight", "color": "#1a1a2e"}`).
- **`html_attrs`**: A dict of HTML attributes to inject into the `<html>` and `<body>` tags of the canvas iframe (e.g. `{"html": {"data-theme": "brand"}, "body": {"class": "brand-body"}}`).
- **`css` / `js`**: Lists of static files or external URLs to load when this theme is active.
- **`css_bundles` / `js_bundles`**: Lists of Webpack bundle arguments to pass to `webpack_loader.utils.get_files` (e.g. `[("main",)]` or `[("main", "MY_CONFIG")]`).
- **`dark_mode`**: An optional dictionary specifying dark mode overrides and additions for this theme.

### Dark Mode Configuration (`dark_mode`)

When `dark_mode` is configured on a theme, the theme's `supports_dark_mode` property evaluates to `True`, enabling the color scheme toggle button in the gallery topbar.

The `dark_mode` dictionary accepts:

- **`canvas_background`**: An optional background applied to the preview canvas when dark mode is active. Can be a built-in slug (e.g. `"dark-grey"`, `"black"`) or a custom dictionary (e.g. `{"label": "Dark Surface", "color": "#1e1e2e"}`). If omitted, the base theme background is used.
- **`html_attrs`**: HTML attributes merged into `<html>` and `<body>` tags when dark mode is active. Matching keys override the base theme attributes (e.g. swapping `data-theme="brand-light"` to `data-theme="brand-dark"`).
- **`css`**: Additional stylesheets loaded in addition to the base theme CSS when dark mode is active.
- **`js`**: Additional scripts loaded in addition to the base theme JS when dark mode is active.
- **`css_bundles` / `js_bundles`**: Additional Webpack bundles loaded when dark mode is active.

### Typed Theme Objects

For typing and programmatic access, `dj_design_system.types` exposes dataclasses:

```python
from dj_design_system.types import ColorScheme, DarkModeConfig, Theme

theme = Theme(
    value="dds",
    label="Django Design System",
    html_attrs={"html": {"class": "gallery-theme-light"}},
    canvas_background="white",
    dark_mode=DarkModeConfig(
        html_attrs={"html": {"class": "gallery-theme-dark"}},
        canvas_background="dark-grey",
    ),
)

assert theme.supports_dark_mode is True
```

Use `get_themes()` from `dj_design_system.settings` to retrieve all normalized `Theme` instances, or `get_theme(identifier)` to fetch a single theme.

> **Demo Examples**:
> - Run `just demo dds` to browse the built-in DDS component library with explicit dark mode support enabled (defined in `example_project/settings_dds_gallery.py`). Toggle the sun/moon icon in the topbar to watch the component canvas seamlessly adapt between light and dark modes.
> - Run `just demo` to inspect the multi-theme setup in `example_project/settings.py`. Toggle between "Default Theme" and "Dark Theme" in the topbar. Notice that because these legacy demo themes do not declare an internal `dark_mode` config, the consumer color scheme button is gracefully disabled.

---

## App-Specific Assets and Canvas Attributes

If you have multiple Django apps under the same codebase, you can restrict or load specific static assets and body classes for components belonging to particular apps.

### Settings Configuration
Configure app-specific assets and canvas HTML attributes in `settings.py`:

```python
DJ_DESIGN_SYSTEM = {
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
   DJ_DESIGN_SYSTEM = {
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

