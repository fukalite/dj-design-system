# Implementation Plan: Gallery Rebuild 5 — Page Composition & Legacy Asset Removal

Rewrites the gallery templates as compositions of built-in components and removes the legacy gallery assets.

## Phase 1: Baseline Measurements
- [x] Task: Record component page render time on the example project. [a7bb97a] (See `performance.md`.)
- [x] Task: Add tests pinning template block names, element IDs and legacy include paths (`breadcrumb.html`, `navtree.html`, `toolbar.html`, `canvas_widget.html`). [a7bb97a]
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 2: Shell & Simple Pages
- [ ] Task: Write Failing Tests (`Red Phase`)
  - [ ] `base.html`, `index.html`, `folder.html` and `documentation.html` render via `dds__*` components (assert component output markers).
  - [ ] Legacy partials render their component equivalents.
- [ ] Task: Implement to Pass Tests (`Green Phase`)
  - [ ] Rewrite the templates; convert legacy partials into thin wrappers.
  - [ ] Load gallery assets solely via internal component media.
- [ ] Task: Refactor and Verify Coverage
- [ ] Task: Confirm the track 0 visual baseline passes.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 3: Component Page & Sandbox
- [ ] Task: Write Failing Tests (`Red Phase`)
  - [ ] `component.html` and `sandbox_fragment.html` render via components; the HTMX fragment response still contains only the sandbox body.
  - [ ] View context provides tab, viewport and zoom option lists.
- [ ] Task: Implement to Pass Tests (`Green Phase`)
  - [ ] Rewrite the templates; move hard-coded option lists into view context or component defaults.
  - [ ] Convert `canvas_widget.html` into a thin wrapper.
- [ ] Task: Refactor and Verify Coverage
- [ ] Task: Confirm the track 0 visual baseline and all e2e tests pass.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 4: Legacy Asset Removal
- [ ] Task: Assign or remove every remaining rule in the legacy stylesheets; delete the empty files.
- [ ] Task: Remove references to deleted files (templates, `.github/scripts/save_canvas_pages.py`, docs, tests).
- [ ] Task: Verify the static demo export still builds and renders.
- [ ] Task: Re-measure component page render time; investigate any significant regression.
- [ ] Task: Confirm the track 0 visual baseline, `just check`, `just test` and `just e2e` pass.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
