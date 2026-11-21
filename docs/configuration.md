# Configuration

`dj-design-system` works with zero configuration out of the box. When you need to customise gallery behaviour, global assets, themes, preview canvases, or per-app component namespaces, configure two complementary layers:

1. **Project-level settings** via `DJ_DESIGN_SYSTEM = DesignSystemSettings(...)` in your Django `settings.py`.
2. **App-level defaults** via `design_system = AppSettings(...)` on any Django `AppConfig` subclass.

Importing from `dj_design_system.config` executes no Django imports and never accesses `django.conf.settings`, so it is safe at the top of any `settings.py` or `apps.py`.

For field-by-field signatures and types, see the [Configuration & Settings API Reference](api/settings.md).

---

## Project-Level Settings (`DesignSystemSettings`)

Assign an immutable `DesignSystemSettings` instance to `DJ_DESIGN_SYSTEM` in `settings.py`. Runtime assets and consumer themes sit at the root, while gallery chrome, preview canvas options, and per-app overrides live in dedicated sub-objects:

```python
from dj_design_system.config import (
    AppSettings,
    CanvasBackground,
    CanvasSettings,
    DarkModeConfig,
    DDS_DEFAULT_CANVAS_BACKGROUNDS,
    DesignSystemSettings,
    DirectorySettings,
    FlattenStrategy,
    GallerySettings,
    Theme,
)

DJ_DESIGN_SYSTEM = DesignSystemSettings(
    name="Acme Design System",
    css=("site/tokens.css", "site/components.css"),
    js=("site/components.js",),
    themes={
        "default": Theme(
            label="Light",
            html_attrs={"html": {"data-theme": "light"}},
            canvas_background="white",
            dark_mode=DarkModeConfig(
                html_attrs={"html": {"data-theme": "dark"}},
                canvas_background="dark-grey",
            ),
        ),
    },
    default_theme="default",
    gallery=GallerySettings(
        is_public=False,
        exclude_apps=("admin",),
    ),
    canvas=CanvasSettings(
        backgrounds={
            **DDS_DEFAULT_CANVAS_BACKGROUNDS,
            "warm": CanvasBackground(label="Warm Paper", color="#faf6f0"),
        },
        default_background="warm",
    ),
    apps={
        "third_party_ui": AppSettings(
            extra_css=("site/third-party-tweaks.css",),
        ),
    },
)
```

### Prefixed Built-In Defaults

All built-in defaults exported from `dj_design_system.config` use the `DDS_DEFAULT_*` prefix so importing them into `settings.py` never clashes with project constants:

- `DDS_DEFAULT_THEMES` — `{"default": Theme(...)}`
- `DDS_DEFAULT_UI_THEMES` — `"desert"` (with `DarkModeConfig()`) and `"classic"`
- `DDS_DEFAULT_CANVAS_BACKGROUNDS` — `"white"`, `"light-grey"`, `"dark-grey"`, `"black"`, `"checkerboard"`
- `DDS_DEFAULT_DOC_VARIANTS` — `"minimal"`, `"maximal"`, `"defaults"`, `"all_slots"`
- `DDS_DEFAULT_NAV_ORDER` — `(NodeType.FOLDER, NodeType.COMPONENT, NodeType.DOCUMENT)`

### Split Settings with `.replace(...)`

Every settings dataclass provides `.replace(**changes)` so environment-specific settings modules can inherit cleanly from a base configuration without mutating shared dicts:

```python
# settings/production.py
from myproject.settings.base import *  # noqa: F401, F403

DJ_DESIGN_SYSTEM = DJ_DESIGN_SYSTEM.replace(
    gallery=DJ_DESIGN_SYSTEM.gallery.replace(enabled=False),
)
```

### Disabling the Gallery Per Environment

Setting `GallerySettings(enabled=False)` returns HTTP `404` for all gallery views and gallery REST API endpoints before authentication or permission checks run, while keeping template tags (`{% load design_components %}`) active in production templates:

