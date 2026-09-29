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

## Phase 2: `Icon`, `Button`, `IconButton`
- [x] Task: Write Failing Tests (`Red Phase`) [2b4d3c0]
  - [x] `Icon` renders each named SVG/mask icon, with `aria-hidden` and size.
  - [x] `Button` renders variants and `aria-pressed` / `aria-expanded` / `aria-controls` correctly.
  - [x] `IconButton` renders `<a>` with `href` and `<button>` otherwise; requires a label.
- [x] Task: Implement to Pass Tests (`Green Phase`) [2b4d3c0]
  - [x] Implement components, templates and gallery side-cars.
  - [x] Move the related CSS rules (including responsive rules) out of the legacy stylesheets.
- [x] Task: Refactor and Verify Coverage [2b4d3c0]
- [x] Task: Confirm the track 0 visual baseline passes. [2b4d3c0]
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 3: `Divider`, `SectionHeading`, `CodeBlock`, `Notice`, `Table`
- [ ] Task: Write Failing Tests (`Red Phase`)
  - [ ] Each renders the legacy markup and classes; `SectionHeading` honours `level`.
  - [ ] `CodeBlock` escapes plain input and passes through pre-highlighted HTML safely.
  - [ ] `Notice` renders `warning` and `hint` variants; the snapshot variant includes its script with CSP nonce support.
  - [ ] `Table` renders `head` and `body` slots.
- [ ] Task: Implement to Pass Tests (`Green Phase`)
  - [ ] Implement components, templates and gallery side-cars.
  - [ ] Move related CSS rules and `gallery-snapshot-notice.js` into the component assets.
- [ ] Task: Refactor and Verify Coverage
- [ ] Task: Confirm the track 0 visual baseline passes.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
