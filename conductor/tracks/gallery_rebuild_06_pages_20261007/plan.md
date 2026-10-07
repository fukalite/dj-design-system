# Implementation Plan: Gallery Page Composition, Legacy Asset Removal & Visual Baselines

> **Subagent Strategy:** Refer to [`conductor/initiatives/gallery_rebuild/subagents.md`](../../initiatives/gallery_rebuild/subagents.md) for prompt templates and drift adaptation rules.

## Phase 1: Page Template Composition & Legacy Asset Removal
- [ ] **Orchestrator Pre-Dispatch Check:** Inspect view context keys in `dj_design_system/views/` and map them to the `{% dds__* %}` components built in Tracks 3–5
- [ ] **Delegate to `dds-component-builder` (Template B adapted for page templates):** Rewrite `dj_design_system/templates/dj_design_system/gallery/*.html` and `canvas_widget.html` as thin compositions of `{% dds__* %}` components and `<l-*>` Every Layout primitives, injecting `component_registry.get_internal_media()` in `base.html`
- [ ] **Delegate to `dds-css-architect` (Template A):** Remove all legacy BEM rules from `dj_design_system/static/dj_design_system/gallery.css` and `gallery-toolbar.css` (and remove obsolete legacy JS files replaced by `<dds-*>` custom elements), leaving only the clean `@layer` imports
- [ ] **Delegate to `dds-reviewer` (Template D):** Verify zero BEM (`__` or `--`) remains across `dj_design_system/`, run `just build-ts`, `just test`, and `just check`
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: E2E, Accessibility & Visual Baseline Verification
- [ ] **Delegate to `dds-ts-specialist` (Template C):** Run Playwright E2E and `axe-core` accessibility suites (`just e2e`), updating any legacy selector references in E2E tests to match the new `<dds-*>` / `.dds-*` / `[data-surface]` DOM
- [ ] **Orchestrator Visual Baseline Update:** Regenerate visual regression baselines via `just update-visual-baselines` and verify `just visual` passes cleanly
- [ ] **Delegate to `dds-reviewer` (Template D):** Final audit of all modified templates, CSS, and E2E tests
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
