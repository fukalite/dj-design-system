# Implementation Plan: Gallery Rebuild 4 — Sandbox & Canvas Components

Builds the canvas, documentation and sandbox components, and redistributes `gallery-toolbar.js` / `gallery-toolbar.css` into component-owned assets.

## Phase 1: Toolbar Behaviour Characterisation [checkpoint: 2451a49]
- [x] Task: Write Characterisation Tests [2451a49]
  - [x] Add e2e tests pinning current toolbar behaviour: each popout opens and closes (click, outside click, Escape); background, viewport and zoom apply to the iframe; outline, measure and RTL toggles; drawer resize; state retained across an HTMX parameter change. (Correction: the legacy script has no Escape handling, so Escape isn't pinned. #112 adds it. The tests are in `tests/e2e/test_sandbox_toolbar.py`.)
  - [x] Confirm they pass against the legacy implementation.
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) [2451a49]

---

## Phase 2: `CanvasWidget`, `UsageExample`, `ParamsTable` [checkpoint: a9846f5]
- [x] Task: Write Failing Tests (`Red Phase`) [e40021e]
  - [x] `CanvasWidget` renders the three toggles, the iframe (`src` or `srcdoc`, `sandbox`) and both code panes, handling pre-highlighted input. (Correction: it takes raw code and highlights it through `CodeBlock`'s new `bare` variant, a plain `<pre><code>`, so the panes keep their exact markup. Nothing produces pre-highlighted input with a `highlight` wrapper, so that branch was dead.)
  - [x] `UsageExample` renders with and without a preview URL.
  - [x] `ParamsTable` renders every column and the "no parameters" state.
- [x] Task: Implement to Pass Tests (`Green Phase`) [e40021e]
  - [x] Implement components, templates and gallery side-cars.
  - [x] Move canvas widget, usage, doc preview and parameters table CSS, plus the iframe resize messaging JS. (The parameters table's CSS already lives in `Table`. The resize script now loads on every gallery page, so doc-page canvases also grow to fit tall content; accepted.)
- [x] Task: Refactor and Verify Coverage [e40021e]
- [x] Task: Confirm the track 0 visual baseline passes. [952a256]
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) [a9846f5]

---

## Phase 3: `ParamsForm`, `FormRow` [checkpoint: 2517973]
- [x] Task: Write Failing Tests (`Red Phase`) [42d7cfb]
  - [x] `ParamsForm` renders the HTMX attributes, hidden theme input and drawer wrapper.
  - [x] `FormRow` renders label, hint, field and errors from a `BoundField`. (Also takes an example dict, for gallery examples, which travel as URL parameters.)
- [x] Task: Implement to Pass Tests (`Green Phase`) [42d7cfb]
  - [x] Implement components, templates and gallery side-cars.
  - [x] Move parameter form and drawer CSS and the drawer resize JS.
- [x] Task: Refactor and Verify Coverage [42d7cfb]
- [x] Task: Confirm the track 0 visual baseline and characterisation tests pass. [2517973]
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) [2517973]

---

## Phase 4: `SandboxToolbar`, `Popout`, `PopoutOption`, `ToggleButton`
- [x] Task: Write Failing Tests (`Red Phase`) [c1c0438]
  - [x] Each renders the legacy markup, IDs, ARIA attributes and `data-*` attributes. (Composed, they reproduce the legacy toolbar.)
- [x] Task: Implement to Pass Tests (`Green Phase`) [c1c0438]
  - [x] Implement components, templates and gallery side-cars.
  - [x] Split the remaining `gallery-toolbar.js` into component JS; move `gallery-measure.js`; move `gallery-toolbar.css`.
  - [x] Delete `gallery-toolbar.js` and `gallery-toolbar.css` once empty.
- [x] Task: Refactor and Verify Coverage [c1c0438]
- [x] Task: Confirm the track 0 visual baseline and characterisation tests pass. [c453bf1]
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
