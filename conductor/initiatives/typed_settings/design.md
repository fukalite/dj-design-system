# Design Document: Typed & Devolved Settings (`typed_settings`)

This document specifies the target configuration architecture for `dj-design-system`: replacing the 29 flat `DJ_DESIGN_SYSTEM` dictionary keys with grouped, immutable, typed dataclasses, devolving app-scoped defaults onto Django `AppConfig` subclasses, unifying manual and app-delegated navigation ordering, overhauling configuration documentation, and executing a `v0.10.0` to `v1.0.0` deprecation and migration lifecycle.

---

## 1. Problem Forces & Goals

Configuring a single app today scatters keys across seven separate top-level dictionaries in `settings.py` (`APP_CSS`, `APP_JS`, `APP_CSS_BUNDLES`, `APP_JS_BUNDLES`, `APP_THEMES`, `APP_CANVAS_HTML_ATTRS`, `COMPONENT_DIRECTORIES`). Reusable and contrib apps cannot ship sensible defaults without asking every host project to duplicate those entries in `settings.py`. Meanwhile, 29 flat `SCREAMING_SNAKE_CASE` keys mix runtime assets, gallery chrome, preview canvas configuration, and per-app overrides into one untyped dictionary where typos fail silently and [dj_design_system/settings.py](../../../dj_design_system/settings.py) carries nearly 600 lines of manual dictionary coercion.

This design solves four concerns together:
- **App-level devolution with project sovereignty**: Apps declare defaults on `AppConfig.design_system = AppSettings(...)`, while the host project keeps final override control in `DJ_DESIGN_SYSTEM`.
- **Static safety and small surface area**: Six public settings types replace 29 flat keys and seven parallel app maps, providing IDE autocomplete, `mypy` checking, and proactive Django system checks.
- **Safe `settings.py` imports**: Importing `dj_design_system.config` at the top of any `settings.py` or `apps.py` executes zero Django imports and never touches `django.conf.settings`.
- **Clean migration path**: Legacy flat dictionaries remain supported throughout `v0.10.x` via a compatibility adapter, `RemovedInDjDS10Warning`, Django system checks, and `manage.py migrate_dds_settings`, before bundled removal in `v1.0.0`.

---

## 2. Import-Safety Boundary

Importing any `dj_design_system` submodule inside a project's `settings.py` currently triggers `dj_design_system/__init__.py` -> `components/base.py` -> `parameters/user.py` (`settings.AUTH_USER_MODEL`), forcing Django to evaluate a half-executed settings module.

To keep `from dj_design_system.config import ...` safe at line 1 of any `settings.py` or `apps.py`:

1. **PEP 562 lazy re-exports in [dj_design_system/\_\_init\_\_.py](../../../dj_design_system/__init__.py)**:
   - Move eager imports of `components`, `data`, `gallery`, `services.registry`, and `slots` under `if TYPE_CHECKING:`.
   - Resolve public symbols on demand in `__getattr__(name: str)` (caching resolved values in `globals()[name]` so `unittest.mock.patch` works) and expose `__dir__()`.
2. **Stdlib-only acyclic configuration stack**:
   ```text
   constants.py  (stdlib only)
        ^
   types.py      (stdlib + constants.py; enums & value types)
        ^
   config.py     (stdlib + constants.py + types.py; settings)
   ```
   - `constants.py`, `types.py`, and `config.py` must never import `django.*`, `dj_design_system.settings`, `dj_design_system.services.*`, `dj_design_system.components.*`, `dj_design_system.data`, or `dj_design_system.gallery`.
3. **Lazy `AUTH_USER_MODEL` in [dj_design_system/parameters/user.py](../../../dj_design_system/parameters/user.py) and [model.py](../../../dj_design_system/parameters/model.py)**:
   - `ModelParam.__init_subclass__` validates `getattr(own_meta, "model", None) is not None` at class-definition time.
   - Extend `ModelParam._resolve_model()` to accept a zero-arg callable (`if callable(model) and not isinstance(model, type): model = model()`), and define `UserParam.Meta.model = staticmethod(lambda: settings.AUTH_USER_MODEL)`.
4. **CI verification**:
   - Subprocess test with `DJANGO_SETTINGS_MODULE` unset importing `dj_design_system.config`, `dj_design_system.types`, and `dj_design_system.constants` and asserting `"django" not in sys.modules`.

---

## 3. Public Configuration Schema (`dj_design_system/config.py`)

