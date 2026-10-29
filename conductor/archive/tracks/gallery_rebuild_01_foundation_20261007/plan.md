# Implementation Plan: Visual Regression Harness & `dds` Component Foundation

## Phase 1: Styleguides, Visual Harness & Component Foundation
- [x] Author `conductor/code_styleguides/dds-components.md` and `conductor/code_styleguides/example-project.md`
- [x] Assimilate visual regression harness (`dj_design_system/testing/visual.py`, `plugins.py`, `tests/e2e/visual/`, `justfile`, `.github/workflows/ci.yml`)
- [x] Promote `dj_design_system/components.py` to `dj_design_system/components/` (`base.py`, `elements/`, `domain/`)
- [x] Configure `BUILTIN_APP_LABEL = "dj_design_system"`, `BUILTIN_PREFIX = "dds"`, and `FlattenStrategy.ALL` in `dj_design_system/services/component.py`
- [x] Add `is_internal` to `ComponentInfo` and `get_internal_media()` + consumer `dds__*` shadowing to `ComponentRegistry`
- [x] Add `ensure_component_loaders_and_finders()` in `dj_design_system/services/media.py` and invoke in `DjangoDesignSystemConfig.ready()`
- [x] Implement `dj_design_system/services/visibility.py`, `GALLERY_SHOW_DDS_COMPONENTS`, `GALLERY_EXCLUDE_APPS`, and `example_project/settings_dds.py`
- [x] Verify unit tests (`test_builtin_components.py`, `test_internal_components.py`, `test_gallery_visibility.py`, `test_testing_visual.py`, `test_visual_config.py`, `test_visual_prune.py`), `ruff`, `djlint`, and `mypy`
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)
