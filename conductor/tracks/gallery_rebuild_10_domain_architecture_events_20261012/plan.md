# Implementation Plan: Domain Component Architecture, Event Decoupling & Shell Mediator (`gallery_rebuild_10_domain_architecture_events_20261012`)

## Phase 1: Leaf Domain Architecture & Persistence (`theme_select` & `search_box`)
- [ ] Task: Write unit tests in `tests/components/test_theme_select.py` and `tests/components/test_search_box.py` asserting `ThemeOption` dataclass, event-only dispatch (no cookie/storage writes), `SearchIndexEntry` dataclass, and Combobox `aria-activedescendant` behavior.
- [ ] Task: Refactor `theme_select.py` and `theme_select.ts`:
  - Define and export `ThemeOption` dataclass.
  - Strip `document.cookie` and `localStorage` mutations from `theme_select.ts`, dispatching `dds:theme-change` exclusively.
- [ ] Task: Update `gallery-shell.ts`:
  - Centralize `document.cookie` and `localStorage` persistence inside `handleThemeChange()`.
  - Add global hotkey coordination (`'/'` / `⌘K`) to focus `<dds-search-box>`.
- [ ] Task: Refactor `search_box.py` and `search_box.ts`:
  - Define and export `SearchIndexEntry` dataclass.
  - Remove un-scoped `document` key listener; support `data-global-shortcut`.
  - Implement full WAI-ARIA Combobox pattern with `aria-activedescendant` and scroll-into-view.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 2: Stage & Sandbox Control Decoupling (`canvas_widget` & `sandbox_toolbar`)
- [ ] Task: Write unit tests in `tests/components/test_sandbox_toolbar.py` and `tests/components/test_canvas_widget.py` asserting decoupled variant navigation, elimination of iframe DOM penetration, and removal of sibling event sniffing.
- [ ] Task: Refactor `sandbox_toolbar.py` and `sandbox_toolbar.ts`:
  - Define and export `SandboxControlOption` dataclass.
  - Remove `window.location.href` mutation from `sandbox_toolbar.ts`; dispatch `dds:sandbox-variant` or render native links.
  - Stop querying child `dds-popout` DOM internals; listen to `dds:popout-select`.
  - Remove hardcoded `sessionStorage['dds_toolbar_state']`.
- [ ] Task: Refactor `canvas_widget.py` and `canvas_widget.ts`:
  - Remove all preview iframe DOM penetration (`.canvas-wrapper`, inline style injection, `dir='rtl'`).
  - Communicate canvas parameters via URL query parameters or postMessage protocol.
  - Remove document-level listeners for sibling toolbar events and `sessionStorage` lookups.
- [ ] Task: Update `gallery-shell.ts` to coordinate variant routing and toolbar persistence.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 3: Parameters & Navigation Tree Contracts (`sandbox_params` & `nav_tree`)
- [ ] Task: Write unit tests in `tests/components/test_sandbox_params.py` and `tests/components/test_nav_tree.py` asserting `NavTreeNode` dataclass, removal of hardcoded query inputs, and `extra_inputs` slot support.
- [ ] Task: Refactor `sandbox_params.py` and `sandbox_params.html`:
  - Remove hardcoded hidden inputs for `_iss`, `_dds_theme`, and `_dds_variant`.
  - Add `{% slot "extra_inputs" %}` slot for host application hidden inputs.
  - Remove hardcoded `DEFAULT_HX_TARGET = "closest [data-gallery-sandbox-body]"`.
  - Harmonise client-side `dds:params-change` dispatch with HTMX form submission.
- [ ] Task: Refactor `nav_tree.py` and `__init__.py`:
  - Define and export `NavTreeNode` dataclass.
  - Remove core coupling to `NavItemInputData` and gallery-specific node semantics (`active_variant`, `has_index_doc`).
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 4: Full System Verification & Regression Gate
- [ ] Task: Compile all TypeScript modules with `just build-ts`.
- [ ] Task: Run `just check` (ruff, djlint, stylelint) and verify 0 errors.
- [ ] Task: Run full test suite with `just test` (all 1,569+ unit tests pass).
- [ ] Task: Track Completion Checkpoint & Summary.
