# Implementation Plan: Built-in `elements` Collection

> **Subagent Strategy:** Refer to [`conductor/initiatives/gallery_rebuild/subagents.md`](../../initiatives/gallery_rebuild/subagents.md) for prompt templates, parallel batching rules, and `[DRIFT & CONTEXT NOTES]` injection.

## Phase 1: Core Static Primitives (`icon`, `button`, `badge`, `notice`, `table`, `breadcrumb`, `form_field`)
- [x] **Orchestrator Pre-Dispatch Contract Lock:** Define exact parameter signatures and slot names for `icon`, `button`, `badge`, `notice`, `table`, `breadcrumb`, and `form_field` (since `button`, `notice`, and `breadcrumb` may compose `{% dds__icon %}`)
- [x] **Parallel Batch 1A — Delegate 4x `dds-component-builder` (Template B) concurrently:**
  - Subagent 1: `dj_design_system/components/elements/icon/` + `tests/components/test_icon.py`
  - Subagent 2: `dj_design_system/components/elements/badge/` + `tests/components/test_badge.py`
  - Subagent 3: `dj_design_system/components/elements/table/` + `tests/components/test_table.py`
  - Subagent 4: `dj_design_system/components/elements/form_field/` + `tests/components/test_form_field.py`
- [x] **Parallel Batch 1B (composing `dds__icon`) — Delegate 3x `dds-component-builder` (Template B) concurrently:**
  - Subagent 1: `dj_design_system/components/elements/button/` + `tests/components/test_button.py`
  - Subagent 2: `dj_design_system/components/elements/notice/` + `tests/components/test_notice.py`
  - Subagent 3: `dj_design_system/components/elements/breadcrumb/` + `tests/components/test_breadcrumb.py`
- [x] **Delegate to `dds-reviewer` (Template D):** Audit all 7 `elements/` directories and `tests/components/test_*.py` against `dds-components.md`, `python.md`, and `html-css.md`, and run `just test` & `just check`
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Interactive Element Primitives (`code_block`, `tabs`, `popout`, `popout_option`)
- [x] **Orchestrator Pre-Dispatch Contract Lock:** Lock the HTML `data-*` / `aria-*` hooks and custom event names (`dds:copy`, `dds:tab-change`, `dds:popout-select`) shared between `.html` and `.ts` for `code_block`, `tabs`, and `popout` / `popout_option`
- [x] **Parallel Batch 2A (Server Markup, CSS & Unit Tests) — Delegate 3x `dds-component-builder` (Template B) concurrently:**
  - Subagent 1: `dj_design_system/components/elements/code_block/` (`.py`, `.html`, `.css`, `gallery.py`, `index.md`) + `tests/components/test_code_block.py`
  - Subagent 2: `dj_design_system/components/elements/tabs/` (`.py`, `.html`, `.css`, `gallery.py`, `index.md`) + `tests/components/test_tabs.py`
  - Subagent 3: `dj_design_system/components/elements/popout/` and `popout_option/` (`.py`, `.html`, `.css`, `gallery.py`, `index.md`) + `tests/components/test_popout.py`
- [x] **Parallel Batch 2B (Light DOM Custom Elements in TS) — Delegate 3x `dds-ts-specialist` (Template C) concurrently:**
  - Subagent 1: `dj_design_system/components/elements/code_block/code_block.ts` (`<dds-code-block>`)
  - Subagent 2: `dj_design_system/components/elements/tabs/tabs.ts` (`<dds-tabs>`)
  - Subagent 3: `dj_design_system/components/elements/popout/popout.ts` (`<dds-popout>`)
- [x] **Delegate to `dds-reviewer` (Template D):** Run `just build-ts`, audit all Phase 2 files against `dds-components.md` and `javascript.md`, and run `just test` & `just check`
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)