```python
DJ_DESIGN_SYSTEM = DesignSystemSettings(
    gallery=GallerySettings(enabled=False),
)
```

### Access Control & App Visibility

- Set `GallerySettings(is_public=False)` to restrict gallery access to authenticated users holding the `dj_design_system.can_view_gallery` permission.
- Set `GallerySettings(include_apps=("my_app",))` to show only listed apps (for example `include_apps=("dj_design_system",)` to inspect the built-in `dds` component library in isolation).
- Set `GallerySettings(exclude_apps=("legacy_app",))` to hide specific apps from gallery navigation, search, counts, and the REST API. Hidden components remain usable as template tags.

---

## App-Level Defaults (`AppConfig.design_system`)

Each Django app can declare its own default `AppSettings` directly on its `AppConfig` subclass so app-owned stylesheets, prefixes, directory rules, and navigation ordering stay co-located with the app:

```python
# myapp/apps.py
from django.apps import AppConfig
from dj_design_system.config import AppSettings, DirectorySettings, FlattenStrategy


class MyAppConfig(AppConfig):
    name = "myapp"
    verbose_name = "Marketing UI"
    design_system = AppSettings(
        prefix="mkt",
        flatten=FlattenStrategy.LEAF,
        css=("myapp/marketing.css",),
        canvas_html_attrs={"body": {"class": "mkt-scope"}},
        directories={
            "cards": DirectorySettings(label="Editorial Cards", order=1),
            "foundations": DirectorySettings(
                label="Foundations",
                promote_to_app=True,
                order=0,
            ),
        },
    )
```

Fields omitted on `AppSettings` default to the `UNSET` sentinel ("inherit from lower tier"), distinguishing an omitted field from an explicitly cleared `None` or `()`.

---

## Resolution Precedence & Render Cascades

Project-level settings sit at two distinct points depending on whether a setting is **inherited** or **layered**.

### 1. Inherited Settings (4-Tier Override Stack)

Settings with a project-wide default resolve top-down, with project per-app overrides always taking final precedence:

```text
Project per-app override   (DJ_DESIGN_SYSTEM.apps[app_label])
          │
          ▼
App default                (AppConfig.design_system)
          │
          ▼
Project global default     (DJ_DESIGN_SYSTEM / gallery.*)
          │
          ▼
Built-in library default   (DDS_DEFAULT_*)
```

- **`nav_order`**: `DirectorySettings.nav_order` → Project `apps[label].nav_order` → `AppConfig.design_system.nav_order` → Project `gallery.nav_order` → `DDS_DEFAULT_NAV_ORDER`.
- **`themes`**: Component `Meta.available_themes` → Project `apps[label].themes` → `AppConfig.design_system.themes` → Project `DJ_DESIGN_SYSTEM.themes` → `DDS_DEFAULT_THEMES`.
- **App-only settings** (`label`, `order`, `prefix`, `flatten`, `short_names`, `directories`): Project `apps[label]` → `AppConfig.design_system` → built-in default.

### 2. Layered Settings (Additive Render Cascades)

Project global assets and canvas attributes are never replaced by app settings; resolved app values layer after project global values in render order:

- **Assets (`css`, `js`, webpack bundles)**:
  `Project global (DJ_DESIGN_SYSTEM.css)` → `Active Theme (theme.css / dark_mode.css)` → `Resolved App (AppConfig → Project apps[label] + extra_css)` → `Component co-located media`.
- **Canvas HTML attributes**:
  `Project global (canvas.html_attrs)` → `Active Theme` → `Dark mode` → `Resolved App (AppConfig → Project apps[label])`.

### 3. Merging `AppConfig` with `DJ_DESIGN_SYSTEM.apps[label]`

- **`css` / `js`**: Setting `css=(...)` on `DJ_DESIGN_SYSTEM.apps[label]` replaces the app's base list (`css=()` clears it). Setting `extra_css=(...)` appends after the resolved base list (deduplicated, preserving order) without importing third-party `apps.py` inside `settings.py`. The same rule applies to `js` and `extra_js`.
- **Mappings (`canvas_html_attrs`, `directories`)**: Shallow-merged by key across `AppConfig` → Project override. A value of `None` deletes an inherited key (tombstone); setting the entire field to `None` clears the app mapping.
- **Scalars and other sequences**: An explicit project value replaces the app value.

