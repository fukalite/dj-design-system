# Registry API

## Overview

The component registry is a module-level singleton at `dj_design_system.component_registry`. It stores immutable `ComponentInfo` metadata for every discovered component and provides lookup and template tag registration methods.

```python
from dj_design_system import component_registry
```

## Discovery

Discovery runs automatically in `DjangoDesignSystemConfig.ready()`. For each installed Django app, the registry imports `{app}.components` and walks any sub-packages, registering all concrete `TagComponent` and `BlockComponent` subclasses.

### Discovery Rules

- Looks for `{app}.components` as a module or package.
- Recursively walks sub-packages within `components/` that contain an `__init__.py`.
- Registers concrete `TagComponent` and `BlockComponent` subclasses defined in each inspected module (`cls.__module__ == module.__name__`).
- Skips classes with `Meta.abstract = True` and classes imported from other modules.
- Resolves startup-bound `AppSettings.{prefix, flatten, short_names}` and `DirectorySettings.{prefix, flatten}` from `dj_design_system.services.config` and bakes them onto each frozen `ComponentInfo`.

## `ComponentInfo`

Each discovered component is stored as a frozen `ComponentInfo` dataclass.

### Fields

| Field | Type | Description |
| --- | --- | --- |
| `component_class` | `type` | The component class itself |
| `name` | `str` | Short name (auto-derived or from `Meta.name`) |
| `app_label` | `str` | Django app label where the component was discovered |
| `relative_path` | `str` | Dotted directory path within `components/` (e.g. `"cards.layouts"`) |
| `namespace_prefix` | `str \| None` | Resolved tag prefix from `AppSettings` / `DirectorySettings` |
| `namespace_remaining_parts` | `tuple[str, ...] \| None` | Remaining path segments after the matched prefix |
| `flatten_strategy` | `FlattenStrategy` | Applied flattening strategy (`NONE`, `LEAF`, `ALL`) |
| `qualified_only` | `bool` | `True` when `AppSettings(short_names=False)` disables short-name registration |

### Properties

| Property | Type | Description |
| --- | --- | --- |
| `qualified_name` | `str` | Fully qualified tag name (e.g. `myapp__cards__hero` or `ui__hero`) |
| `is_builtin` | `bool` | `True` for built-in `dj_design_system` components |
| `available_themes` | `list[str]` | Effective theme slugs resolved via the component/app/project cascade |
| `media` | `ComponentMedia` | Merged co-located and `Media`-declared CSS/JS static paths |
| `template_name` | `str \| None` | Bound Django template name, or `None` when using `template_format_str` |
| `tag_type` | `TagType` | `TagType.TAG` or `TagType.BLOCK` (raises `InvalidTagType` on direct `BaseComponent`) |

## Lookup Methods

- **`component_registry.list_all() -> list[ComponentInfo]`** — return all discovered components.
- **`component_registry.list_ordered(app_label: str | None = None) -> list[ComponentInfo]`** — return components ordered with built-in `dj_design_system` first so consumer `dds__*` overrides always win regardless of `INSTALLED_APPS` order.
- **`component_registry.list_by_app(app_label: str) -> list[ComponentInfo]`** — return all components belonging to `app_label`.
- **`component_registry.get_by_name(name: str, app_label: str | None = None) -> ComponentInfo`** — look up a component by short name. Without `app_label`, skips built-in and `qualified_only` components (use `app_label=...` or `dj_design_system.services.canvas.resolve_component()` for those). Raises `ComponentDoesNotExist` or `MultipleComponentsFound`.
- **`component_registry.get_info(component_class: type) -> ComponentInfo`** — look up `ComponentInfo` by class, raising `ComponentDoesNotExist` if unregistered.

## Template Tag Registration

```python
component_registry.register_templatetags(library, app_label=None)
```

Registers every component's `qualified_name` on `library`, plus short `name` tags for components where `not info.is_builtin and not info.qualified_only`. See [Template Tags](templatetags.md).

## Exceptions

Importable from `dj_design_system.exceptions`:

| Exception | When |
| --- | --- |
| `ComponentDoesNotExist` | `get_by_name()` or `get_info()` finds no match |
| `MultipleComponentsFound` | `get_by_name()` finds multiple matching components across apps |
| `InvalidTagType` | Direct `BaseComponent` subclass lacks `TagComponent` / `BlockComponent` base |
