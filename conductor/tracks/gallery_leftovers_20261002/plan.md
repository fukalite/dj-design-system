# Implementation Plan: Gallery Rebuild 7 — Remaining Markup into Components

Moves the last hand-written gallery markup into built-in components and shared templates.

## Phase 1: Canvas Messages, PageHeader, UsageExamples [checkpoint: 23168bc]
- [x] Task: Canvas Messages [4e297be]
  - [x] Write failing tests that the three canvas messages render from shared templates with unchanged markup.
  - [x] Move them to `canvas/error.html` and `canvas/warning.html`; raise an issue for the unstyled error in the canvas iframe. (unstyled error in the iframe: #147)
- [x] Task: `PageHeader` [aa683e6]
  - [x] Write failing tests (parity with the index and folder headings, escaping, registration).
  - [x] Implement it and use it in `index.html` and `folder.html`.
- [x] Task: `UsageExamples` [9b1c524]
  - [x] Write failing tests (parity with the `.gallery-usage` wrapper, CSS ownership).
  - [x] Implement it, move the `.gallery-usage` rules, and use it in `component.html`.
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) [23168bc]

---

## Phase 2: Sandbox Parts
- [ ] Task: `BgSwatch` and `ToolbarValue`
  - [ ] Write failing tests (parity with the toolbar's swatch, chip and value markup).
  - [ ] Implement them and use them in `toolbar.html`.
- [ ] Task: `SandboxCanvas`
  - [ ] Write failing tests (parity with the wrapper, CSS ownership).
  - [ ] Implement it, move the `.gallery-sandbox__canvas` rule, and use it in `sandbox_fragment.html`.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