### 3.1 Naming, Immutability & Split-Settings Ergonomics
- **`*Settings`** is reserved exclusively for Django settings-layer types: `DesignSystemSettings`, `GallerySettings`, `CanvasSettings`, `AppSettings`, `DirectorySettings`.
- **`*Config`** remains on component/data-layer types (`GalleryConfig` in `dj_design_system/gallery.py`, `DarkModeConfig`, `DocVariantConfig`).
- **Pickle- and deepcopy-safe frozen mappings**: Bare `MappingProxyType` fails under `copy.deepcopy`, `dataclasses.asdict`, and `pickle`. Wrap frozen mappings in a small stdlib `FrozenMapping(Mapping[K, V])` implementing `__deepcopy__`, `__reduce__`, and equality with `dict`.
- **Ergonomic split-settings helper**: `DesignSystemSettings`, `GallerySettings`, `CanvasSettings`, `AppSettings`, and `DirectorySettings` provide `.replace(**kwargs)` (delegating to `dataclasses.replace`) so split settings files (`settings/base.py` -> `settings/prod.py`, `example_project/settings_dds.py`) stay concise:
  ```python
  # Non-binding exemplar
  DJ_DESIGN_SYSTEM = DJ_DESIGN_SYSTEM.replace(
      name="dj-design-system (dds Built-in Gallery)",
      gallery=DJ_DESIGN_SYSTEM.gallery.replace(include_apps=("dj_design_system",)),
  )
  ```
- **`UNSET` sentinel**: Single-member enum `_UnsetType.UNSET` (`UNSET: Final[_UnsetType]`) used strictly on `AppSettings` to distinguish *"omitted (inherit from lower tier)"* from *"explicitly cleared (`None` or `()`)"*.

### 3.2 Shared Value Types & Type Aliases

| Symbol | Shape & Invariants |
|---|---|
| `HtmlAttrsDict` (`TypedDict(total=False)`) | `html: Mapping[str, str \| None]`, `body: Mapping[str, str \| None]`. Plain dict at runtime; `None` attribute values act as deletion tombstones during app/project merging and are stripped before rendering. |
| `WebpackBundleSpec` (type alias) | `str \| tuple[str] \| tuple[str, str]` (e.g. `"main"` or `("main", "CUSTOM")`). Bare `str` rejected as the outer sequence value. |
| `NavOrderSpec` (type alias) | `tuple[NodeType \| str, ...] \| Literal["alphabetical"]`. |
| `CanvasBackground` (`@dataclass(frozen=True)`) | `color: str`, `label: str = ""`. The mapping key in `CanvasSettings.backgrounds` is the slug; `label=""` supports colour-only theme backgrounds. |
| `DarkModeConfig` (`@dataclass(frozen=True)`) | `html_attrs: HtmlAttrsDict`, `css: tuple[str, ...] = ()`, `js: tuple[str, ...] = ()`, `css_bundles: tuple[WebpackBundleSpec, ...] = ()`, `js_bundles: tuple[WebpackBundleSpec, ...] = ()`, `canvas_background: str \| CanvasBackground \| None = None`. Coerces `str` paths and raw `canvas_background` dicts in `__post_init__`. |
| `Theme` (`@dataclass(frozen=True)`) | `value: str = ""`, `label: str = ""`, `html_attrs`, `css`, `js`, `css_bundles`, `js_bundles`, `canvas_background`, `dark_mode: DarkModeConfig \| None = None`. Retains `supports_dark_mode`, `has_dark_mode_assets`, `has_external_assets`. When placed in a `themes` mapping with `value=""`, the key populates `value` internally and `label` defaults to `value.capitalize()`. |
| `DocVariantConfig` (`@dataclass(frozen=True)`) | `key`, `name`, `label`, `strategy: DocVariantStrategy`, `show_in_docs: bool = True`, `kwargs: FrozenMapping`, `param_factory`, `slot_factory`. |

### 3.3 Public Settings Classes (6 Symbols)

