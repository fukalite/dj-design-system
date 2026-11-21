# Specification: v1.0.0 Legacy Settings Removal

Reference architecture: [Typed & Devolved Settings Design Document](../../initiatives/typed_settings/design.md) (§7.1).

## Overview
Execute the bundled `v1.0.0` breaking removal of the legacy flat `DJ_DESIGN_SYSTEM` dictionary compatibility layer, `dds_settings` proxy, `BUILTIN_*` default aliases, `RemovedInDjDS10Warning`, and `manage.py migrate_dds_settings` (coordinated with `remove_namespaces_20260720` and `deprecate_legacy_gallery_kwargs_20260927`).

## Functional Requirements
1. **Remove Legacy Compatibility Adapter & Proxy**:
   - Delete the legacy `dict` -> `DesignSystemSettings` adapter from `dj_design_system/services/config.py`.
   - Enforce `DesignSystemSettings | None` strictly in `get_config()` (raising `ImproperlyConfigured` for plain `dict`s) and system check `E009`.
   - Remove `DjangoDesignSystemSettings`, `dds_settings`, `DEFAULTS`, and `BUILTIN_*` legacy re-exports from `dj_design_system/settings.py` (keeping clean typed re-exports from `services/config.py` and `config.py`).
   - Remove deprecation checks `E020` and `W010`–`W012`, `RemovedInDjDS10Warning`, and `manage.py migrate_dds_settings` (documenting `v0.10.x` as the mandatory stepping-stone release).
2. **Migrate Remaining Internal Tests**:
   - Convert all remaining legacy `DJ_DESIGN_SYSTEM = {...}` overrides in `tests/` to `DesignSystemSettings` / `.replace(...)`.
3. **Update Documentation**:
   - Remove the `0.10.x` deprecation/migration section from `docs/configuration.md` and document `v0.10.x` -> `v1.0.0` in the `v1.0.0` GitHub Release notes.

## Non-Functional Requirements
- Zero references to `dds_settings`, `DEFAULTS`, `COMPONENT_NAMESPACES`, or `RemovedInDjDS10Warning` remain in `dj_design_system/`.
- `just check`, `just typecheck`, `just test`, and `just docs-build` pass cleanly.

## Acceptance Criteria
- Passing a plain `dict` as `DJ_DESIGN_SYSTEM` fails `manage.py check --tag dj_design_system` with `E009` and raises `ImproperlyConfigured` at runtime.
- Entire test suite and documentation build pass with zero legacy dict fallbacks.
