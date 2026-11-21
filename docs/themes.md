# Themes & Styling

This guide covers configuring gallery UI chrome themes, consumer component themes, explicit dark mode support, theme availability cascades, frontend template tag integration, and Tier 2 `--dds-*` design token customisation.

For app-specific CSS/JS assets and `canvas_html_attrs` layering, see [Configuration](configuration.md#resolution-precedence-render-cascades).

---

## Two Distinct Theming Layers

Django Design System decouples two independent theming layers:

1. **Gallery UI Theme (Chrome)** — `GallerySettings.ui_themes` and `GallerySettings.default_ui_theme`:
   - Controls the gallery shell itself (sidebar, topbar, documentation panes, controls).
   - Ships with two built-in UI themes in `DDS_DEFAULT_UI_THEMES`: **Desert** (default, supports dark mode) and **Classic** (light-only).
   - Selected via the UI Theme selector (`_dds_gallery_ui_theme`) and toggled between light/dark via the sidebar footer toggle (`action="toggle-theme"`).
   - Persisted in `dds_gallery_ui_theme` and `dds_gallery_theme` cookies/`localStorage`, dispatching `dds:gallery-ui-theme-change` and `dds:gallery-theme-change`.

2. **Consumer Component Themes & Dark Mode (Previews + Frontend)** — `DesignSystemSettings.themes` and `DesignSystemSettings.default_theme`:
   - Controls stylesheets, scripts, HTML attributes, and preview backgrounds for your components inside canvas iframes, markdown `canvas` blocks, and `{% global_stylesheets theme=... %}`.
   - When multiple themes are configured, a Theme Selector dropdown appears in the topbar (`_dds_theme`).
   - When the active theme defines `dark_mode=DarkModeConfig(...)`, the topbar Colour Scheme toggle (`action="toggle-consumer-color-scheme"`) becomes active (`_dds_color_scheme`). When `dark_mode` is omitted (`None`), previews lock strictly to `ColorScheme.LIGHT` so OS dark mode never bleeds into light-only themes.
   - Persisted in `dds_theme` and `dds_color_scheme`, dispatching `dds:consumer-color-scheme-change`.

---

## Configuring Gallery UI Themes (`GallerySettings.ui_themes`)

Extend `DDS_DEFAULT_UI_THEMES` with custom `Theme` instances in `settings.py`:

```python
from dj_design_system.config import (
    DDS_DEFAULT_UI_THEMES,
    DarkModeConfig,
    DesignSystemSettings,
    GallerySettings,
    Theme,
)

DJ_DESIGN_SYSTEM = DesignSystemSettings(
    gallery=GallerySettings(
        ui_themes={
            **DDS_DEFAULT_UI_THEMES,
            "corporate": Theme(
                label="Corporate Slate",
                css=("css/gallery-theme-corporate.css",),
                js=("js/gallery-theme-corporate.js",),
                dark_mode=DarkModeConfig(
                    css=("css/gallery-theme-corporate-dark.css",),
                ),
            ),
        },
        default_ui_theme="desert",
    ),
)
```

When a UI theme other than `"desert"` is active, the gallery attaches `.gallery-ui-theme-<slug>` to `<html>` and `<dds-gallery-shell>`, letting you scope Tier 2 token overrides cleanly:

```css
.gallery-ui-theme-corporate {
  --dds-color-accent: #2563eb;
  --dds-surface-sidebar-bg-color: #1e293b;
  --dds-surface-sidebar-text-color: #f8fafc;
}

.gallery-ui-theme-corporate.gallery-theme-dark {
  --dds-color-accent: #60a5fa;
  --dds-surface-sidebar-bg-color: #0f172a;
}
```

---

## Configuring Consumer Themes (`DesignSystemSettings.themes`)

Consumer themes sit at the top level of `DesignSystemSettings` because they are used both inside the gallery and at runtime via `{% global_stylesheets theme=... %}`:

```python
from dj_design_system.config import (
    CanvasBackground,
    DarkModeConfig,
    DesignSystemSettings,
    Theme,
)

DJ_DESIGN_SYSTEM = DesignSystemSettings(
    themes={
        "brand": Theme(
            label="Brand Theme",
            canvas_background="white",
            html_attrs={
                "html": {"data-theme": "brand-light"},
                "body": {"class": "brand-theme-light"},
            },
            css=("css/brand.css",),
            js=("js/brand.js",),
            dark_mode=DarkModeConfig(
                canvas_background=CanvasBackground(label="Midnight", color="#1a1a2e"),
                html_attrs={
                    "html": {"data-theme": "brand-dark"},
                    "body": {"class": "brand-theme-dark"},
                },
                css=("css/brand-dark.css",),
            ),
        ),
        "classic": Theme(
            label="Classic (Light Only)",
            canvas_background="light-grey",
            html_attrs={"html": {"data-theme": "classic"}},
            css=("css/classic.css",),
        ),
    },
    default_theme="brand",
)
```

- **`Theme.value`** is populated automatically from the mapping key when omitted.
- **`canvas_background`** accepts either a slug defined in `CanvasSettings.backgrounds` (`"white"`, `"light-grey"`, `"dark-grey"`, `"black"`, `"checkerboard"`) or an inline `CanvasBackground(color=..., label=...)`.
- **`dark_mode`**: when set to a `DarkModeConfig(...)`, `theme.supports_dark_mode` is `True`; its `html_attrs` merge over the base theme's attributes (a `None` value acts as a deletion tombstone), and its `css` / `js` / bundles append after the base theme's assets.

Programmatic callers can read configured themes through `dj_design_system.services.config` (`get_themes()`, `get_theme(identifier=...)`, `get_default_theme()`).

---

## Theme Availability Cascade

By default, every component supports every theme in `DesignSystemSettings.themes`. Restrict theme availability at any tier (highest to lowest priority):

1. **Component `Meta.available_themes`**:
   ```python
   class InfoCardComponent(TagComponent):
       class Meta:
           available_themes = ("dark",)
   ```
2. **Project per-app override (`DJ_DESIGN_SYSTEM.apps[label].themes`)**:
   ```python
   DJ_DESIGN_SYSTEM = DesignSystemSettings(
       apps={
           "admin_portal": AppSettings(themes=("default", "dark")),
       }
   )
   ```
3. **App default (`AppConfig.design_system.themes`)**:
   ```python
   class PublicSiteConfig(AppConfig):
       name = "public_site"
       design_system = AppSettings(themes=("default", "brand"))
   ```
4. **Project global fallback (`DesignSystemSettings.themes`)**: all configured project themes (`themes=None` explicitly restores all project themes; `themes=()` allows none).

---

## Frontend Integration (Theme Manager)

Use `{% global_stylesheets %}` and `{% global_scripts %}` in your production base template to emit the exact same asset cascade (project global → active theme → app assets) used in the gallery canvas:

```htmldjango
{% load design_components %}

{% global_stylesheets app_label=request.resolver_match.app_name theme=request.session.user_theme %}
{% global_scripts app_label=request.resolver_match.app_name theme=request.session.user_theme %}
```

---

<a id="theming-the-gallery-ui-with-tier-2---dds--tokens"></a>
## Theming the Gallery UI with Tier 2 `--dds-*` Tokens

The built-in `dds` gallery UI uses a **CUBE CSS** cascade (`@layer reset, tokens, global, composition, blocks, utilities;`) and a 3-tier token architecture defined in `dj_design_system/static/dj_design_system/tokens.css`:

1. **Tier 1 (`--_dds-*`) — Private Primitives**: internal palette and scale values on `:root`. Never reference or override `--_dds-*` in consumer stylesheets.
2. **Tier 2 (`--dds-*`) — Public Semantic Contract**: semantic tokens across `layer`/`surface`, `font`/`text`, `space`/`layout`, `state`, `control`, and `status`, plus contextual `[data-surface='<name>']` scopes (`stage`, `code`, `docs`, `sandbox`, `topbar`, `sidebar`, `popout`, `overlay`).
3. **Tier 3 (`--_<component>-*`) — Component Tokens**: private tokens scoped to `.dds-<component>` roots, derived strictly from Tier 2 tokens.

### Customising Tier 2 `--dds-*` Tokens

Load a custom stylesheet via `GallerySettings(extra_css=("myapp/css/gallery-theme.css",))` and override public `--dds-*` tokens on `:root` and `.gallery-theme-dark` (see [`example_project/static/example_project/theme-dds-consumer.css`](https://github.com/fukalite/dj-design-system/blob/main/example_project/static/example_project/theme-dds-consumer.css)):

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

`dj_design_system/static/dj_design_system/composition.css` provides 11 intrinsic **Every Layout** primitives in `@layer composition` usable as custom elements (`<l-*>`) or classes (`.l-*`):

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
