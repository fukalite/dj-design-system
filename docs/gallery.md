# Component Gallery

The gallery provides a browsable UI for all registered components, with a
tree-view navigation sidebar built from the filesystem structure.

> **See it live:** A static snapshot of the example component gallery is deployed at
> [fukalite.github.io/dj-design-system/demo/](https://fukalite.github.io/dj-design-system/demo/).
> Note that HTMX-powered interactions (live canvas previews) are not available in the
> static snapshot — run the example project locally with `just demo` for the full
> interactive experience.

## Setup

Include the gallery URLs in your project:

```python
from django.urls import include, path

urlpatterns = [
    path("dds/", include("dj_design_system.urls")),
]
```

## URL Structure

All gallery pages live under a single prefix:

| URL                  | Description                           |
| -------------------- | ------------------------------------- |
| `/dds/`              | Gallery index                         |
| `/dds/<app>/`        | App root (folder listing or index.md) |
| `/dds/<app>/<path>/` | Component, document, or folder        |

The gallery determines the type of page to render (component, markdown
document, or folder listing) by looking up the path in the navigation tree —
no URL prefixes are needed to distinguish node types.

## Navigation Tree

The sidebar navigation is built automatically from:

1. **Registered components** — discovered from each app's `components/` package.
2. **Markdown files** — discovered from the same directories.

**Important:** every directory under `components/` must be a proper Python
package (contain an `__init__.py` file) for component auto-discovery to
traverse into it. Without `__init__.py`, `pkgutil.walk_packages` will skip
the directory and components inside it will not appear in the gallery.

### Leaf-folder collapsing

When the deepest folder name matches the component name, the folder is
collapsed. For example, `elements/icon/component.py` appears as _Icon_ under
_Elements_, not _Elements → Icon → Icon_.

### Markdown conventions

| File            | Behaviour                                          |
| --------------- | -------------------------------------------------- |
| `index.md`      | Attached to the parent folder or component node.   |
| Any other `.md` | Appears as a standalone document node in the tree. |

Case is ignored for `index.md` (e.g. `INDEX.MD` works too).

### Labels

Node labels are derived from the slug using sentence case:
`info_card` → _Info card_, `hero-banner` → _Hero banner_. App labels follow
the same rule but are rendered uppercase in the sidebar via CSS.

#### Overriding labels with `verbose_name`

Both apps and components can declare an explicit display label that takes
precedence over the auto-derived one:

**Apps** — set `verbose_name` on the `AppConfig`:

```python
class MyAppConfig(AppConfig):
    name = "my_app"
    verbose_name = "My design system"
```

**Components** — set `verbose_name` on the inner `Meta` class:

```python
class ButtonComponent(TagComponent):
    template_format_str = "<button>{label}</button>"
    label = StrParam("The button label")

    class Meta:
        verbose_name = "Action button"
```

The `verbose_name` is used in the sidebar navigation, breadcrumbs, and
all other display contexts. In the sidebar, app labels are rendered
uppercase via CSS regardless of the `verbose_name`.

#### Overriding folder labels and structuring with `COMPONENT_DIRECTORIES`

You can use the `COMPONENT_DIRECTORIES` setting in `settings.py` to customize the labels of intermediate folders that contain your components. You can also extract subdirectories out of their parent app and display them as top-level apps in the navigation sidebar using `promote_to_app`.

```python
DJ_DESIGN_SYSTEM = {
    "COMPONENT_DIRECTORIES": {
        "myapp": {
            "card": {
                "label": "Custom Cards Label",  # Customizes the folder name in the nav
            },
            "promoted_features": {
                "promote_to_app": True,  # Pulls this folder out to the root navigation level
                "label": "Promoted Features App",
            },
        }
    }
}
```

### Icons

The navigation sidebar displays SVG icons for node types:

- **Components** — a 3D box/package icon
- **Documents** — a page-with-lines icon
- **Folders** — a disclosure chevron (via `<details>`)

Icons are rendered via CSS `mask-image` with inline SVG data URIs (no
external dependencies or icon libraries).

## Component Pages

A component page has two panes:

### Documentation pane (primary)

Rendered in this order:

1. **Docstring** — the component class docstring, if present.
2. **Usage examples** — minimal and bigger (maximal) template tag usage
   with syntax-highlighted code blocks. Each example includes a small live
   preview iframe so the rendered result is visible inline.
3. **Parameters table** — name, type, required, default, choices, and
   description for each parameter.
4. **Markdown** — content from `index.md` in the component's directory, if
   present.

Each usage preview has a subtle link icon that switches to the sandbox
pane. URLs with the `#pane-sandbox` hash fragment open the sandbox
directly; the fragment stays in sync when switching panes via the header
toggle on narrow viewports.

### Sandbox pane

A live preview of the component rendered inside an **iframe canvas**. The
iframe provides full CSS/JS isolation from the gallery chrome — the
component is rendered in its own HTML document with the correct cascade:

1. Global CSS (`{% global_stylesheets %}`)
2. Theme CSS and active dark mode CSS (when `dark_mode` is configured and dark mode is active)
3. App-specific CSS (`APP_CSS`)
4. Canvas layout CSS (padding, backgrounds)
5. Component-specific CSS
6. Global JS (`GLOBAL_JS_BUNDLES`, `GLOBAL_JS`), then theme, dark mode, app, and component JS

A **toolbar** above the canvas provides:

- **Background picker** — choose from all configured background colours.
- **Viewport** — constrain the canvas to a preset width (Small mobile 320 px,
  Large mobile 414 px, Tablet 768 px, Desktop 1024 px, Full HD 1920 px,
  Ultrawide 2560 px) or leave it responsive. Viewports wider than the pane are scaled down to fit, just like
  browser DevTools responsive mode, so media queries still fire at the true
  width.
- **Zoom control** — scale the canvas from 25 % to 200 %.
- **Box model outline** — toggle a colour-coded outline that visualises
  element boundaries (orange outlines), padding areas (green tint), and
  the component root content area (blue tint).
- **Measure** — hover over any element to see its margin (orange), padding
  (green), and content area (blue) dimensions with pixel labels.
- **RTL** — toggle right-to-left text direction on the canvas to test
  bidirectional layout support.

Default parameter values are chosen automatically:

- If the parameter has a `default`, that value is used.
- If the parameter has `choices`, the first choice is used.
- For required string parameters without a default, the parameter name is
  used as placeholder text.
- `BlockComponent` subclasses receive `"Sample content"` as their content.

#### Canvas backgrounds

The canvas background defaults to the value of
`GALLERY_CANVAS_DEFAULT_BACKGROUND` (default: `"light-grey"`). Users can
switch backgrounds via the toolbar in the sandbox pane or via the `bg`
query parameter (e.g. `?bg=dark-grey`).

Built-in backgrounds: `white`, `light-grey`, `dark-grey`, `black`,
`checkerboard`.

To add project-specific backgrounds without replacing the built-in set,
use `GALLERY_CANVAS_EXTRA_BACKGROUNDS`. Each entry is a dict with
`value`, `color`, and optionally `label`:

```python
DJ_DESIGN_SYSTEM = {
    "GALLERY_CANVAS_EXTRA_BACKGROUNDS": {
        "brand-blue": {"color": "#e6ebf0", "label": "Brand Blue"},
    },
    "GALLERY_CANVAS_DEFAULT_BACKGROUND": "brand-blue",
}
```

Extra backgrounds are merged into the built-in set in the toolbar.
If a key in `GALLERY_CANVAS_EXTRA_BACKGROUNDS` matches a built-in key,
it will override the built-in entry.

To replace the built-in set entirely, set `GALLERY_CANVAS_BACKGROUNDS`
to a dict of `{slug: {"label": ..., "color": ...}}` entries.

#### Canvas HTML attributes

Some CSS frameworks (e.g. GOV.UK Frontend) scope their styles to specific
classes on the `<html>` or `<body>` element. Use
`GALLERY_CANVAS_HTML_ATTRS` to add these attributes to the canvas iframe's
document:

```python
DJ_DESIGN_SYSTEM = {
    "GALLERY_CANVAS_HTML_ATTRS": {
        "html": {"class": "govuk-template"},
    },
}
```

#### Canvas Dark Mode and Color Scheme

When previewing components in canvas iframes:

- The active theme's `dark_mode` configuration dictates whether dark mode can be activated (`supports_dark_mode=True`).
- When dark mode is active (`_dds_color_scheme=dark`), the canvas document merges `dark_mode.html_attrs` into `<html>` and `<body>`, appends `dark_mode.css` and `dark_mode.js`, and sets the dedicated dark mode background (`theme.dark_mode.canvas_background`).
- When a theme does not configure `dark_mode`, the preview canvas is constrained to light mode (`ColorScheme.LIGHT`), guarding against OS-level dark mode styles leaking into components that lack dark mode styling.
- Inline Markdown documentation canvas blocks (````canvas ... ````) automatically inherit and reflect the active color scheme.

<a id="customising-gallery-examples"></a>
## Customising Gallery Examples & Configuration

By default, the gallery generates minimal and maximal usage examples automatically based on parameter types. You can customize examples and configure rich component metadata by creating a side-car Python file next to your component (`gallery.py` or `<component_name>_gallery.py`).

### Modern Configuration: `GalleryConfig`

Export a `config` instance of `GalleryConfig`:

```python
# button_gallery.py or gallery.py
from dj_design_system.gallery import GalleryConfig, Variant

config = GalleryConfig(
    icon="ph:cursor-click",
    order=1,
    group="Actions",
    variants=[
        Variant(name="basic", label="Primary Button", kwargs={"label": "Click me"}),
        Variant(
            name="danger",
            label="Destructive Action",
            description="Use danger buttons for actions that cannot be undone, such as deleting a record.",
            kwargs={"label": "Delete Account", "variant": "danger"},
            icon="ph:trash",
            show_in_nav=True,
        ),
    ],
)
```

#### `GalleryConfig` Options

| Attribute | Type | Default | Description |
| --- | --- | --- | --- |
| `variants` | `list[Variant]` or `list[dict]` | `[]` | List of named component variants. Supports `Variant` instances or shorthand dicts. |
| `order` | `int` | `0` | Explicit ordering priority in the sidebar navigation. Lower numbers appear first. |
| `group` | `str | None` | `None` | Grouping sub-folder name in the sidebar navigation. |
| `icon` | `str | None` | `None` | Custom icon identifier (e.g. `"ph:cursor-click"`) for the component in the sidebar. |
| `theme` | `str | None` | `None` | Default theme override for previewing this component in the canvas. |
| `hidden` | `bool` | `False` | When `True`, hides the component and its variants from sidebar navigation and search. |
| `canvas_template`| `str | None` | `None` | HTML layout template for canvas previews (operates in Smart Hybrid mode). |
| `extra_context` | `dict[str, Any]` | `{}` | Context variables passed into canvas templates. |
| `param_defaults` | `dict[str, Any]` | `{}` | Base parameter defaults (supports values or callables for dynamic resolution). |

---

## Named Variants

The `Variant` class defines specific component variations, configurations, and documentation snippets.

```python
from dj_design_system.gallery import Variant

Variant(
    name="danger",
    label="Destructive Action",
    description="Rendered with high-visibility red contrast for irreversible actions.",
    kwargs={"label": "Delete Item", "variant": "danger"},
    positional_args=(),
    canvas_template=None,
    extra_context={},
    icon="ph:trash",
    theme=None,
    show_in_nav=True,
)
```

### Variant Attributes

- **`name`** (`str`): Unique slug identifier (e.g. `"basic"`, `"maximal"`, `"danger"`).
- **`label`** (`str | None`): Display label used in navigation and documentation. Defaults to title-cased name.
- **`description`** (`str | None`): Markdown documentation explaining the intended use of this variant.
- **`kwargs`** (`dict[str, Any]`): Parameter keyword arguments passed to the component tag. Supports static values, `GalleryParameter`, or dynamic callables.
- **`positional_args`** (`tuple[Any, ...]`): Positional argument values passed to the component tag.
- **`canvas_template`** (`str | None`): Variant-specific canvas layout template overriding the component's `canvas_template`.
- **`extra_context`** (`dict[str, Any]`): Extra context variables merged into preview rendering for this variant.
- **`icon`** (`str | None`): Custom icon identifier displayed next to the variant in the sidebar.
- **`theme`** (`str | None`): Theme override applied when previewing this specific variant.
- **`show_in_nav`** (`bool`): Whether this variant appears as a nested child link in the sidebar navigation. Defaults to `False` for default variants (`basic`, `maximal`) and `True` for custom variants.

### Focused Variant View & Breadcrumb Navigation

When navigating to a variant via deep-link (e.g. `/demo_components/badge/?variant=status`):

1. **Focused Documentation**: The usage section displays the dedicated variant title, badge, markdown description, a focused live preview canvas, and syntax-highlighted tag code.
2. **Breadcrumb Trail**: The active variant is appended as the terminal crumb:
   `Gallery / Demo Components / Badge / Status Indicator`
   Clicking the parent component in the breadcrumbs navigates directly back to the full component overview.
3. **Sandbox Pre-filling**: Form fields in the interactive Sandbox pane are automatically populated with the variant's arguments, and the toolbar preset selector reflects the active preset.

---

## Smart Hybrid `canvas_template`

The `canvas_template` option on `GalleryConfig` or `Variant` allows you to customize the HTML canvas wrapping your component preview. It operates in **Smart Hybrid mode**:

### 1. Wrapper Mode (`{{ component }}` present)

When your template string contains the `{{ component }}` placeholder, the component is rendered first and injected into your wrapper HTML along with any `extra_context`:

```python
config = GalleryConfig(
    canvas_template="""
    <div style="max-width: 400px; margin: 2rem auto; padding: 1.5rem; background: #f8fafc; border-radius: 8px;">
        <h4 style="margin-top:0;">Dialog Preview</h4>
        {{ component }}
    </div>
    """
)
```

### 2. Raw Template Mode (`{{ component }}` absent)

When `{{ component }}` is omitted, the template is rendered directly through Django's template engine as raw template code. `{% load design_components %}` is automatically injected if not already present:

```python
Variant(
    name="grid_preview",
    label="Card Grid Showcase",
    canvas_template="""
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
        {% card title="Card 1" %}<p>Body 1</p>{% endcard %}
        {% card title="Card 2" %}<p>Body 2</p>{% endcard %}
    </div>
    """,
    show_in_nav=True,
)
```

---

## Dynamic Callables & Parameter Evaluation

To avoid evaluating database queries or stateful models at Python import time, you can pass callables in `param_defaults` or variant `kwargs`:

```python
config = GalleryConfig(
    param_defaults={
        # Evaluated at canvas render time, NOT at import time:
        "active_user": lambda: User.objects.filter(is_active=True).first(),
        "timestamp": timezone.now,
    }
)
```

---

## Filling Slots in Variants

For components that accept named slots, provide slot content in variant `kwargs` using the `slot__` prefix:

```python
Variant(
    name="product_card",
    kwargs={
        "title": "Pro Plan",
        "slot__header": "<img src='banner.jpg' alt='Header'>",
        "slot__body": "<p>Full access to all components.</p>",
        "slot__footer": "<button type='button'>Upgrade</button>",
    },
)
```

---

## Upgrading Legacy Gallery Configurations

> [!WARNING] Deprecation Notice: Legacy Kwargs
> Defining `basic_kwargs` and `maximal_kwargs` dictionaries directly in gallery files is deprecated and will be removed in a future release.
> Export `config = GalleryConfig(...)` instead. The gallery currently maintains backwards compatibility and automatically synthesizes a `GalleryConfig` while emitting a `DeprecationWarning`.

### Automated Migration Command

Django Design System includes an automated management command that uses AST parsing to safely upgrade legacy `*_gallery.py` files across your apps:

```bash
# Check if unmigrated files exist (useful for CI)
python manage.py migrate_gallery_configs --check

# Dry-run migration
python manage.py migrate_gallery_configs --dry-run

# Perform migration across all apps
python manage.py migrate_gallery_configs

# Keep legacy basic_kwargs/maximal_kwargs variables alongside config
python manage.py migrate_gallery_configs --keep-legacy
```

### Manual Comparison

#### Before (Legacy)
```python
# badge_gallery.py
basic_kwargs = {
    "text": "New basic badge",
}

maximal_kwargs = {
    "text": "Critical Alert!",
    "theme": "danger",
    "slot__body": "Here is the body content",
    "user": GalleryParameter(value=User.objects.first(), code="request.user"),
}
```

#### After (Modern)
```python
# badge_gallery.py or gallery.py
from dj_design_system.gallery import GalleryConfig, Variant

config = GalleryConfig(
    variants=[
        Variant(name="basic", kwargs={"text": "New basic badge"}),
        Variant(
            name="maximal",
            kwargs={
                "text": "Critical Alert!",
                "theme": "danger",
                "slot__body": "Here is the body content",
                "user": GalleryParameter(
                    value=lambda: User.objects.first(), code="request.user"
                ),
            },
        ),
    ]
)
```

## Relative Links in Markdown

When writing markdown documentation, you can use standard relative file paths to link to other markdown documents within the design system. The gallery will automatically translate these relative paths into the correct dynamic gallery URLs, regardless of how your components are organized or aliased via settings.

For example, if you are editing `components/button/index.md` and want to link to `components/icon/index.md`:

```markdown
See the [Icon Component](../icon/index.md) for more details.
You can also use anchors: [Icon Attributes](../icon/index.md#attributes).
```

## Live Demos in Markdown

Markdown files (e.g. `index.md` in a component folder) can embed live component previews using fenced `canvas` blocks. Because the canvas block is rendered through Django's template engine, it fully supports **nested components**, **slots**, and **arbitrary HTML**.

` ```canvas
<div class="demo-wrapper">
  {% card title="Welcome" %}
    {% slot "body" %}
      <p>This is a nested card showing <strong>HTML</strong> and components together.</p>
      {% button label="Click me" %}
    {% endslot %}
  {% endcard %}
</div>
``` `

The syntax inside the block is standard Django template syntax (`{% load design_components %}` is applied automatically). All your registered components and template filters are available.

Each canvas block renders as a widget with:

- A **live preview** iframe (basic mode, auto-height, rendered via `srcdoc`).
- A **syntax-highlighted code block** showing the template tag.
- A small icon toggle in the bottom-right corner to switch between
  preview only, code only, or both (default).

Invalid syntax renders as a red error message. When `DEBUG = True`, the
original source is shown alongside the error.

### Browser Requirements

Canvas blocks use the `srcdoc` attribute on `<iframe>` elements to safely embed the fully rendered document without requiring additional HTTP requests.

This requires a modern browser. Minimum supported versions:
- Chrome ≥ 60
- Firefox ≥ 55
- Safari ≥ 12
- Edge ≥ 79

### Security Warning

Because canvas blocks are rendered using Django's template engine, **Django's auto-escaping protects against XSS** by default.

However, if your components use `ModelParam` to render database content, **do not use `|safe` or `mark_safe()`** on untrusted fields. If you disable auto-escaping on user-submitted data, that data will be executed in the canvas iframe.

## Syntax Highlighting

All fenced code blocks in documentation pages receive Pygments syntax
highlighting with a dark (Monokai) theme. The gallery automatically
detects Django template syntax (`{%` or `{{`) in untagged or
`py`/`python`-tagged fenced blocks and highlights them using the
`html+django` lexer.

To explicitly request Django template highlighting, use the
`html+django` language tag:

````markdown
```html+django
{% icon "check" size="large" %}
```
````

### Customising the highlight style

The Pygments style can be changed via the `GALLERY_CODEHILITE_STYLE`
setting. Set it to any [Pygments style name](https://pygments.org/styles/)
or to an empty string to disable highlighting entirely:

```python
DJ_DESIGN_SYSTEM = {
    "GALLERY_CODEHILITE_STYLE": "dracula",  # or "" to disable
}
```

Highlight colours are defined as CSS custom properties in
`gallery-highlight.css`. Override the `--hl-palette-*` variables for
palette changes, or the `--hl-*` semantic variables for finer control:

```css
:root {
  --hl-palette-keyword: #569cd6; /* change keyword colour */
  --hl-string: #ce9178; /* override just the string token */
}
```

## Settings

All settings are configured via the `dj_design_system` dictionary in
your Django settings module:

```python
from dj_design_system.types import NodeType

DJ_DESIGN_SYSTEM = {
    "ENABLE_GALLERY": True,
    "GALLERY_IS_PUBLIC": True,
    "DESIGN_SYSTEM_NAME": "Django Design System",
    "GALLERY_NAV_ORDER": [NodeType.FOLDER, NodeType.COMPONENT, NodeType.DOCUMENT],
}
```

| Setting                             | Type                      | Default                                                    | Description                                                 |
| ----------------------------------- | ------------------------- | ---------------------------------------------------------- | ----------------------------------------------------------- |
| `ENABLE_GALLERY`                    | `bool`                    | `True`                                                     | Enable or disable the gallery entirely.                     |
| `GALLERY_IS_PUBLIC`                 | `bool`                    | `True`                                                     | When `False`, requires the `can_view_gallery` perm.         |
| `DESIGN_SYSTEM_NAME`                | `str`                     | `"Django Design System"`                                   | Display name shown in the gallery header.                   |
| `GALLERY_INCLUDE_APPS`              | `list[str]` or `None`     | `None`                                                     | When set, only components from these apps appear in gallery.|
| `GALLERY_EXCLUDE_APPS`              | `list[str]`               | `[]`                                                       | App labels excluded from gallery navigation and search.     |
| `GALLERY_NAV_ORDER`                 | `list[NodeType]` or `str` | `[NodeType.FOLDER, NodeType.COMPONENT, NodeType.DOCUMENT]` | Controls the sort order of nodes in the sidebar.            |
| `GALLERY_CANVAS_DEFAULT_BACKGROUND` | `str`                     | `"light-grey"`                                             | Default background for the sandbox canvas.                  |
| `GALLERY_CANVAS_BACKGROUNDS`        | `dict`                    | `BUILTIN_CANVAS_BACKGROUNDS`                               | Dict of canvas backgrounds (replaces built-ins).            |
| `GALLERY_CANVAS_EXTRA_BACKGROUNDS`  | `dict`                    | `{}`                                                       | Extra backgrounds merged into the built-in set.             |
| `GALLERY_CANVAS_HTML_ATTRS`         | `dict`                    | `{}`                                                       | Extra attributes for the canvas `<html>` and `<body>` tags. |
| `GALLERY_CODEHILITE_STYLE`          | `str`                     | `"monokai"`                                                | Pygments style for code highlighting. `""` to disable.      |
| `GALLERY_EXTRA_CSS`                 | `list[str]`               | `[]`                                                       | Custom CSS static paths or external URLs loaded in `<head>`.|

### Navigation sort order

Within each level of the navigation tree, children are grouped by type
and then sorted alphabetically within each group. The `GALLERY_NAV_ORDER`
setting controls the order of those type groups.

The default value `[NodeType.FOLDER, NodeType.COMPONENT, NodeType.DOCUMENT]`
puts folders first, then components, then documents — matching the
convention used by most IDEs and file browsers.

Any permutation of the three `NodeType` values is valid:

```python
from dj_design_system.types import NodeType

# Documents first, then components, then folders
DJ_DESIGN_SYSTEM = {
    "GALLERY_NAV_ORDER": [NodeType.DOCUMENT, NodeType.COMPONENT, NodeType.FOLDER],
}
```

To ignore type grouping entirely and sort all nodes alphabetically by
label, use the string `"alphabetical"`:

```python
DJ_DESIGN_SYSTEM = {
    "GALLERY_NAV_ORDER": "alphabetical",
}
```

### Access control

By default, the gallery is public. To restrict access, set
`GALLERY_IS_PUBLIC = False` and assign the
`dj_design_system.can_view_gallery` permission to appropriate users.

---

## Customising Gallery Look and Feel

The gallery UI employs a modular, 3-tiered customisation architecture that allows consumers to tailor the appearance and layout from lightweight design token tweaks to bespoke template structures:

```
┌─────────────────────────────────────────────────────────────┐
│ Tier 1: Design Tokens (GALLERY_EXTRA_CSS)                   │
│ Override :root --dds-* tokens (colours, fonts, surfaces)    │
├─────────────────────────────────────────────────────────────┤
│ Tier 2: Template Areas & Panes                              │
│ Override areas (topbar, sidebar, tabs) & panes (docs, etc.) │
├─────────────────────────────────────────────────────────────┤
│ Tier 3: Component Shadowing                                 │
│ Shadow interactive widgets (canvas_widget, sandbox_params)  │
└─────────────────────────────────────────────────────────────┘
```

### Tier 1: Token Overrides via `GALLERY_EXTRA_CSS`

To brand the gallery chrome without modifying any templates, supply one or more CSS file paths in `GALLERY_EXTRA_CSS`. These files are linked in `<head>` after all built-in styles and component stylesheets:

```python
DJ_DESIGN_SYSTEM = {
    "GALLERY_EXTRA_CSS": [
        "myapp/css/gallery-theme.css",
    ],
}
```

Inside your CSS file, override the semantic `--dds-*` custom properties on `:root`:

```css
:root {
  /* Brand accents */
  --dds-brand-primary-color: #0052cc;
  --dds-brand-primary-hover-color: #0747a6;

  /* Typography */
  --dds-text-body-font: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --dds-text-heading-font: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;

  /* Surface & background colours */
  --dds-surface-bg-color: #f8fafc;
  --dds-surface-topbar-bg: #ffffff;
  --dds-surface-sidebar-bg: #f1f5f9;
  --dds-border-default-color: #e2e8f0;
}
```

### Tier 2: Overriding Template Areas and Panes

Layout and presentation markup are structured into modular Django templates under `dj_design_system/gallery/areas/` and `dj_design_system/gallery/panes/`. Structural layout across areas and panes is composed with **Every Layout** primitives (`<l-stack>`, `<l-cluster>`, `<l-sidebar>`, `<l-grid>`) in `@layer composition`. To customise any section, place a template with the matching path in your project's `templates/` directory:

#### Layout Areas (`dj_design_system/gallery/areas/`)

- **`areas/topbar.html`**: Header branding bar, mobile drawer toggle, breadcrumbs, search box trigger, theme dropdown (`{% dds__theme_select %}`, rendered when multiple themes exist), consumer color scheme toggle button (`action="toggle-consumer-color-scheme"`, enabled when the active theme configures `dark_mode`), and toolbar actions slot.
- **`areas/sidebar.html`**: Navigation drawer containing brand link, the interactive `<dds-nav-tree>`, and gallery UI theme toggle button (`action="toggle-theme"`).
- **`areas/tabs.html`**: Mobile responsive tabs switcher toggling between Documentation and Sandbox views.

#### Content Panes (`dj_design_system/gallery/panes/`)

- **`panes/docs.html`**: The documentation column on component pages. Composed of modular sub-templates:
  - `panes/docs/header.html`: Component title, docstring description, or active variant badge & preview.
  - `panes/docs/usage.html`: Minimal, maximal, and qualified tag code blocks and preview canvases.
  - `panes/docs/params.html`: Parameter specifications table and named slots table.
  - `panes/docs/further.html`: Extended Markdown documentation rendered from co-located `index.md`.
- **`panes/sandbox.html`**: The interactive testing canvas, controls toolbar, and live parameter editing form (`{% dds__sandbox_params %}`).
- **`panes/folder.html`**: Navigable card grid rendered when browsing folder nodes without an `index.md`.
- **`panes/index.html`**: Landing page welcome message and static snapshot notices.

#### The `<dds-gallery-shell>` Custom Element

While structural markup lives in templates, client-side coordination is handled by the `<dds-gallery-shell>` custom element (located in `dj_design_system/static/dj_design_system/gallery-shell.ts`). The custom element encapsulates:
1. **Responsive Drawer State:** Toggling `data-drawer-state="open|closed"` on mobile viewports.
2. **Backdrop & Keyboard Traps:** Managing focus and dismissing the drawer on backdrop clicks or Escape key presses.
3. **URL Hash Synchronisation:** Switching between Documentation and Sandbox tabs based on URL `#pane-*` fragments.
4. **Cross-Iframe Theme Event Relay:** Forwarding `dds:theme-change` CustomEvents from the outer gallery chrome into canvas iframes.
5. **Gallery UI Theme Management:** Switching the gallery chrome itself between Light, Dark, and System modes (`dds_gallery_theme` cookie / `localStorage` / `_dds_gallery_theme` query param) and toggling `.gallery-theme-dark` / `.gallery-theme-light` classes.
6. **Consumer Color Scheme Synchronisation:** Toggling previewed components between light and dark modes (`dds_color_scheme` cookie / `localStorage` / `_dds_color_scheme` query param), updating preview iframe URLs, synchronising the toggle button state (moon/sun icon and disabled state if unsupported), and dispatching `dds:consumer-color-scheme-change`.

### Tier 3: Built-in `dds` Primitives & Component Shadowing

The gallery UI delegates interactive widgets to built-in components:
- **`elements/`** (`badge`, `breadcrumb`, `button`, `code_block`, `form_field`, `icon`, `notice`, `popout`, `table`, `tabs`, `theme_select`) — reusable UI primitives registered as `{% dds__<name> %}`.
- **`domain/`** (`canvas_widget`, `nav_tree`, `sandbox_params`, `sandbox_toolbar`, `search_box`, `split_pane`) — interactive domain widgets registered as `{% dds__<name> %}`.

To shadow any built-in component with your own implementation, map a directory in `COMPONENT_DIRECTORIES`:

```python
from dj_design_system.types import FlattenStrategy

DJ_DESIGN_SYSTEM = {
    "COMPONENT_DIRECTORIES": {
        "myapp": {
            "dds_overrides": {
                "prefix": "dds",
                "flatten": FlattenStrategy.ALL,
            },
        },
    },
}
```

### Inspecting Built-in `dds` Components (`GALLERY_INCLUDE_APPS` & `GALLERY_EXCLUDE_APPS`)

By default, built-in `dj_design_system` components are excluded from consumer galleries, so the gallery sidebar and search index display only your project's own Django apps.

To browse and inspect the built-in `dj_design_system` component library inside the gallery in isolation, use `GALLERY_INCLUDE_APPS` (see [`example_project/settings_dds_gallery.py`](../example_project/settings_dds_gallery.py)):

```python
DJ_DESIGN_SYSTEM = {
    "DESIGN_SYSTEM_NAME": "Built-in Component Library",
    "GALLERY_INCLUDE_APPS": ["dj_design_system"],
}
```

---

## Content Security Policy (CSP)

The gallery UI and component canvas are fully compatible with strict Content Security Policies (`script-src` and `style-src` without `unsafe-inline`).

### Static Assets & Non-Inline Architecture
All gallery interactive logic (tab switching, theme selection, canvas height syncing, static snapshot notices) is loaded via external static JavaScript files under `{% static %}` URLs. No inline scripts or inline `style="..."` attributes are present in gallery templates.

### Automatic CSP Nonce Support
If your application uses CSP nonces (e.g. via `django-csp` middleware setting `request.csp_nonce`), `dj-design-system` automatically attaches `nonce="..."` attributes to:
- Static script tags in gallery templates (`{% if request.csp_nonce %}nonce="{{ request.csp_nonce }}"{% endif %}`)
- Dynamic `<script>` tags generated by `{% global_scripts %}` and `{% component_scripts %}`
- Dynamic `<style>` tags for canvas background rules generated by `build_canvas_bg_styles`
