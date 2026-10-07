# Implementation Plan: CSS Architecture, 3-Tier Design Tokens & TypeScript Pipeline

> **Subagent Strategy:** Refer to [`conductor/initiatives/gallery_rebuild/subagents.md`](../../initiatives/gallery_rebuild/subagents.md) for prompt templates and drift adaptation rules.

## Phase 1: 3-Tier Design Tokens & Every Layout Composition Layer
- [ ] **Orchestrator Pre-Dispatch Check:** Confirm token domain names and Every Layout primitive list against `conductor/code_styleguides/dds-components.md` (Sections 4–6)
- [ ] **Delegate to `dds-css-architect` (Template A):**
  - Write `tests/test_dds_tokens_and_layout.py` (Red Phase) verifying `@layer reset, tokens, global, composition, blocks, utilities;`, all Tier 1 `--_dds-*` and Tier 2 `--dds-*` tokens across all 6 domains, `.gallery-theme-dark`, `[data-surface]` re-aliasing (zero Tier 1 leaks), and all 11 Every Layout `<l-*>` / `.l-*` primitives
  - Implement `dj_design_system/static/dj_design_system/tokens.css` and `composition.css`, and prepend `@layer` / `@import` to `gallery.css` (Green Phase)
- [ ] **Delegate to `dds-reviewer` (Template D):** Audit `tokens.css`, `composition.css`, `gallery.css`, and `tests/test_dds_tokens_and_layout.py` against `dds-components.md`, `html-css.md`, and `python.md`, and run `just test` & `just check`
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: TypeScript Build Pipeline for Co-located Web Components
- [ ] **Delegate to `dds-ts-specialist` (Template C):**
  - Configure `tsconfig.json` and `just build-ts` to compile `dj_design_system/components/**/*.ts` into sibling gitignored `.js` files
  - Write `tests/test_ts_pipeline.py` verifying TypeScript compilation and `ComponentsStaticFinder` resolution of compiled `.js` assets
  - Update `justfile` and `.github/workflows/ci.yml` to run `just build-ts` before E2E/visual suites
- [ ] **Delegate to `dds-reviewer` (Template D):** Audit `tsconfig.json`, `justfile`, `.github/workflows/ci.yml`, and `tests/test_ts_pipeline.py`, and run `just test` & `just check`
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
