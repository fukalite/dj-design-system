# Specification: Typed Schema, Import-Safety & 4-Tier Resolution

Reference architecture: [Typed & Devolved Settings Design Document](../../initiatives/typed_settings/design.md).

## Overview
Establish the import-safe configuration schema (`dj_design_system/config.py`), the 4-tier project/app resolution service (`dj_design_system/services/config.py`), devolved `AppConfig.design_system = AppSettings(...)`, wired `GallerySettings.enabled` 404 enforcement, manual and app-delegated navigation ordering (`app_order` + `nav_order`), runtime consumer updates, and collision-free Django system checks.

## Functional Requirements
1. **Import-Safety Boundary** (§2 of design doc):
   - Convert `dj_design_system/__init__.py` to PEP 562 lazy `__getattr__` (caching into `globals()[name]`) and `__dir__()`.
   - Keep `constants.py` -> `types.py` -> `config.py` strictly stdlib-only with zero `django.*` imports.
   - Make `UserParam` resolve `settings.AUTH_USER_MODEL` lazily via zero-arg callable support in `ModelParam._resolve_model()`.
2. **Typed Settings Schema** (§3 of design doc):
   - Implement `FrozenMapping`, `_UnsetType.UNSET`, `HtmlAttrsDict`, `WebpackBundleSpec`, `NavOrderSpec`, `CanvasBackground`, frozen `Theme` and `DarkModeConfig`, `DocVariantConfig`, `DirectorySettings`, `AppSettings` (including `extra_css`, `extra_js`, `order`, `nav_order`, `prefix`, `flatten`, `short_names`), `CanvasSettings`, `GallerySettings` (including `enabled`, `app_order`, `nav_order`), and `DesignSystemSettings`.
   - Provide `.replace(**kwargs)` on all five `*Settings` classes.
   - Export `DDS_DEFAULT_THEMES`, `DDS_DEFAULT_UI_THEMES`, `DDS_DEFAULT_CANVAS_BACKGROUNDS`, `DDS_DEFAULT_DOC_VARIANTS`, and `DDS_DEFAULT_NAV_ORDER`.
   - Dogfood `design_system = AppSettings(prefix="dds", flatten=FlattenStrategy.ALL, short_names=False)` on `DjangoDesignSystemConfig`.
3. **4-Tier Resolution, Caching & Signals** (§4 of design doc):
   - Implement `dj_design_system/services/config.py` with keyword-only typed accessors, internal `_ResolvedAppSettings` / `_ResolvedDirectorySettings`, `apps.apps_ready` startup gate, single-slot identity cache for immutable `DesignSystemSettings`, `LookupError`-safe resolution for synthetic app labels, and `django.core.signals.setting_changed` invalidation for both `"DJ_DESIGN_SYSTEM"` and `"INSTALLED_APPS"` (also clearing `navigation_service` caches).
4. **Runtime Consumer Updates & New Capabilities** (§4.4 of design doc):
   - Wire `GallerySettings.enabled` into `gallery_access_required` (`views/decorators.py`), returning `Http404` when `False` across gallery and gallery REST API views.
   - Update `navigation.py` for `(list, tuple)` `nav_order`, `app_order`, slug pinning + `NodeType` grouping, app/directory delegation, and promoted breadcrumb labels.
   - Update `media.py` (`get_bundle_urls`), `canvas_renderer.py` (`None` tombstones + `CanvasBackground` + layered merge order), `canvas.py`, `gallery_context.py`, and `registry.py` (presentation-only directory inheritance + `short_names`).
5. **Collision-Free System Checks** (§5 of design doc):
   - Implement `E009`–`E013` and `W003`–`W007` in `dj_design_system/checks.py`, preserving `E001`–`E003`, `W001`–`W002`, and reserving `E004`–`E008` for PRs #285–#288.

## Non-Functional Requirements
- Subprocess test with `DJANGO_SETTINGS_MODULE` unset confirms `"django" not in sys.modules` after importing `dj_design_system.config`, `types`, and `constants`.
- `copy.deepcopy`, `pickle`, and `dataclasses.asdict` succeed on all `*Settings` objects.
- `ruff check`, `ruff format --check`, `mypy dj_design_system/`, and `just test` pass with zero regressions.

## Acceptance Criteria
- `DesignSystemSettings` and `AppConfig.design_system = AppSettings(...)` resolve across all 4 tiers and additive render cascades as specified in `design.md`.
- `GallerySettings(enabled=False)` returns 404 on gallery and gallery REST API routes regardless of `is_public` or user permissions.
- Manual `app_order` and app/directory-level `nav_order` (slug pinning, `NodeType` buckets, `"alphabetical"`, numeric `order` fallback) pass unit and integration tests.
- All new system checks emit expected IDs without clashing with existing checks or PRs #285–#288.