#### `DirectorySettings` (`@dataclass(frozen=True)`)
Subfolder rules inside `AppSettings.directories`:
- `prefix: str | None = None` — Tag prefix for this subtree (`None` preserves parent/app prefix for presentation-only entries).
- `flatten: FlattenStrategy | None = None` — Folder flattening strategy (`None` preserves parent/app prefix inheritance for label-only / `promote_to_app`-only entries).
- `label: str | None = None` — Custom display label in gallery navigation and breadcrumbs.
- `promote_to_app: bool = False` — Promotes the directory to a top-level gallery app section.
- `order: int | None = None` — Numeric sort weight among sibling folders or top-level promoted apps (aligned with PR #262).
- `nav_order: NavOrderSpec | None = None` — Ordering for this folder's direct children (`None` inherits app/project `nav_order`).

#### `AppSettings` (`@dataclass(frozen=True)`)
Attached to `AppConfig.design_system` (app defaults) and `DesignSystemSettings.apps[app_label]` (project overrides). All fields default to `UNSET`:
- `label: str | None | _UnsetType = UNSET` — Gallery display name override (falls back to `AppConfig.verbose_name`, then capitalised `app_label`).
- `order: int | _UnsetType = UNSET` — Numeric sort weight among top-level sidebar apps (aligned with PR #262; superseded when project specifies `gallery.app_order`).
- `nav_order: NavOrderSpec | _UnsetType = UNSET` — App-level ordering for root children inside this app (inherits `GallerySettings.nav_order` when `UNSET`).
- `prefix: str | None | _UnsetType = UNSET` — App-wide tag prefix (absorbs PR #285's `AppConfig.dds_component_prefix` and replaces `COMPONENT_DIRECTORIES[app][""]`).
- `flatten: FlattenStrategy | _UnsetType = UNSET` — App-wide flattening strategy (default `FlattenStrategy.NONE`; contrib apps set `FlattenStrategy.ALL`).
- `short_names: bool | _UnsetType = UNSET` — Whether bare short tags (`{% button %}`) and unscoped `get_by_name()` lookups are registered (default `True`; contrib apps and built-ins set `False`).
- `themes: tuple[str, ...] | None | _UnsetType = UNSET` — Allowlist of theme slugs (`None` = all project themes; `()` = none).
- `css: tuple[str, ...] | _UnsetType = UNSET` — App static stylesheets / URLs (coerces `str | Sequence[str]`); replaces lower tier.
- `extra_css: tuple[str, ...] | _UnsetType = UNSET` — Additive stylesheets appended after resolved `css` (deduplicated preserving order), allowing projects to layer overrides onto third-party apps without importing third-party `apps.py` inside `settings.py`.
- `js: tuple[str, ...] | _UnsetType = UNSET` — App static scripts / URLs (coerces `str | Sequence[str]`); replaces lower tier.
- `extra_js: tuple[str, ...] | _UnsetType = UNSET` — Additive scripts appended after resolved `js` (deduplicated preserving order).
- `css_bundles: tuple[WebpackBundleSpec, ...] | _UnsetType = UNSET` — App webpack CSS bundles.
- `js_bundles: tuple[WebpackBundleSpec, ...] | _UnsetType = UNSET` — App webpack JS bundles.
- `canvas_html_attrs: HtmlAttrsDict | None | _UnsetType = UNSET` — App-scoped canvas `<html>`/`<body>` attributes.
- `directories: Mapping[str, DirectorySettings | None] | None | _UnsetType = UNSET` — Per-subfolder rules keyed by dot-separated relative path. Rejects `""` in `__post_init__` (root settings belong on `AppSettings` directly).

#### `CanvasSettings` (`@dataclass(frozen=True)`)
Sibling to `gallery` on `DesignSystemSettings` (keeps nesting at max 2 levels and serves `{% canvas %}` tags alongside gallery previews):
- `backgrounds: Mapping[str, CanvasBackground] = DDS_DEFAULT_CANVAS_BACKGROUNDS`
- `default_background: str = "light-grey"`
- `html_attrs: HtmlAttrsDict = FrozenMapping()`

#### `GallerySettings` (`@dataclass(frozen=True)`)
- `enabled: bool = True` — Enforced in `gallery_access_required` ([dj_design_system/views/decorators.py](../../../dj_design_system/views/decorators.py)) across gallery and gallery REST API views; raises `Http404` before auth/public checks when `False` so specific environments can disable the gallery cleanly.
- `is_public: bool = True`
- `app_order: tuple[str, ...] = ()` — Explicit top-level sidebar ordering of app labels and promoted root slugs; unlisted apps follow by numeric `order`, then alphabetically.
- `nav_order: NavOrderSpec = DDS_DEFAULT_NAV_ORDER` — Project default intra-app ordering strategy (inheritable and overridable via `AppSettings.nav_order` and `DirectorySettings.nav_order`).
- `codehilite_style: str | None = "monokai"` (`None` or `""` disables Pygments highlighting).
- `ui_themes: Mapping[str, Theme] = DDS_DEFAULT_UI_THEMES`
- `default_ui_theme: str = "desert"`
- `include_apps: tuple[str, ...] | None = None` (`None` = all non-excluded; `()` = none).
- `exclude_apps: tuple[str, ...] = ()`
- `extra_css: tuple[str, ...] = ()`
- `doc_variants: Mapping[str, DocVariantConfig] = DDS_DEFAULT_DOC_VARIANTS` *(retains disabled built-ins with `show_in_docs=False` so per-component `GalleryConfig.doc_variants` can still re-enable `"defaults"` or `"all_slots"` with their built-in strategy)*.

#### `DesignSystemSettings` (`@dataclass(frozen=True)`)
Root object assigned to `settings.DJ_DESIGN_SYSTEM`:
- `name: str = "Django Design System"`
- `css: tuple[str, ...] = ()`
- `js: tuple[str, ...] = ()`
- `css_bundles: tuple[WebpackBundleSpec, ...] = ()`
- `js_bundles: tuple[WebpackBundleSpec, ...] = ()`
- `themes: Mapping[str, Theme] = DDS_DEFAULT_THEMES` *(top-level because `{% global_stylesheets theme=... %}` and `BaseComponent.get_available_themes()` operate outside the gallery)*.
- `default_theme: str = "default"`
- `gallery: GallerySettings = field(default_factory=GallerySettings)`
- `canvas: CanvasSettings = field(default_factory=CanvasSettings)`
- `apps: Mapping[str, AppSettings] = FrozenMapping()`

### 3.4 Prefixed Immutable Defaults Exported from `dj_design_system/config.py`
All built-in defaults share the unified `DDS_DEFAULT_*` prefix so importing them into `settings.py` never clashes with Django or project constants (legacy `BUILTIN_CANVAS_BACKGROUNDS` and `BUILTIN_DOC_VARIANTS` remain on the `0.10.x` `dj_design_system/settings.py` facade only):
- `DDS_DEFAULT_THEMES` (`"default"`)
- `DDS_DEFAULT_UI_THEMES` (`"desert"` with `DarkModeConfig()`, `"classic"`)
- `DDS_DEFAULT_CANVAS_BACKGROUNDS` (`"white"`, `"light-grey"`, `"dark-grey"`, `"black"`, `"checkerboard"`)
- `DDS_DEFAULT_DOC_VARIANTS` (`"minimal"`, `"maximal"`, `"defaults"`, `"all_slots"`)
- `DDS_DEFAULT_NAV_ORDER` (`(NodeType.FOLDER, NodeType.COMPONENT, NodeType.DOCUMENT)`)

### 3.5 Disposition of All 29 Legacy Keys

| Legacy Key(s) | New Location | Notes |
|---|---|---|
| `DESIGN_SYSTEM_NAME` | `DesignSystemSettings.name` | Direct |
| `ENABLE_GALLERY` | `GallerySettings.enabled` | Wired into `gallery_access_required` (returns `404` when `False`) |
| `GALLERY_IS_PUBLIC` | `GallerySettings.is_public` | Direct |
| `GALLERY_NAV_ORDER` | `GallerySettings.nav_order` (+ `AppSettings` / `DirectorySettings`) | Preserves `"alphabetical"` and `NodeType` lists; adds manual slug pinning and app delegation |
| `GLOBAL_CSS`, `GLOBAL_JS` | `DesignSystemSettings.css`, `.js` | Accepts `str` or sequence in `__post_init__` |
| `GLOBAL_CSS_BUNDLES`, `GLOBAL_JS_BUNDLES` | `DesignSystemSettings.css_bundles`, `.js_bundles` | Accepts `str` or `(name, config)` tuples |
| `GALLERY_THEMES`, `GALLERY_DEFAULT_THEME` | `DesignSystemSettings.themes`, `.default_theme` | Promoted to root |
| `GALLERY_UI_THEMES`, `GALLERY_DEFAULT_UI_THEME` | `GallerySettings.ui_themes`, `.default_ui_theme` | Gallery chrome only |
| `GALLERY_INCLUDE_APPS`, `GALLERY_EXCLUDE_APPS` | `GallerySettings.include_apps`, `.exclude_apps` | `None` vs `()` distinction preserved |
| `GALLERY_EXTRA_CSS`, `GALLERY_CODEHILITE_STYLE` | `GallerySettings.extra_css`, `.codehilite_style` | `""` and `None` both disable highlighting |
| `GALLERY_DOC_VARIANTS` | `GallerySettings.doc_variants` | Retains disabled built-in keys |
| `GALLERY_CANVAS_BACKGROUNDS` | `CanvasSettings.backgrounds` | `{}` clears built-ins |
| `GALLERY_CANVAS_EXTRA_BACKGROUNDS` | **Merged into `CanvasSettings.backgrounds`** | Use `{**DDS_DEFAULT_CANVAS_BACKGROUNDS, ...}`; adapter merges automatically in `0.10.x` |
| `GALLERY_CANVAS_DEFAULT_BACKGROUND` | `CanvasSettings.default_background` | Direct |
| `GALLERY_CANVAS_HTML_ATTRS` | `CanvasSettings.html_attrs` | `HtmlAttrsDict` |
| `APP_THEMES`, `APP_CSS`, `APP_JS`, `APP_CSS_BUNDLES`, `APP_JS_BUNDLES`, `APP_CANVAS_HTML_ATTRS` | `AppConfig.design_system` or `DesignSystemSettings.apps[label]` | Collapsed from 6 parallel dicts into one `AppSettings` |
| `COMPONENT_DIRECTORIES` | `AppSettings.{prefix, flatten, label, order, directories}` | Magic `""` key promoted to root `AppSettings` fields |
| `COMPONENT_NAMESPACES` | **Removed** | Already deprecated (`remove_namespaces_20260720`); adapted per-app as fallback in `0.10.x` |

---

## 4. App-Level & Project-Level Resolution Protocol

### 4.1 Precedence Model & Render Cascades

Project-level settings sit at **two** distinct points depending on whether a setting is **inherited** or **layered**:

1. **Inherited settings (4-tier override stack)** — applies to settings with a project-wide default that apps can specialise (`nav_order`, `themes`):
   ```text
   Project per-app override  (DJ_DESIGN_SYSTEM.apps[label])
                    |
                    v
   App default               (AppConfig.design_system)
                    |
                    v
   Project global default    (DJ_DESIGN_SYSTEM / gallery.*)
                    |
                    v
   Built-in library default  (DDS_DEFAULT_*)
   ```
   - `nav_order`: `DirectorySettings.nav_order` > Project `apps[label].nav_order` > `AppConfig.design_system.nav_order` > Project `gallery.nav_order` > `DDS_DEFAULT_NAV_ORDER`.
   - `themes`: Component `Meta.available_themes` > Project `apps[label].themes` > `AppConfig.design_system.themes` > Project `DJ_DESIGN_SYSTEM.themes` > `DDS_DEFAULT_THEMES`.
   - App-only settings (`label`, `order`, `prefix`, `flatten`, `short_names`, `directories`) skip tier 3: Project `apps[label]` > `AppConfig.design_system` > Built-in default.

2. **Layered settings (additive render cascade)** — project global assets and canvas attributes are never replaced by app settings; resolved app values layer after project global values in render order:
   - **Assets (`css`, `js`, bundles)**: `Project global (DJ_DESIGN_SYSTEM.css)` -> `Active Theme (theme.css / dark_mode.css)` -> `Resolved App (AppConfig -> Project apps[label] + extra_css)` -> `Component co-located media`.
   - **Canvas HTML attrs**: `Project global (canvas.html_attrs)` -> `Active Theme` -> `Dark mode` -> `Resolved App (AppConfig -> Project apps[label])`. Never pre-merge `CanvasSettings.html_attrs` into app settings.

3. **Intra-app merge rules (`AppConfig` -> `DJ_DESIGN_SYSTEM.apps[label]`)**:
   - Only `AppSettings` uses `UNSET` ("inherit").
   - `css` / `js`: explicit project `css` replaces the app's base list (`css=()` clears it); project `extra_css` appends after the resolved base list (deduplicated via `dict.fromkeys`). Same for `js` / `extra_js`.
   - Other scalars and sequences (`themes`, `css_bundles`, `js_bundles`, `nav_order`): explicit project value replaces the app value.
   - Mappings (`canvas_html_attrs`, `directories`): shallow-merge by key across App -> Project; `None` as a value deletes an inherited key; `None` on the whole field clears the app mapping.

4. **Manual & delegated navigation ordering**:
   - **Top-level sidebar**: Apps and promoted roots listed in `GallerySettings.app_order` appear first in that exact sequence; unlisted apps follow sorted by `(order, label.lower())` using `AppSettings.order` / `DirectorySettings.order` (aligned with PR #262).
   - **Within an app or folder (`nav_order`)**:
     - Plain `str` slugs pin matching direct children first in declared order (`isinstance(item, NodeType)` cleanly distinguishes `NodeType.FOLDER` from a slug named `"folder"`).
     - Remaining unlisted children group by any `NodeType` entries in `nav_order` (or remain flat when `"alphabetical"`), sorted within each group by `(node.order, node.label.lower())` (honouring PR #262 frontmatter, `GalleryConfig.order`, and `DirectorySettings.order`).

5. **Startup vs request-time lifecycle**:
   - **Startup-bound** (baked onto frozen `ComponentInfo` during `ComponentRegistry.autodiscover()`): `prefix`, `flatten`, `short_names`, and `directories[path].{prefix, flatten}`. Tests changing these must re-run discovery on a fresh `ComponentRegistry`.
   - **Request-time dynamic** (respond immediately to `@override_settings`): `name`, `css`, `js`, bundles, `themes`, `default_theme`, `gallery.*`, `canvas.*`, `AppSettings.{label, order, nav_order, themes, css, extra_css, js, extra_js, bundles, canvas_html_attrs}`, `DirectorySettings.{label, order, nav_order, promote_to_app}`.

### 4.2 `AppConfig` & Contrib Integration
- Apps declare `design_system = AppSettings(...)` on their `AppConfig` subclass.
- `DjangoDesignSystemConfig` ([dj_design_system/apps.py](../../../dj_design_system/apps.py)) dogfoods `design_system = AppSettings(prefix="dds", flatten=FlattenStrategy.ALL, short_names=False)`.
- PR #285's `AppConfig.dds_component_prefix` is absorbed pre-merge into `AppConfig.design_system = AppSettings(prefix=..., flatten=FlattenStrategy.ALL, short_names=False)` so `ContribAppConfig` (PR #286) uses a single config attribute.
- Tag prefix resolution in [dj_design_system/services/registry.py](../../../dj_design_system/services/registry.py) walks `relative_path` longest-match first:
  - A `DirectorySettings` with `prefix is None and flatten is None` (e.g. `DirectorySettings(promote_to_app=True, label="...")`) is presentation-only and inherits the parent directory or `AppSettings.prefix`.
  - When `short_names=False`, the app registers only `qualified_name` tags and is skipped by unscoped `get_by_name(name)` (still reachable via `get_by_name(name, app_label=...)` and `resolve_component()`).
- Synthetic/uninstalled app labels catch `LookupError` from `apps.get_app_config(app_label)` and still resolve from `DJ_DESIGN_SYSTEM.apps.get(app_label)`.

### 4.3 Caching, Signals & Service API (`dj_design_system/services/config.py`)
- **Startup gate**: Scan `AppConfig.design_system` only when `apps.apps_ready` is `True` (not `apps.ready`, which is `False` during `DjangoDesignSystemConfig.ready()` -> `autodiscover()`). Never cache before `apps.apps_ready`.
- **Safe caching**:
  - Single-slot `(raw_obj, resolved)` identity cache for immutable `DesignSystemSettings` (immune to `id()` reuse and leaks across `@override_settings`).
  - Mutable legacy `dict` settings are adapted on read (immune to in-place dict mutation in tests) with warning deduplication keyed by `frozenset(raw.keys())` reset on `setting_changed`.
- **Signal invalidation**: Connect `django.core.signals.setting_changed` in `DjangoDesignSystemConfig.ready()` (before `autodiscover()`) and clear both config caches and `navigation_service.clear_navigation_cache()` whenever `setting in ("DJ_DESIGN_SYSTEM", "INSTALLED_APPS")`.
- **Internal resolved types**: `_ResolvedAppSettings` and `_ResolvedDirectorySettings` (zero `UNSET` sentinels, `extra_css`/`extra_js` folded, `None` tombstones stripped) remain internal to `services/config.py`.
- **Typed service accessors** (keyword-only args per `layered-architecture.md`): `get_config()`, `get_gallery_settings()`, `get_canvas_settings()`, `get_app_settings(*, app_label)`, `get_all_app_settings()`, `get_themes()`, `get_theme(*, identifier)`, `get_default_theme()`, `get_gallery_ui_themes()`, `get_gallery_ui_theme(*, identifier)`, `get_default_gallery_ui_theme()`, `get_backgrounds()`, `get_default_background()`, `get_doc_variants()`, `get_doc_variant(*, key)`, `resolve_doc_variants(...)`, `clear_config_cache()`.

### 4.4 Required Runtime Consumer Updates
1. [dj_design_system/views/decorators.py](../../../dj_design_system/views/decorators.py): Enforce `GallerySettings.enabled` at the top of `gallery_access_required`, raising `Http404` when `False` (and apply across all gallery and gallery REST API views).
2. [dj_design_system/services/navigation.py](../../../dj_design_system/services/navigation.py): Accept `(list, tuple)` for `nav_order` (line 413), implement `app_order` and slug pinning + `NodeType` grouping, read `AppSettings` / `DirectorySettings` (lines 221, 593), and fix `build_breadcrumbs` (line 762) to use promoted directory labels.
3. [dj_design_system/services/media.py](../../../dj_design_system/services/media.py): Accept both bare bundle `str` (`"main"`) and `(name, config)` tuples in `get_bundle_urls` (lines 63–65).
4. [dj_design_system/services/canvas_renderer.py](../../../dj_design_system/services/canvas_renderer.py): Apply `None` tombstones via `.pop(k, None)` in `build_html_attrs`, strip `None` in `_flatten_attrs`, and support `CanvasBackground` attribute access alongside [canvas.py](../../../dj_design_system/services/canvas.py) and [gallery_context.py](../../../dj_design_system/services/gallery_context.py).
5. [dj_design_system/services/registry.py](../../../dj_design_system/services/registry.py): Keep `flatten: FlattenStrategy | None = None` on resolved directories so label-only / `promote_to_app`-only entries inherit parent prefixes.

---

## 5. Validation Boundary & Collision-Free System Check Registry

- **`__post_init__` (minimal)**: Container normalisation (`FrozenMapping`, `tuple`), coercing bare `str` paths and raw dicts inside `Theme`/`DarkModeConfig`, rejecting `""` key in `AppSettings.directories`. Never raises on cross-field mismatches (e.g. `default_theme not in themes`), preserving layered `.replace()` calls and letting `manage.py check` report issues cleanly.
- **[dj_design_system/checks.py](../../../dj_design_system/checks.py)**: Inspects raw `settings.DJ_DESIGN_SYSTEM` before running the adapter so existing checks (`E001`/`E002` in `tests/test_checks.py`) keep passing cleanly. Preserves `check_gallery_settings` export.

| Check ID | Level | Condition |
|---|---|---|
| `E001`–`E003` | Error | Existing gallery `include_apps` / `exclude_apps` type & overlap checks. |
| `E004`–`E006` | Error | Reserved (PR #285): invalid prefix syntax (`^[a-z][a-z0-9_]*$`, no `__`), reserved `"dds"` whole-app prefix, duplicate effective app prefix across installed apps (evaluated post-merge). |
| `E007` | Error | Reserved (PR #286): `ContribAppConfig.requires` missing app. |
| `E008` | Error | Reserved (PR #288): `contrib.django_admin` installed after `django.contrib.admin`. |
| `E009` | Error | `settings.DJ_DESIGN_SYSTEM` is neither `DesignSystemSettings`, `dict` (`0.10.x`), nor `None`. |
| `E010` | Error | `AppConfig.design_system` is present and not `None`, but is not an `AppSettings` instance. |
| `E011` | Error | `apps["dj_design_system"]` attempts to override built-in naming invariants (`prefix`, `flatten`, `short_names`). |
| `E012` | Error | `Theme.value` is explicitly set and does not match its mapping key in `themes` or `ui_themes`. |
| `E013` | Error | `promote_to_app=True` root slug collides with an installed app label, another promoted directory, or a nested promoted parent/child. |
| `E020` | Error | Legacy `DJ_DESIGN_SYSTEM` dict contains new-style field names (e.g. `"name"`, `"gallery"`, `"canvas"`, `"apps"`). |
| `W001`–`W002` | Warning | Existing `include_apps`+`exclude_apps` redundancy and uninstalled app label warnings. |
| `W003` | Warning | Key in `DesignSystemSettings.apps` is not in `INSTALLED_APPS`. |
| `W004` | Warning | `default_theme`, `default_ui_theme`, or `default_background` slug is missing from its mapping (or mapping is empty). |
| `W005` | Warning | `Theme.canvas_background` or `DarkModeConfig.canvas_background` string slug is not in `CanvasSettings.backgrounds`. |
| `W006` | Warning | `AppSettings.themes` references a theme slug not in `DesignSystemSettings.themes` (or is empty `()`). |
| `W007` | Warning | Directory path in `AppSettings.directories` does not exist under the app's `components/` folder. |
| `W010` | Warning | `DJ_DESIGN_SYSTEM` uses deprecated legacy flat `dict` syntax (scheduled for removal in `1.0.0`). |
| `W011` | Warning | Deprecated `COMPONENT_NAMESPACES` key in use. |
| `W012` | Warning | Unknown key(s) in legacy `DJ_DESIGN_SYSTEM` dict (with `difflib` closest-match hint). |

---

## 6. Documentation Overhaul

### 6.1 Information Architecture
Create `docs/configuration.md` as the single configuration hub directly after Quick Start in [mkdocs.yml](../../../mkdocs.yml), eliminating duplicated tables across five pages and stale drift (`FlattenStrategy.TREE`, incorrect `is_staff=True` claim, lowercase `dj_design_system = {...}`, obsolete colon syntax):

```yaml
nav:
  - Home: index.md
  - Quick Start: quickstart.md
  - Configuration: configuration.md
  - Guides:
      - Components: components.md
      - Organising Apps & Folders: organisation.md
      - Gallery: gallery.md
      - Themes & Styling: themes.md
      - Template Tags: templatetags.md
      - Registry: registry.md
      - REST API: rest-api.md
      - Integration Testing: testing.md
  - API Reference:
      - api/index.md
      - Configuration & Settings: api/settings.md
      - Gallery Side-Car Config: api/gallery.md
      - Components & Slots: api/components.md
      - Parameters: api/parameters.md
  - Changelog: changelog.md
  - "Demo →": https://fukalite.github.io/dj-design-system/demo/
```

### 6.2 Four-Tier Progressive Disclosure & Page Ownership
1. **Tier 0 (`docs/quickstart.md`)**: 3-step zero-config install (`INSTALLED_APPS`, `urls.py`, first component); note automatic registration of `ComponentsStaticFinder` and `ComponentsTemplateLoader`, moving manual loader setup to `configuration.md`.
2. **Tier 1 (`docs/configuration.md`)**: `DesignSystemSettings` overview (`name`/assets/themes at root + `gallery`, `canvas`, `apps`), split-settings inheritance via `.replace(...)`, environment disabling via `GallerySettings(enabled=False)`, external asset URLs, system checks, and manual loader opt-in.
3. **Tier 2 (`docs/configuration.md` + `docs/organisation.md`)**: Devolved `AppConfig.design_system = AppSettings(...)`, the 4-tier override stack and additive render cascade, manual and app-delegated `nav_order` / `app_order`, a **Reusable & Contrib App Author Guide** (relying on `verbose_name`, shipping defaults, `extra_css`/`extra_js` consumer overrides), and the startup vs request-time `@override_settings` boundary (cross-linked in `docs/testing.md`).
4. **Tier 3 (`docs/api/settings.md` + `docs/configuration.md#migrating-from-dict-settings`)**: Replace the 294-line hand-written `docs/api/settings.md` with `mkdocstrings` targeting `dj_design_system.config` (using clean type aliases so `_UnsetType` stays readable) and replace orphan `docs/api-reference.md` with `docs/api/index.md`.

### 6.3 Cross-Page Holistic Rewrites
- `docs/gallery.md`: Delete the 13-row shadow `## Settings` table; update inline snippets to `*Settings`; fix stale Tier 2 CSS tokens (`--dds-brand-primary-color` -> `--dds-color-accent`) and wrong `GALLERY_CANVAS_EXTRA_BACKGROUNDS` schema.
- `docs/themes.md`: Scope strictly to theming/styling; move `APP_CSS`/`APP_JS`/`APP_CANVAS_HTML_ATTRS` to `configuration.md`; document the full theme availability cascade (`Meta.available_themes` > Project `apps[label].themes` > `AppConfig.design_system.themes` > Project `themes`).
- `docs/templatetags.md`: Fix lowercase `dj_design_system` dict snippets and duplicated `### Qualified Name` heading; document `app_label=` and `theme=` kwargs on `{% global_stylesheets %}` / `{% global_scripts %}`.
- `docs/organisation.md`: Add app-level configuration patterns (`AppConfig.design_system`) and fix `{% demo_components:button %}` -> `{% demo_components__button %}`.
- `docs/index.md`: Add Configuration to "Where to go next"; fix duplicate `StrParam` import, colon tag syntax, and `/gallery/` demo URL.
- `docs/testing.md` & `docs/registry.md`: Update `GALLERY_DOC_VARIANTS` / `COMPONENT_DIRECTORIES` references and document `@override_settings` with `.replace(...)` and startup-bound settings.

---

## 7. Deprecation, Versioning & Migration Tool

### 7.1 Release Roadmap (`v0.9.2` -> `v0.10.0` -> `v1.0.0`)
- **`v0.10.0` (Introduce + Soft Deprecation)**:
  - Ship Tracks 1–3: `dj_design_system/config.py`, `services/config.py`, `AppConfig.design_system`, PEP 562 lazy `__init__.py`, wired `GallerySettings.enabled` 404 guard, legacy dict compatibility adapter, `RemovedInDjDS10Warning(DeprecationWarning)`, system checks `E009`–`E020` and `W003`–`W012`, `manage.py migrate_dds_settings`, overhauled docs, and `example_project/` migration.
  - Keep [dj_design_system/settings.py](../../../dj_design_system/settings.py) (`dds_settings` proxy, legacy helper functions, and `BUILTIN_*` re-exports) as a read-through facade over `services/config.py` so devolved `AppConfig.design_system` settings reach legacy callers.
  - Emit `RemovedInDjDS10Warning` once per distinct legacy dict key-signature (never per request) plus system check `W010`.
  - Publish deprecation notices in GitHub Release notes (consumed by `docs_hooks/changelog.py`).
- **`v1.0.0` (Bundled Hard Removal — Track 4)**:
  - Drop flat `DJ_DESIGN_SYSTEM` dict adapter, `dds_settings` proxy, `BUILTIN_*` aliases, `RemovedInDjDS10Warning`, `COMPONENT_NAMESPACES` ([remove_namespaces_20260720](../../tracks/remove_namespaces_20260720/index.md)), and legacy gallery kwargs ([deprecate_legacy_gallery_kwargs_20260927](../../tracks/deprecate_legacy_gallery_kwargs_20260927/index.md)) together. Passing a `dict` raises `ImproperlyConfigured` (`E009`).

### 7.2 Legacy Compatibility Adapter Guarantees (`0.10.x`)
- Adapts all 29 legacy keys into `DesignSystemSettings`:
  - `None` mapping values (`COMPONENT_NAMESPACES: None`, `APP_CSS: None`, etc.) safely treated as `{}`.
  - Per-app fallback from `COMPONENT_NAMESPACES` only when an app is absent from `COMPONENT_DIRECTORIES`.
  - `GALLERY_CANVAS_BACKGROUNDS={}` clears built-ins; `GALLERY_CANVAS_EXTRA_BACKGROUNDS` alone merges over `DDS_DEFAULT_CANVAS_BACKGROUNDS`.
  - `GALLERY_CODEHILITE_STYLE=""` preserved (`dds_settings` facade returns `""` when `codehilite_style is None`).
  - `GALLERY_NAV_ORDER="alphabetical"` preserved verbatim.
  - `GALLERY_DOC_VARIANTS` retains disabled built-in `DocVariantConfig` entries (`show_in_docs=False`).
  - `APP_THEMES[app]` distinguishes `None` (all themes), `()` (none), and bare `str` (`"dark"`).
  - Pure or mixed dicts containing new-style keys (`{"name": ...}`, `{"gallery": ...}`) raise `ImproperlyConfigured` (`E020`).
  - Explicit empty legacy dict `DJ_DESIGN_SYSTEM = {}` emits `W010` / `RemovedInDjDS10Warning`; omitted `DJ_DESIGN_SYSTEM` emits zero warnings.

### 7.3 Migration Management Command (`manage.py migrate_dds_settings`)
- **Interface**:
  - Default (no flags): prints ruff-formatted `DesignSystemSettings(...)` and minimal imports to `stdout` (never mutates `settings.py` in place).
  - `--split-apps`: emits `AppConfig.design_system = AppSettings(...)` snippets for local project apps and keeps third-party apps in `DesignSystemSettings.apps`.
  - `--app <label>` (repeatable): emits snippet for specific app(s) only.
  - `--check`: CI gate exiting non-zero if `DJ_DESIGN_SYSTEM` is a legacy `dict`, `COMPONENT_NAMESPACES` is set, or any `# MANUAL:` unresolved expression exists.
  - `--no-format` / `--include-defaults`: disables `ruff format -` or includes default-valued fields.
- **Hybrid Introspection + AST Hints**:
  - Reads raw `settings.DJ_DESIGN_SYSTEM` through the runtime adapter so output is verified by `exec()`-equivalence golden tests in CI.
  - Best-effort AST scan of `DJANGO_SETTINGS_MODULE` detects `**base_settings.DJ_DESIGN_SYSTEM` unpacking (emits `.replace(...)` guidance), dynamic expressions / env vars, `BASE_DIR`-derived paths, and `lambda`/`functools.partial` callables, annotating each with `# MANUAL:` and warning whenever AST cannot locate the assignment.
- **Safe `--split-apps` Local App Classification**:
  - Classifies an app as local only when `app_label != "dj_design_system"`, not `django.*`, `Path(app_config.path).resolve().is_relative_to(project_root)`, and no intermediate path segment is in `{".venv", "venv", "env", "site-packages", "dist-packages", ".tox", ".nox", "node_modules"}`.
  - Emits `name = app_config.name` (preserving non-default `label`), checks both `type(app_config) is AppConfig` and `(Path(app_config.path) / "apps.py").exists()` so existing `default = False` `apps.py` files are never clobbered, and flags apps that already define `design_system`.
