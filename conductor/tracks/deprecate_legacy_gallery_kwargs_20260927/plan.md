# Implementation Plan: Remove Deprecated Legacy Gallery Kwargs

## Phase 1: Code Removal
- [ ] Task: Remove fallback synthesis in `ComponentInfo.gallery_config`
  - [ ] Write failing unit test confirming that omitting `config` no longer synthesizes from `basic_kwargs` / `maximal_kwargs`.
  - [ ] Remove legacy fallback and deprecation warning in `dj_design_system/data.py`.
- [ ] Task: Remove `ComponentInfo.gallery_basic_kwargs` and `ComponentInfo.gallery_maximal_kwargs`
  - [ ] Write failing unit tests confirming removal of legacy properties.
  - [ ] Remove `gallery_basic_kwargs`, `gallery_maximal_kwargs`, and `_gallery_kwargs` from `dj_design_system/data.py`.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Test Suite & Documentation Cleanup
- [ ] Task: Update legacy callers in tests
  - [ ] Refactor tests still accessing `gallery_basic_kwargs` or `gallery_maximal_kwargs` to access `gallery_config`.
- [ ] Task: Documentation update
  - [ ] Verify documentation reflects removal of legacy gallery kwargs.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
