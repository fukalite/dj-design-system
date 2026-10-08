# Implementation Plan: Built-in `domain` Collection — Shell, Navigation & Docs

> **Subagent Strategy:** Refer to [`conductor/initiatives/gallery_rebuild/subagents.md`](../../initiatives/gallery_rebuild/subagents.md) for prompt templates, parallel batching rules, and `[DRIFT & CONTEXT NOTES]` injection.

## Phase 1: Shell & Navigation Components (`gallery_shell`, `toolbar`, `sidebar`, `nav_tree`, `search_box`, `theme_select`, `folder_listing`)
- [x] **Orchestrator Pre-Dispatch Contract Lock:** Define exact parameter/slot contracts and custom events (`dds:nav-toggle`, `dds:theme-change`, `dds:search-select`) for `nav_tree`, `search_box`, `theme_select`, `folder_listing`, `sidebar`, `toolbar`, and `gallery_shell`
- [x] **Parallel Batch 1A (Leaf Domain Navigation Components) — Delegate 4x `dds-component-builder` (Template B) concurrently:**
  - Subagent 1: `dj_design_system/components/domain/nav_tree/` + `tests/components/test_nav_tree.py`
  - Subagent 2: `dj_design_system/components/domain/search_box/` + `tests/components/test_search_box.py`
  - Subagent 3: `dj_design_system/components/domain/theme_select/` + `tests/components/test_theme_select.py`
  - Subagent 4: `dj_design_system/components/domain/folder_listing/` + `tests/components/test_folder_listing.py`
- [x] **Parallel Batch 1B (Composite Shell Components) — Delegate 3x `dds-component-builder` (Template B) concurrently:**
  - Subagent 1: `dj_design_system/components/domain/sidebar/` + `tests/components/test_sidebar.py`
  - Subagent 2: `dj_design_system/components/domain/toolbar/` + `tests/components/test_toolbar.py`
  - Subagent 3: `dj_design_system/components/domain/gallery_shell/` + `tests/components/test_gallery_shell.py`
- [x] **Parallel Batch 1C (Light DOM Custom Elements in TS) — Delegate 4x `dds-ts-specialist` (Template C) concurrently:**
  - Subagent 1: `nav_tree/nav_tree.ts` (`<dds-nav-tree>`)
  - Subagent 2: `search_box/search_box.ts` (`<dds-search-box>`)
  - Subagent 3: `theme_select/theme_select.ts` (`<dds-theme-select>`)
  - Subagent 4: `gallery_shell/gallery_shell.ts` (`<dds-gallery-shell>`)
- [x] **Delegate to `dds-reviewer` (Template D):** Run `just build-ts`, audit all 7 Phase 1 domain components and tests against all styleguides, and run `just test` & `just check`
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Documentation Components (`prose`, `params_table`, `usage_example`, `variant_view`)
- [ ] **Orchestrator Pre-Dispatch Contract Lock:** Confirm parameter shapes passed from views to `prose`, `params_table`, `usage_example`, and `variant_view`
- [ ] **Parallel Batch 2A — Delegate 4x `dds-component-builder` (Template B) concurrently:**
  - Subagent 1: `dj_design_system/components/domain/prose/` + `tests/components/test_prose.py`
  - Subagent 2: `dj_design_system/components/domain/params_table/` + `tests/components/test_params_table.py`
  - Subagent 3: `dj_design_system/components/domain/usage_example/` + `tests/components/test_usage_example.py`
  - Subagent 4: `dj_design_system/components/domain/variant_view/` + `tests/components/test_variant_view.py`
- [ ] **Delegate to `dds-reviewer` (Template D):** Audit all 4 documentation components and tests against `dds-components.md`, `python.md`, and `html-css.md`, and run `just test` & `just check`
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
