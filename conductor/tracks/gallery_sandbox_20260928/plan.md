# Implementation Plan: Gallery Rebuild 4 — Sandbox & Canvas Components

Builds the canvas, documentation and sandbox components, and redistributes `gallery-toolbar.js` / `gallery-toolbar.css` into component-owned assets.

## Phase 1: Toolbar Behaviour Characterisation [checkpoint: 2451a49]
- [x] Task: Write Characterisation Tests [2451a49]
  - [x] Add e2e tests pinning current toolbar behaviour: each popout opens and closes (click, outside click, Escape); background, viewport and zoom apply to the iframe; outline, measure and RTL toggles; drawer resize; state retained across an HTMX parameter change. (Correction: the legacy script has no Escape handling, so Escape isn't pinned. #112 adds it. The tests are in `tests/e2e/test_sandbox_toolbar.py`.)
  - [x] Confirm they pass against the legacy implementation.
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) [2451a49]

---

## Phase 2: `CanvasWidget`, `UsageExample`, `ParamsTable`
- [ ] Task: Write Failing Tests (`Red Phase`)
  - [ ] `CanvasWidget` renders the three toggles, the iframe (`src` or `srcdoc`, `sandbox`) and both code panes, handling pre-highlighted input.
  - [ ] `UsageExample` renders with and without a preview URL.
  - [ ] `ParamsTable` renders every column and the "no parameters" state.
- [ ] Task: Implement to Pass Tests (`Green Phase`)
  - [ ] Implement components, templates and gallery side-cars.
  - [ ] Move canvas widget, usage, doc preview and parameters table CSS, plus the iframe resize messaging JS.
- [ ] Task: Refactor and Verify Coverage
- [ ] Task: Confirm the track 0 visual baseline passes.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 3: `ParamsForm`, `FormRow`
- [ ] Task: Write Failing Tests (`Red Phase`)
  - [ ] `ParamsForm` renders the HTMX attributes, hidden theme input and drawer wrapper.
  - [ ] `FormRow` renders label, hint, field and errors from a `BoundField`.
- [ ] Task: Implement to Pass Tests (`Green Phase`)
  - [ ] Implement components, templates and gallery side-cars.
  - [ ] Move parameter form and drawer CSS and the drawer resize JS.
- [ ] Task: Refactor and Verify Coverage
- [ ] Task: Confirm the track 0 visual baseline and characterisation tests pass.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 4: `SandboxToolbar`, `Popout`, `PopoutOption`, `ToggleButton`
- [ ] Task: Write Failing Tests (`Red Phase`)
  - [ ] Each renders the legacy markup, IDs, ARIA attributes and `data-*` attributes.
- [ ] Task: Implement to Pass Tests (`Green Phase`)
  - [ ] Implement components, templates and gallery side-cars.
  - [ ] Split the remaining `gallery-toolbar.js` into component JS; move `gallery-measure.js`; move `gallery-toolbar.css`.
  - [ ] Delete `gallery-toolbar.js` and `gallery-toolbar.css` once empty.
- [ ] Task: Refactor and Verify Coverage
- [ ] Task: Confirm the track 0 visual baseline and characterisation tests pass.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