---

## Navigation Ordering (`app_order`, `order`, and `nav_order`)

### Top-Level Sidebar Order

1. Apps and promoted directories listed in `GallerySettings.app_order` appear first in that exact sequence.
2. Unlisted apps and promoted roots follow sorted by `(order, label.lower())`, reading `AppSettings.order` or `DirectorySettings.order`.

### Intra-App & Folder Order (`nav_order`)

`nav_order` can be set globally on `GallerySettings`, per app on `AppSettings`, or per folder on `DirectorySettings`:

- **Type grouping** (default): pass a tuple of `NodeType` members, e.g. `(NodeType.FOLDER, NodeType.COMPONENT, NodeType.DOCUMENT)`.
- **Alphabetical**: pass `"alphabetical"` to ignore node types and sort by `(order, label.lower())`.
- **Manual slug pinning**: mix plain string slugs with `NodeType` buckets to pin specific direct children in declared order (slug pins on `AppSettings.nav_order` apply to the app root and do not leak into nested subfolders):

```python
from dj_design_system.config import AppSettings, DirectorySettings, NodeType

AppSettings(
    nav_order=(
        "getting_started",
        NodeType.FOLDER,
        NodeType.COMPONENT,
        NodeType.DOCUMENT,
    ),
    directories={
        "primitives": DirectorySettings(
            nav_order=("colour", "typography", NodeType.COMPONENT),
        ),
    },
)
```

Within each unlisted group, children sort by `(node.order, node.label.lower())` (honouring `GalleryConfig.order` and `DirectorySettings.order`).

---

## Reusable & Contrib App Author Guide

When shipping a reusable Django app or contrib package containing components:

1. **Rely on `AppConfig.verbose_name`** for the gallery display name rather than setting `AppSettings.label` unless the gallery label must differ from `verbose_name`.
2. **Choose a short, unique prefix with `short_names=False`** and `flatten=FlattenStrategy.ALL` so your components never collide with host project short tags:

   ```python
   from django.apps import AppConfig
   from dj_design_system.config import AppSettings, FlattenStrategy


   class AcmeWidgetsConfig(AppConfig):
       name = "acme_widgets"
       verbose_name = "Acme Widgets"
       design_system = AppSettings(
           prefix="acme",
           flatten=FlattenStrategy.ALL,
           short_names=False,
           css=("acme_widgets/widgets.css",),
       )
   ```

3. **Keep consumer customisation import-free**: host projects can layer tweaks onto your app using `extra_css` / `extra_js` or override `prefix` in `DJ_DESIGN_SYSTEM.apps["acme_widgets"]` without importing `acme_widgets.apps` in `settings.py`.
4. **Built-in shadowing**: the whole-app prefix `"dds"` is reserved for `dj_design_system` (`dj_design_system.E005`), but a consumer subfolder may declare `DirectorySettings(prefix="dds", flatten=FlattenStrategy.ALL)` to intentionally shadow specific built-in `dds__*` components.

---

## External Asset URLs & Webpack Bundles

