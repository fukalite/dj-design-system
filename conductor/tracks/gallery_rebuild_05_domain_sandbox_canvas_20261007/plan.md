# Implementation Plan: Built-in `domain` Collection — Sandbox, Controls & Canvas

## Phase 1: Sandbox Layout & Parameter Controls (`split_pane`, `sandbox_toolbar`, `params_form`)
- [ ] Write unit and DOM interaction tests for `split_pane`, `sandbox_toolbar`, and `params_form`
- [ ] Implement co-located `dj_design_system/components/domain/{split_pane,sandbox_toolbar,params_form}/` with `.py`, `.html`, `.css`, `.ts`, `gallery.py`, and `index.md`
- [ ] Compile TypeScript (`just build-ts`) and run `just test` and `just check`
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Isolated Canvas Widget (`canvas_widget`)
- [ ] Write unit and E2E tests for `canvas_widget` (`<dds-canvas-widget>`) covering iframe sizing, background/theme switching, parameter updates, and code drawer toggling
- [ ] Implement co-located `dj_design_system/components/domain/canvas_widget/` with `.py`, `.html`, `.css`, `.ts`, `gallery.py`, and `index.md`
- [ ] Compile TypeScript (`just build-ts`) and run `just test` and `just check`
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
