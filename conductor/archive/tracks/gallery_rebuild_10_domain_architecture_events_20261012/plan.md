# Implementation Plan: Domain Component Architecture, Event Decoupling & Shell Mediator (`gallery_rebuild_10_domain_architecture_events_20261012`)

## Phase 1: Thin Leaf Composites & Modular Shell/Theme/Pane Managers (`theme_select`, `search_box`, `theme-manager.ts`, `pane-manager.ts`)
- [x] Task: Write unit tests in `tests/components/test_theme_select.py`, `tests/components/test_search_box.py`, and shell/manager tests asserting `ThemeOption` dataclass, event-only dispatch in `theme_select.ts` (zero cookie/storage writes), `SearchIndexEntry` dataclass, Combobox `aria-activedescendant` + scroll-into-view + `focusInput()` in `search_box.ts` (no un-scoped document `/` keydown listener), and modular `ThemeManager` / `PaneManager` orchestration (including static snapshot notice consolidation).
- [x] Task: Refactor `theme_select.py`, `__init__.py`, and `theme_select.ts`:
  - Define and export `ThemeOption` dataclass in `theme_select.py` and `__init__.py`.
  - Strip `document.cookie` and `localStorage` mutations from `theme_select.ts`, dispatching `dds:theme-change` exclusively.
- [x] Task: Refactor `search_box.py`, `__init__.py`, and `search_box.ts`:
  - Define and export `SearchIndexEntry` dataclass in `search_box.py` and `__init__.py`.
  - Remove un-scoped `document.addEventListener('keydown')` for `'/'`; expose `focusInput(): void`.
  - Implement full WAI-ARIA Combobox pattern with option `id`s, `aria-activedescendant`, and `scrollIntoView({ block: 'nearest' })`.
- [x] Task: Extract `theme-manager.ts` and `pane-manager.ts` in `dj_design_system/static/dj_design_system/` and wire into `gallery-shell.ts`:
  - Move UI/consumer theme & colour scheme persistence (`document.cookie`, `localStorage`, URL params, iframe sync) into `ThemeManager`.
  - Move drawer state, tab/split-pane hash routing, global `'/'` & `⌘K`/`Ctrl+K` search focus, and `#static-snapshot-notice` visibility into `PaneManager`, removing legacy `gallery-snapshot-notice.js`.
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 2: Popout Encapsulation, Stage Controls, Iframe `postMessage` & `SandboxManager` (`popout`, `sandbox_toolbar`, `canvas_widget`, `canvas-resize.ts`, `sandbox-manager.ts`)
- [x] Task: Write unit tests in `tests/components/test_popout.py`, `tests/components/test_sandbox_toolbar.py`, `tests/components/test_canvas_widget.py`, and sandbox/iframe manager tests asserting `<dds-popout>` trigger label auto-update & `selectValue()`, `SandboxControlOption` dataclass, decoupled `sandbox_toolbar.ts` (no `window.location.href`, no `sessionStorage`, no child popout DOM piercing), decoupled `canvas_widget.ts` (no `contentDocument` style/DOM injection, no `dds:sandbox-*` document listeners, no `sessionStorage`), typed `canvas-resize.ts` `postMessage` stage receiver, and `SandboxManager` coordination.
- [x] Task: Enhance `popout.ts` (`DDSPopoutElement`):
  - Auto-update `[data-popout-trigger] > span` when a `menuitemradio` option is selected and include `label` in `dds:popout-select` detail.
  - Expose public `selectValue(value: string): void` method.
- [x] Task: Refactor `sandbox_toolbar.py`, `__init__.py`, and `sandbox_toolbar.ts`:
  - Define and export `SandboxControlOption` dataclass.
  - Remove `window.location.href` mutation, `sessionStorage`, and child `dds-popout` DOM queries from `sandbox_toolbar.ts`; emit `dds:sandbox-variant` and expose `applyState(state)` delegating to child `popout.selectValue()`.
- [x] Task: Refactor `canvas_widget.ts`, upgrade `canvas-resize.js` to `canvas-resize.ts`, and update `canvas.css`:
  - Remove all preview iframe `contentDocument` DOM/style penetration, sibling `dds:sandbox-*` listeners, and `sessionStorage` lookups from `canvas_widget.ts`; post `{ type: 'dds:canvas-stage', ... }` to `iframe.contentWindow`.
  - Convert `canvas-resize.js` to strict TypeScript `canvas-resize.ts` handling both resize observation and incoming `dds:canvas-stage` messages, backed by `[data-canvas-outline]` and `[data-canvas-measure]` rules in `canvas.css`.
- [x] Task: Create `sandbox-manager.ts` and integrate with `gallery-shell.ts` to coordinate `sessionStorage` (`dds_toolbar_state`), toolbar <-> canvas synchronisation, variant URL navigation, and reset.
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 3: Parameters & Navigation Tree Contracts (`sandbox_params` & `nav_tree`)
- [x] Task: Write unit tests in `tests/components/test_sandbox_params.py` and `tests/components/test_nav_tree.py` asserting `NavTreeNode` dataclass, removal of hardcoded query inputs (`_iss`, `_dds_theme`, `_dds_variant`), `extra_inputs` slot support, and explicit `hx_target` handling.
- [x] Task: Refactor `sandbox_params.py`, `sandbox_params.html`, `sandbox_params.ts`, and `templates/dj_design_system/gallery/panes/sandbox.html`:
  - Remove hardcoded hidden inputs for `_iss`, `_dds_theme`, and `_dds_variant` from `sandbox_params.html`; add `{% slot "extra_inputs" %}` and pass gallery routing inputs from `panes/sandbox.html`.
  - Remove hardcoded `DEFAULT_HX_TARGET = "closest [data-gallery-sandbox-body]"` default from `sandbox_params.py`.
  - Harmonise client-side `dds:params-change` dispatch with HTMX form submission.
- [x] Task: Refactor `nav_tree.py` and `__init__.py`:
  - Define and export `NavTreeNode` dataclass.
  - Remove core coupling to `data.NavItemInputData` inside `nav_tree.py`.
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 4: Native TypeScript Test Suite (Vitest), Python Cruft Removal & Full System Verification
- [x] Task: Configure `vitest` and `happy-dom` in `package.json` and `vitest.config.ts`.
- [x] Task: Write native TypeScript behavioural DOM tests in `tests/ts/` covering all 11 Light DOM custom elements (`popout`, `code_block`, `tooltip`, `tabs`, `split_pane`, `theme_select`, `search_box`, `sandbox_toolbar`, `canvas_widget`, `sandbox_params`, `nav_tree`) and the 5 static shell/manager/iframe modules (`gallery-shell`, `theme-manager`, `pane-manager`, `sandbox-manager`, `canvas-resize`).
- [x] Task: Run the new Vitest suite (`npx vitest run`) and existing Python test suite (`just test`) side by side and verify both pass 100%.
- [x] Task: Remove the legacy Python `.ts` substring-matching test classes from `tests/components/test_*.py` and `tests/test_gallery_shell_ts.py` (retaining legitimate Python/template/CSS/build pipeline tests).
- [x] Task: Wire `just test-ts` into `justfile` (`just test`) and `.github/workflows/ci.yml`.
- [x] Task: Compile all TypeScript modules with `just build-ts`, run `just check` and `just typecheck`, and run `just test`.
- [x] Task: Track Completion Checkpoint & Summary.


