# Implementation Plan: Track 1 — Typed Schema, Import-Safety & 4-Tier Resolution

## Phase 1: Import-Safety Hardening
- [x] Task: Red Phase — Add subprocess import-isolation test (`DJANGO_SETTINGS_MODULE` unset, asserting `"django" not in sys.modules` after importing `dj_design_system.config`, `types`, `constants`) and lazy `UserParam` test with custom `AUTH_USER_MODEL`.
- [x] Task: Green Phase — Convert `dj_design_system/__init__.py` to PEP 562 lazy `__getattr__` + `__dir__()`; add callable `Meta.model` support in `ModelParam._resolve_model()` and update `UserParam.Meta.model` to a lazy callable.
- [x] Task: Refactor Phase — Verify `tests/test_public_api.py` and `unittest.mock.patch` behaviour against lazy exports.
- [x] Task: Quality Check (`just check`, `just typecheck`, `just test`)
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Public `*Settings` Schema (`dj_design_system/config.py`)
- [x] Task: Red Phase — Write unit tests for `FrozenMapping` (`deepcopy`, `pickle`, `asdict`, equality), `UNSET` narrowing, `.replace()` on all five `*Settings` classes, `AppSettings.directories` rejecting `""`, `CanvasBackground`, frozen `Theme`/`DarkModeConfig`, `DDS_DEFAULT_*` immutability, and `AppSettings` `extra_css`/`extra_js`.
- [x] Task: Green Phase — Implement `dj_design_system/config.py` (stdlib + `constants.py` + `types.py` only) and update `types.py` so `Theme`, `DarkModeConfig`, and `DocVariantConfig` are deeply immutable and coerce raw dicts cleanly.
- [x] Task: Refactor Phase — Verify clean type aliases (`HtmlAttrsDict`, `WebpackBundleSpec`, `NavOrderSpec`) for `mypy` and `mkdocstrings`.
- [x] Task: Quality Check (`just check`, `just typecheck`, `just test`)
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: 4-Tier Resolution Service & Caching (`dj_design_system/services/config.py`)
- [x] Task: Red Phase — Write exhaustive service tests covering 4-tier inheritance (`nav_order`, `themes`), app-only 3-tier merge (`label`, `order`, `prefix`, `flatten`, `short_names`, `directories`), `css` replace + `extra_css` append deduplication, `canvas_html_attrs` merge and `None` tombstones, `apps.apps_ready` gating, uninstalled app `LookupError` safety, and `setting_changed` invalidation for both `DJ_DESIGN_SYSTEM` and `INSTALLED_APPS`.
- [x] Task: Green Phase — Implement `dj_design_system/services/config.py` with keyword-only typed accessors, internal `_ResolvedAppSettings` / `_ResolvedDirectorySettings`, single-slot identity cache, signal registration in `DjangoDesignSystemConfig.ready()`, and dogfood `design_system` on `DjangoDesignSystemConfig`.
- [x] Task: Refactor Phase — Audit against `layered-architecture.md` (zero mutable dict globals, keyword-only signatures, precise types).
- [x] Task: Quality Check (`just check`, `just typecheck`, `just test`)
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 4: Runtime Consumers, `GallerySettings.enabled` & Manual `nav_order`
- [x] Task: Red Phase — Write failing tests for `GallerySettings(enabled=False)` returning 404 across gallery and REST API views, `GallerySettings.app_order`, app/directory `nav_order` (pinned slugs, mixed `NodeType` buckets, `"alphabetical"`, numeric `order` tie-breaking), `media.py` string/tuple bundle specs, `canvas_renderer.py` tombstone stripping and `CanvasBackground`, `registry.py` presentation-only directory fallthrough + `short_names=False`, and promoted breadcrumb labels.
- [x] Task: Green Phase — Update `views/decorators.py`, `services/navigation.py`, `services/media.py`, `services/canvas_renderer.py`, `services/canvas.py`, `services/gallery_context.py`, and `services/registry.py`.
- [x] Task: Refactor Phase — Ensure zero regression across existing gallery, canvas, navigation, and registry test suites.
- [x] Task: Quality Check (`just check`, `just typecheck`, `just test`)
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 5: Collision-Free Django System Checks
- [x] Task: Red Phase — Write tests for `E009`–`E013` and `W003`–`W007` plus non-regression tests for `E001`–`E003`, `W001`–`W002`.
- [x] Task: Green Phase — Add typed configuration checks to `dj_design_system/checks.py` inspecting raw settings safely before resolution.
- [x] Task: Refactor Phase — Verify check messages and actionable hints are consistent across all IDs.
- [x] Task: Quality Check (`just check`, `just typecheck`, `just test`)
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)
