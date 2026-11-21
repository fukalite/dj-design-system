# Template Tags

## How Auto-Registration Works

When Django starts, `DjangoDesignSystemConfig.ready()` triggers `component_registry.autodiscover()`, discovering all concrete `TagComponent` and `BlockComponent` subclasses across installed apps. Template tags are registered lazily on a `django.template.Library` when a template tag module calls `component_registry.register_templatetags(register)`.

## Tag Naming

### Short Name

Derived automatically from the class name, or set explicitly via `Meta.name`:

| Class Name | Derived Short Name |
| --- | --- |
| `IconComponent` | `icon` |
| `MyFancyButton` | `my_fancy_button` |
| `HeroCardComponent` | `hero_card` |

Override with `Meta.name`:

```python
class HeroCardComponent(TagComponent):
    class Meta:
        name = "hero"
```

Apps configured with `AppSettings(short_names=False)` (including built-in `dds__*` components and contrib packages) do not register short names, ensuring they never shadow host project tags.

### Qualified Name

By default, the qualified name is `{app_label}__{relative_path}__{name}` joined by `__`:

| Component Location | Qualified Name |
| --- | --- |
| `myapp/components/icon.py` → `IconComponent` | `myapp__icon` |
| `myapp/components/cards/info_card.py` → `InfoCardComponent` | `myapp__cards__info_card` |
| `myapp/components/cards/layouts/hero.py` → `HeroCardComponent` (`Meta.name = "hero"`) | `myapp__cards__layouts__hero` |

Customise prefixes and flattening via `AppSettings(prefix=..., flatten=..., directories={...})` on `AppConfig.design_system` or `DJ_DESIGN_SYSTEM.apps`. For example, mapping `prefix="ui"` gives `ui__icon`, and mapping `"cards": DirectorySettings(prefix="cards", flatten=FlattenStrategy.ALL)` flattens subfolders to `cards__hero`. See [Configuration](configuration.md#app-level-defaults-appconfigdesign_system).

Qualified names are always registered.

## Template Tag Libraries

### Central Library: `design_components`

Contains components from all installed apps:

```htmldjango
{% load design_components %}
{% icon "check" %}
{% callout type="info" %}Hello{% endcallout %}
{% myapp__cards__layouts__hero %}
```

### Per-App Libraries

Create a scoped library in `myapp/templatetags/components.py`:

```python
from django import template
from dj_design_system import component_registry

register = template.Library()
component_registry.register_templatetags(register, app_label="myapp")
```

Load it in templates with `{% load components %}`.

## Name Clashes and Overriding

When two or more components with `short_names=True` share a short name:

1. Every component remains available via its **qualified name**.
2. The short name is assigned to the **last-discovered component** in `INSTALLED_APPS` order.

Place your overriding app **after** the app you want to override in `INSTALLED_APPS`.

## Registration Types

| Component Base Class | Registration Method | Template Syntax |
| --- | --- | --- |
| `TagComponent` | `simple_tag` | `{% icon "check" %}` |
| `BlockComponent` | `simple_block_tag` | `{% callout %}...{% endcallout %}` |
| `BlockComponent` (slotted) | `library.tag` | `{% card %}{% slot "body" %}...{% endslot %}{% endcard %}` |
| `BaseComponent` (directly) | Not registered | Python-only usage |

### Slot Tag (`{% slot %}`)

Inside a slotted `BlockComponent`, capture named slot content with `{% slot "name" %}...{% endslot %}`:

```htmldjango
{% load design_components %}
{% card "My Card" %}
  {% slot "body" %}Card body content{% endslot %}
  {% slot "footer" %}Card footer{% endslot %}
{% endcard %}
```

Rules enforced at template parse time:

- Only whitespace and template comments may appear between adjacent `{% slot %}` blocks.
- Duplicate, unknown, or missing required slots raise `TemplateSyntaxError`.

## Media Tags

The `design_components` library provides four tags for injecting CSS and JS into base templates.

### `{% component_stylesheets %}` & `{% component_scripts %}`

Render deduplicated `<link rel="stylesheet">` and `<script>` tags for every co-located or `Media`-declared asset across non-built-in registered components (passing `request.csp_nonce` / `csp_nonce` automatically on scripts when present).

### `{% global_stylesheets %}` & `{% global_scripts %}`

Inject project global, theme, and app-specific CSS/JS bundles and asset paths in render cascade order (`DesignSystemSettings.{css, js, css_bundles, js_bundles}` → active `Theme` → resolved `AppSettings.{css, extra_css, js, extra_js, css_bundles, js_bundles}`):

```htmldjango
{% load design_components %}
<head>
    {% global_stylesheets app_label="shop" theme="brand" %}
    {% component_stylesheets %}
</head>
<body>
    ...
    {% global_scripts app_label="shop" theme="brand" %}
    {% component_scripts %}
</body>
```

Both `app_label` and `theme` keyword arguments are optional; omitting them renders only the project global assets. Entries starting with `http://`, `https://`, or `//` are emitted as-is. See [External Asset URLs & Webpack Bundles](configuration.md#external-asset-urls-webpack-bundles).

Example configuration in `settings.py`:

```python
from dj_design_system.config import DesignSystemSettings

DJ_DESIGN_SYSTEM = DesignSystemSettings(
    css_bundles=("main",),
    css=(
        "https://fonts.googleapis.com/css2?family=Inter&display=swap",
        "myapp/extra.css",
    ),
    js_bundles=("main",),
)
```

## Gallery Library: `dj_design_system_gallery`

Tags used by the gallery UI (`{% load dj_design_system_gallery %}`):

### `{% canvas %}...{% endcanvas %}`

Renders enclosed template content inside an isolated `<iframe srcdoc="...">` applying the full asset cascade, `CanvasSettings.default_background`, and `CanvasSettings.html_attrs` + theme/app HTML attributes:

```htmldjango
{% load design_components dj_design_system_gallery %}
{% canvas %}
    {% icon "check" %}
{% endcanvas %}
```

### `{% gallery_extra_stylesheets %}`, `{% gallery_ui_theme_stylesheets %}`, `{% gallery_ui_theme_scripts %}`

Emit stylesheet and script tags for `GallerySettings.extra_css` and the active `GallerySettings.ui_themes` entry.

### `{% builtin_component_stylesheets %}` & `{% builtin_component_scripts %}`

Emit stylesheet and ES module script tags for built-in `dds__*` gallery components.
