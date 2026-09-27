# Specification: Remove Deprecated Legacy Gallery Kwargs

## Overview
With the introduction of explicit per-component `GalleryConfig` and named `Variant` definitions (track `gallery_config_revamp_20260801`), legacy ad-hoc gallery configurations have been formally deprecated with runtime `DeprecationWarning`s. This track manages the complete removal of legacy fallbacks and obsolete accessors in a future breaking release once downstream components and users have migrated to `GalleryConfig`.

## Deprecated Items Targeted for Removal
1. **Module-level `basic_kwargs` and `maximal_kwargs` Exports**:
   - Remove fallback synthesis in `ComponentInfo.gallery_config` that auto-constructs `GalleryConfig` from module-level `basic_kwargs` or `maximal_kwargs`.
   - Require components to export `config = GalleryConfig(...)` in `gallery.py` or `<name>_gallery.py`.

2. **Legacy Accessor Properties**:
   - Remove `ComponentInfo.gallery_basic_kwargs` and `ComponentInfo.gallery_maximal_kwargs`.
   - Remove internal cached tuple property `ComponentInfo._gallery_kwargs`.
   - Direct all callers to inspect `info.gallery_config.get_variant('basic')` or `info.gallery_config.get_variant('maximal')`.

3. **Deprecation Warnings**:
   - Clean up emitted `DeprecationWarning` calls once legacy paths and properties are removed.

## Migration & User Guidance
- **Documentation**: Upgrade guide with before/after examples is documented in `docs/gallery.md` under [Upgrading Legacy Gallery Configurations](docs/gallery.md#upgrading-legacy-gallery-configurations).
- **Changelog & Patch Notes**: Deprecations and migration notes are recorded under `[Unreleased]` in `CHANGELOG.md`.
- **Automated Tooling**: Automated migration command `python manage.py migrate_gallery_configs` is provided to upgrade component gallery files seamlessly before removal.

## Acceptance Criteria
- Module-level `basic_kwargs` and `maximal_kwargs` are no longer recognized as fallback gallery configurations.
- Accessing `gallery_basic_kwargs` or `gallery_maximal_kwargs` on `ComponentInfo` raises `AttributeError`.
- All tests and callers pass cleanly using `info.gallery_config`.
