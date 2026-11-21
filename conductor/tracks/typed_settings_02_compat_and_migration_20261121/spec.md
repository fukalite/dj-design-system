# Specification: Compatibility Adapter, Migration CLI & Example Project

Reference architecture: [Typed & Devolved Settings Design Document](../../initiatives/typed_settings/design.md).

## Overview
Deliver a zero-breakage `v0.10.0` upgrade experience for projects using legacy flat `DJ_DESIGN_SYSTEM` dictionaries: a complete 29-key compatibility adapter, once-per-signature `RemovedInDjDS10Warning`, legacy deprecation system checks (`E020`, `W010`–`W012`), a read-through `dj_design_system/settings.py` facade, the `manage.py migrate_dds_settings` management command, and full migration of `example_project/` to `DesignSystemSettings` and `AppConfig.design_system`.

## Functional Requirements
1. **Deprecation Warning Hierarchy** (§7.1 of design doc):
   - Add `DjDesignSystemDeprecationWarning(DeprecationWarning)` and `RemovedInDjDS10Warning(DjDesignSystemDeprecationWarning)` in `dj_design_system/exceptions.py` (or `dj_design_system/deprecations.py`).
   - Emit `RemovedInDjDS10Warning` at most once per distinct legacy dict key-signature (reset on `setting_changed`), never per request.
   - Upgrade existing `COMPONENT_NAMESPACES` and `gallery_*_kwargs` deprecation warnings to `RemovedInDjDS10Warning`.
2. **Legacy Compatibility Adapter & Facade** (§7.2 of design doc):
   - Adapt all 29 legacy `DJ_DESIGN_SYSTEM` dict keys into `DesignSystemSettings`, preserving all edge-case coercions (`None` mapping values, per-app `COMPONENT_NAMESPACES` fallback, `GALLERY_CANVAS_BACKGROUNDS={}` vs `GALLERY_CANVAS_EXTRA_BACKGROUNDS`, `GALLERY_CODEHILITE_STYLE=""`, `GALLERY_NAV_ORDER="alphabetical"`, disabled built-in `DocVariantConfig` retention, `APP_THEMES` `None` vs `()` vs bare `str`, and `DJ_DESIGN_SYSTEM = {}`).
   - Raise `ImproperlyConfigured` (`E020`) on any legacy dict containing new-style field names (`"name"`, `"gallery"`, `"canvas"`, `"apps"`).
   - Keep `dj_design_system/settings.py` (`dds_settings`, legacy helper functions, `BUILTIN_CANVAS_BACKGROUNDS`, `BUILTIN_DOC_VARIANTS`) as a read-through facade over `services/config.py` so legacy callers see devolved `AppConfig.design_system` settings.
   - Add deprecation system checks `E020` and `W010`–`W012` (with `difflib` closest-match hints for unknown keys).
3. **Migration Command (`manage.py migrate_dds_settings`)** (§7.3 of design doc):
   - Default mode prints ruff-formatted `DesignSystemSettings(...)` + minimal imports to `stdout` without mutating `settings.py`.
   - Support `--split-apps`, `--app <label>` (repeatable), `--check` (CI gate), `--no-format`, and `--include-defaults`.
   - Implement best-effort AST inspection of `DJANGO_SETTINGS_MODULE` to attach `# MANUAL:` annotations for `**unpacking` (with `.replace(...)` hint), dynamic expressions / env vars, `BASE_DIR`-derived paths, and `lambda`/`functools.partial` callables, plus a warning when AST cannot locate the assignment.
   - Implement safe `--split-apps` local vs third-party app classification checking `BASE_DIR` containment, excluded directory names, `app_label != "dj_design_system"`, non-`django.*`, `app_config.name` + non-default `label`, `(app_path / "apps.py").exists()`, and existing `design_system` attributes.
4. **Example Project Migration**:
   - Migrate `example_project/settings.py`, `example_project/settings_dds.py`, and `example_project/settings_dds_gallery.py` to `DesignSystemSettings` + `.replace(...)`.
   - Devolve `demo_components` and `broken_components` app settings onto their `AppConfig.design_system = AppSettings(...)` subclasses.
   - Fix the pre-existing `canvas_background="dark"` typo in `example_project/settings.py` (`"dark-grey"`).

## Non-Functional Requirements
- `exec()`-equivalence golden tests verify generated `migrate_dds_settings` Python output executes cleanly and produces a `DesignSystemSettings` equal to the runtime adapter result.
- Works gracefully when `ruff` is not on `PATH` (clean fallback to unformatted output).
- `just check`, `just typecheck`, and `just test` pass with zero warnings from `example_project`.

## Acceptance Criteria
- All 29 legacy keys pass round-trip equivalence tests through the adapter and `dds_settings` facade.
- `manage.py check --tag dj_design_system` emits zero errors/warnings on the migrated `example_project`.
- `manage.py migrate_dds_settings --check` fails on legacy dicts and passes on `example_project`.
