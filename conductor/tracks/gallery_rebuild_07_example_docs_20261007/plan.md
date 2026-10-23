# Implementation Plan: `example_project/` Rework & Consumer Shadowing Showcase

> **Subagent Strategy:** Refer to [`conductor/initiatives/gallery_rebuild/subagents.md`](../../initiatives/gallery_rebuild/subagents.md) for prompt templates and drift adaptation rules.

## Phase 1: `example_project/` Refactor & Customization Showcase
- [ ] **Orchestrator Pre-Dispatch Audit:** List all components in `example_project/` and map required pedagogical feature coverage per `conductor/code_styleguides/example-project.md`
- [ ] **Parallel Batch 1A — Delegate 2x `dds-component-builder` concurrently:**
  - Subagent 1: Audit and refactor `example_project/demo_components/` (`components/`, `gallery.py`, `index.md`) to strictly follow `conductor/code_styleguides/example-project.md`
  - Subagent 2: Audit and refactor `example_project/demo_single/` and add a consumer `dds__*` component shadowing + Tier 2 `--dds-*` token theming showcase and test in `tests/test_example_project_showcase.py`
- [ ] **Delegate to `dds-reviewer` (Template D):** Audit `example_project/` against `conductor/code_styleguides/example-project.md`, `python.md`, and `html-css.md`, and run `just test` & `just check`
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: User-Facing Documentation & Initiative Closure
- [ ] **Orchestrator / Documentation Subagent:** Author user-facing documentation in `docs/` covering `GALLERY_SHOW_DDS_COMPONENTS`, `GALLERY_EXCLUDE_APPS`, Tier 2 `--dds-*` token theming, Every Layout `<l-*>` primitives, and `dds__*` component shadowing
- [ ] **Delegate to `dds-reviewer` (Template D):** Run full test and lint verification (`just test`, `just check`, `mypy`) and verify all documentation links
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
