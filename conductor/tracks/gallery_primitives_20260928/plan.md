# Implementation Plan: Gallery Rebuild 2 — Primitive Components

Builds the foundation stylesheet and primitive built-in components, moving their CSS out of the legacy stylesheets without visual change.

## Phase 1: Foundation Stylesheet & Internal Media Loading
- [ ] Task: Write Failing Tests (`Red Phase`)
  - [ ] `gallery/base.html` renders internal component `<link>`/`<script>` tags before the legacy stylesheets.
  - [ ] `canvas_iframe_view` includes an internal component's own media when previewing it.
  - [ ] Consumer canvases still exclude internal media.
- [ ] Task: Implement to Pass Tests (`Green Phase`)
  - [ ] Move tokens, icon masks, typography variables and reset into `ui/foundation.css`.
  - [ ] Load internal media in `base.html`; load previewed-component media in the canvas iframe view.
- [ ] Task: Confirm the track 0 visual baseline passes.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 2: `Icon`, `Button`, `IconButton`
- [ ] Task: Write Failing Tests (`Red Phase`)
  - [ ] `Icon` renders each named SVG/mask icon, with `aria-hidden` and size.
  - [ ] `Button` renders variants and `aria-pressed` / `aria-expanded` / `aria-controls` correctly.
  - [ ] `IconButton` renders `<a>` with `href` and `<button>` otherwise; requires a label.
- [ ] Task: Implement to Pass Tests (`Green Phase`)
  - [ ] Implement components, templates and gallery side-cars.
  - [ ] Move the related CSS rules (including responsive rules) out of the legacy stylesheets.
- [ ] Task: Refactor and Verify Coverage
- [ ] Task: Confirm the track 0 visual baseline passes.
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
