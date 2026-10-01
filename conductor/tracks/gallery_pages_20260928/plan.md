# Implementation Plan: Gallery Rebuild 5 — Page Composition & Legacy Asset Removal

Rewrites the gallery templates as compositions of built-in components and removes the legacy gallery assets.

## Phase 1: Baseline Measurements [checkpoint: a7bb97a]
- [x] Task: Record component page render time on the example project. [a7bb97a] (See `performance.md`.)
- [x] Task: Add tests pinning template block names, element IDs and legacy include paths (`breadcrumb.html`, `navtree.html`, `toolbar.html`, `canvas_widget.html`). [a7bb97a]
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) [a7bb97a]

---

## Phase 2: Shell & Simple Pages [checkpoint: 2ed1fb4]
- [x] Task: Write Failing Tests (`Red Phase`) [2ed1fb4]
  - [x] `base.html`, `index.html`, `folder.html` and `documentation.html` render via `dds__*` components (assert component output markers).
  - [x] Legacy partials render their component equivalents.
- [x] Task: Implement to Pass Tests (`Green Phase`) [2ed1fb4]
  - [x] Rewrite the templates; convert legacy partials into thin wrappers.
  - [x] Load gallery assets solely via internal component media. (Except `gallery.css`, until phase 4, and the second `code_highlight.css` link, which keeps it after `layout/page.css` in the cascade.)
- [x] Task: Refactor and Verify Coverage [2ed1fb4]
- [x] Task: Confirm the track 0 visual baseline passes. [2ed1fb4]
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) [2ed1fb4]

---

## Phase 3: Component Page & Sandbox [checkpoint: 3b8d4d4]
- [x] Task: Write Failing Tests (`Red Phase`) [3b8d4d4]
  - [x] `component.html` and `sandbox_fragment.html` render via components; the HTMX fragment response still contains only the sandbox body.
  - [x] View context provides tab, viewport and zoom option lists.
- [x] Task: Implement to Pass Tests (`Green Phase`) [3b8d4d4]
  - [x] Rewrite the templates; move hard-coded option lists into view context or component defaults. (`toolbar.html` holds the toolbar composition, included by `sandbox_fragment.html`.)
  - [x] Convert `canvas_widget.html` into a thin wrapper. (Markdown canvases now use `CanvasWidget` directly.)
- [x] Task: Refactor and Verify Coverage [3b8d4d4]
- [x] Task: Confirm the track 0 visual baseline and all e2e tests pass. [3b8d4d4]
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) [3b8d4d4]

---

## Phase 4: Legacy Asset Removal
- [x] Task: Assign or remove every remaining rule in the legacy stylesheets; delete the empty files. (Sandbox pane rules moved to `pane.css` and `canvas_widget.css`; unused rules dropped. Media is merged in dependency order so `code_highlight.css` still follows the page and prose CSS.)
- [x] Task: Remove references to deleted files (templates, `.github/scripts/save_canvas_pages.py`, docs, tests). (Only provenance comments remain. Changelog updated.)
- [x] Task: Verify the static demo export still builds and renders. (Only `gallery.css` drops out; 0 computed-style differences across 27 exported pages.)
- [x] Task: Re-measure component page render time; investigate any significant regression. (See `performance.md`: +24% with the cached template loader, +80% without.)
- [x] Task: Confirm the track 0 visual baseline, `just check`, `just test` and `just e2e` pass. (Pane's `sandbox` variant preview baselines regenerated: its own preview now gets the sandbox rule it always had in the gallery.)
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
