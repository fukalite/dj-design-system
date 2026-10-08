# Implementation Plan: Built-in `domain` Collection — Sandbox, Controls & Canvas

> **Subagent Strategy:** Refer to [`conductor/initiatives/gallery_rebuild/subagents.md`](../../initiatives/gallery_rebuild/subagents.md) for prompt templates, parallel batching rules, and `[DRIFT & CONTEXT NOTES]` injection.

## Phase 1: Sandbox Layout & Parameter Controls (`split_pane`, `sandbox_toolbar`, `params_form`)
- [x] **Orchestrator Pre-Dispatch Contract Lock:** Define DOM attributes and custom events (`dds:split-resize`, `dds:viewport-change`, `dds:bg-change`, `dds:params-change`) for `split_pane`, `sandbox_toolbar`, and `params_form`
- [x] **Parallel Batch 1A (Server Markup, CSS & Unit Tests) — Delegate 3x `dds-component-builder` (Template B) concurrently:**
  - Subagent 1: `dj_design_system/components/domain/split_pane/` + `tests/components/test_split_pane.py`
  - Subagent 2: `dj_design_system/components/domain/sandbox_toolbar/` + `tests/components/test_sandbox_toolbar.py`
  - Subagent 3: `dj_design_system/components/domain/params_form/` + `tests/components/test_params_form.py`
- [x] **Parallel Batch 1B (Light DOM Custom Elements in TS) — Delegate 2x `dds-ts-specialist` (Template C) concurrently:**
  - Subagent 1: `split_pane/split_pane.ts` (`<dds-split-pane>`)
  - Subagent 2: `params_form/params_form.ts` (`<dds-params-form>`)
- [x] **Delegate to `dds-reviewer` (Template D):** Run `just build-ts`, audit Phase 1 files against `dds-components.md`, `python.md`, `html-css.md`, and `javascript.md`, and run `just test` & `just check`
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Isolated Canvas Widget (`canvas_widget`)
- [x] **Orchestrator Pre-Dispatch Contract Lock:** Lock iframe `postMessage` resize protocol, toolbar coordination events, and code drawer toggle hooks for `canvas_widget`
- [ ] **Delegate to `dds-component-builder` (Template B):** Implement `dj_design_system/components/domain/canvas_widget/` (`.py`, `.html`, `.css`, `gallery.py`, `index.md`) + `tests/components/test_canvas_widget.py`
- [ ] **Delegate to `dds-ts-specialist` (Template C):** Implement `dj_design_system/components/domain/canvas_widget/canvas_widget.ts` (`<dds-canvas-widget>`) and E2E/DOM resize & toolbar interaction tests
- [ ] **Delegate to `dds-reviewer` (Template D):** Run `just build-ts`, audit `canvas_widget` against all styleguides, and run `just test` & `just check`
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
