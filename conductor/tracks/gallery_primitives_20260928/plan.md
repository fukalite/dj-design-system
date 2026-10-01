# Implementation Plan: Gallery Rebuild 2 — Primitive Components

Builds the foundation stylesheet and primitive built-in components, moving their CSS out of the legacy stylesheets without visual change.

## Phase 1: Foundation Stylesheet & Internal Media Loading [checkpoint: 5ce941b]
- [x] Task: Write Failing Tests (`Red Phase`) [5ce941b]
  - [x] `gallery/base.html` renders internal component `<link>`/`<script>` tags before the legacy stylesheets.
  - [x] `canvas_iframe_view` includes an internal component's own media when previewing it.
  - [x] Consumer canvases still exclude internal media.
- [x] Task: Implement to Pass Tests (`Green Phase`) [5ce941b]
  - [x] Move tokens, icon masks, typography variables and reset into `ui/foundation.css`.
  - [x] Load internal media in `base.html`; load previewed-component media in the canvas iframe view.
- [x] Task: Confirm the track 0 visual baseline passes. [5ce941b] (CI run 36562515878)
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) [5ce941b]

---

## Phase 2: `Icon`, `Button`, `IconButton` [checkpoint: 2b4d3c0]
- [x] Task: Write Failing Tests (`Red Phase`) [2b4d3c0]
  - [x] `Icon` renders each named SVG/mask icon, with `aria-hidden` and size.
  - [x] `Button` renders variants and `aria-pressed` / `aria-expanded` / `aria-controls` correctly.
  - [x] `IconButton` renders `<a>` with `href` and `<button>` otherwise; requires a label.
- [x] Task: Implement to Pass Tests (`Green Phase`) [2b4d3c0]
  - [x] Implement components, templates and gallery side-cars.
  - [x] Move the related CSS rules (including responsive rules) out of the legacy stylesheets.
- [x] Task: Refactor and Verify Coverage [2b4d3c0]
- [x] Task: Confirm the track 0 visual baseline passes. [2b4d3c0]
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) [2b4d3c0]

---

## Phase 3: `Divider`, `SectionHeading`, `CodeBlock`, `Notice`, `Table` [checkpoint: 8671bc3]
- [x] Task: Write Failing Tests (`Red Phase`) [88449d5]
  - [x] Each renders the legacy markup and classes; `SectionHeading` honours `level`.
  - [x] `CodeBlock` escapes plain input and passes through pre-highlighted HTML safely.
  - [x] `Notice` renders `warning` and `hint` variants; the snapshot variant includes its script with CSP nonce support.
  - [x] `Table` renders `head` and `body` slots.
- [x] Task: Implement to Pass Tests (`Green Phase`) [88449d5]
  - [x] Implement components, templates and gallery side-cars.
  - [x] Move related CSS rules and `gallery-snapshot-notice.js` into the component assets.
- [x] Task: Refactor and Verify Coverage [88449d5]
- [x] Task: Capture built-in component canvases in the pinned visual suite (`tests/e2e/visual/`): each built-in's basic and maximal examples in both gallery themes. Replaces the screenshot plugin dropped from `tests/e2e/test_package_components.py`, which had no deterministic rendering environment. [8671bc3]
- [x] Task: Confirm the track 0 visual baseline passes. [8671bc3]
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) [8671bc3]
