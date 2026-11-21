# Implementation Plan: Track 2 — Compatibility Adapter, Migration CLI & Example Project

## Phase 1: Deprecation Warning Hierarchy & Legacy Adapter
- [ ] Task: Red Phase — Write exhaustive adapter tests (`tests/test_config_adapter.py`) covering all 29 legacy keys, `None` mapping values, `COMPONENT_NAMESPACES` per-app fallback, `GALLERY_CANVAS_BACKGROUNDS={}`, `GALLERY_CANVAS_EXTRA_BACKGROUNDS`, `GALLERY_CODEHILITE_STYLE=""`, `GALLERY_NAV_ORDER="alphabetical"`, `GALLERY_DOC_VARIANTS` disabled built-ins, `APP_THEMES` `None`/`()`/bare `str`, new-style keys in dicts (`E020`), in-place dict mutation safety, and single-emission `RemovedInDjDS10Warning` (using `warnings.catch_warnings(record=True)`).
- [ ] Task: Green Phase — Implement `RemovedInDjDS10Warning`, legacy dict adapter in `services/config.py`, `E020` / `W010`–`W012` checks in `checks.py`, and the read-through `dj_design_system/settings.py` facade.
- [ ] Task: Refactor Phase — Upgrade existing `COMPONENT_NAMESPACES` and `gallery_*_kwargs` warnings to `RemovedInDjDS10Warning`; confirm all existing test files (`tests/test_settings.py`, `tests/test_checks.py`, `tests/test_registry.py`) pass unchanged.
- [ ] Task: Quality Check (`just check`, `just typecheck`, `just test`)
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: `manage.py migrate_dds_settings` Management Command
- [ ] Task: Red Phase — Write unit and `exec()`-equivalence golden tests (`tests/test_migrate_dds_settings.py`) covering default stdout generation, `--split-apps` local vs third-party classification (including existing `apps.py` with `default = False`, missing `apps.py`, existing `design_system`, `.venv`/`dj_design_system` exclusions), `--app`, `--check`, `--no-format`, `--include-defaults`, AST `# MANUAL:` hints (`**unpacking`, env vars, `BASE_DIR`, `lambda`/`partial`), and missing `ruff` fallback.
- [ ] Task: Green Phase — Implement `dj_design_system/management/commands/migrate_dds_settings.py` delegating formatting/AST/classification logic to a dedicated service module per `layered-architecture.md`.
- [ ] Task: Refactor Phase — Verify zero side-effects in default mode and clean error messages.
- [ ] Task: Quality Check (`just check`, `just typecheck`, `just test`)
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Migrate `example_project/`
- [ ] Task: Red Phase — Add check/smoke assertions verifying `example_project` passes `manage.py check --tag dj_design_system` and `migrate_dds_settings --check` cleanly.
- [ ] Task: Green Phase — Convert `example_project/settings.py`, `settings_dds.py`, and `settings_dds_gallery.py` to `DesignSystemSettings` + `.replace(...)`; move app-specific config to `example_project/demo_components/apps.py` and `example_project/broken_components/apps.py`; fix `canvas_background="dark-grey"`.
- [ ] Task: Refactor Phase — Run `just test-demo` and E2E gallery checks against `example_project`.
- [ ] Task: Quality Check (`just check`, `just typecheck`, `just test`)
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