- Any `css`, `extra_css`, `js`, `extra_js`, or `gallery.extra_css` entry starting with `http://`, `https://`, or `//` is emitted as-is rather than passed through Django's `static()` helper.
- `css_bundles` and `js_bundles` accept either bare bundle name strings (`"main"`, using webpack-loader's `"DEFAULT"` config) or 1-/2-tuples (`("main",)`, `("main", "CUSTOM")`). Bundles are silently skipped when `django-webpack-loader` is not installed.

---

## Django System Checks

Run `python manage.py check --tag dj_design_system` to validate configuration proactively:

| ID | Level | Condition |
| --- | --- | --- |
| `E001`–`E003` | Error | Invalid `include_apps` / `exclude_apps` types or overlapping entries. |
| `E004`–`E006` | Error | Invalid prefix syntax (`^[a-z][a-z0-9_]*$`, no `__`), reserved whole-app `"dds"` prefix, or duplicate effective app prefix across installed apps. |
| `E009` | Error | `settings.DJ_DESIGN_SYSTEM` is not a `DesignSystemSettings` instance or `None` (including removed legacy `dict` settings), or fails schema validation. |
| `E010` | Error | `AppConfig.design_system` is set to a non-`AppSettings` value. |
| `E011` | Error | `apps["dj_design_system"]` attempts to override `prefix`, `flatten`, or `short_names`. |
| `E012` | Error | `Theme.value` does not match its mapping key in `themes` or `gallery.ui_themes`. |
| `E013` | Error | `promote_to_app=True` root slug collides with an installed app, another promoted directory, or a nested promoted parent/child. |
| `W001`–`W002` | Warning | Redundant `exclude_apps` alongside `include_apps`, or uninstalled app in visibility lists. |
| `W003` | Warning | Key in `DesignSystemSettings.apps` is not in `INSTALLED_APPS`. |
| `W004` | Warning | `default_theme`, `default_ui_theme`, or `default_background` is missing from its mapping. |
| `W005` | Warning | `Theme.canvas_background` or `DarkModeConfig.canvas_background` slug is not in `canvas.backgrounds`. |
| `W006` | Warning | `AppSettings.themes` references an unknown theme slug or is empty `()`. |
| `W007` | Warning | Configured `AppSettings.directories` path does not exist under the app's `components/` folder. |

---

## Startup-Bound vs Request-Time Settings

When testing with Django's `@override_settings(DJ_DESIGN_SYSTEM=...)`:

- **Request-time dynamic** (take effect immediately on the next call; `setting_changed` clears config and navigation caches automatically): `name`, `css`, `js`, bundles, `themes`, `default_theme`, all `gallery.*` and `canvas.*` fields, `AppSettings.{label, order, nav_order, themes, css, extra_css, js, extra_js, css_bundles, js_bundles, canvas_html_attrs}`, and `DirectorySettings.{label, order, nav_order, promote_to_app}`.
- **Startup-bound** (baked onto frozen `ComponentInfo` during `ComponentRegistry.autodiscover()`): `AppSettings.{prefix, flatten, short_names}` and `DirectorySettings.{prefix, flatten}`. Tests that override these must run discovery on a fresh `ComponentRegistry`.

See [Integration Testing](testing.md#testing-with-override_settings) for patterns using `.replace(...)`.

---

## Manual Template Loader & Static Finder Setup

`DjangoDesignSystemConfig.ready()` automatically registers `ComponentsTemplateLoader` and `ComponentsStaticFinder` when you use Django's default `TEMPLATES` and `STATICFILES_FINDERS`. If your project declares custom `loaders` or `STATICFILES_FINDERS` explicitly, include them yourself:

```python
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "dj_design_system.finders.ComponentsStaticFinder",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": False,
        "OPTIONS": {
            "loaders": [
                (
                    "django.template.loaders.cached.Loader",
                    [
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                        "dj_design_system.loaders.ComponentsTemplateLoader",
                    ],
                ),
            ],
        },
    },
]
```

---

## Upgrading from `v0.9.x`

Support for flat `DJ_DESIGN_SYSTEM = {...}` dictionaries, `dds_settings`, `COMPONENT_NAMESPACES`, and `manage.py migrate_dds_settings` was removed in `v1.0.0`. Passing a plain `dict` as `DJ_DESIGN_SYSTEM` now fails `manage.py check --tag dj_design_system` with `dj_design_system.E009` and raises `ImproperlyConfigured` at runtime.

To migrate an existing `v0.9.x` project automatically, upgrade to the `v0.10.x` stepping-stone release first, run `python manage.py migrate_dds_settings` (and verify with `--check`), and then upgrade to `v1.0.0`.
