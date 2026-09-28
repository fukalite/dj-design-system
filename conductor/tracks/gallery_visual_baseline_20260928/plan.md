# Implementation Plan: Gallery Rebuild 0 — Visual Baseline & CI Visual Regression

Captures a deterministic Playwright screenshot baseline of the current gallery in a pinned container, and adds a blocking CI job that compares fresh screenshots against it on every pull request.

## Phase 1: Harness & Comparison [checkpoint: 9dee0fe]
- [x] Task: Write Failing Tests (`Red Phase`) [5f29cf1]
  - [x] The comparison helper passes identical images, fails on differences beyond tolerance, fails on size mismatch, and writes `expected` / `actual` / `diff` files.
  - [x] A missing baseline fails normally and is created in update mode.
- [x] Task: Implement to Pass Tests (`Green Phase`) [29bc1fe]
  - [x] Extract or add a shared `pixelmatch` comparison helper (reusing `VisualRegressionPlugin` logic). [5f29cf1]
  - [x] Add the `visual` marker. [29bc1fe]
  - [x] Add capture helpers: wait for iframes and `document.fonts.ready`, disable animations, mask dynamic regions, block external network. [29bc1fe]
- [x] Task: Refactor and Verify Coverage [9dee0fe]
  - [x] Enable greenlet coverage tracing (Playwright); visual.py 92%, capture.py 100%.
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 2: Pinned Rendering Environment & Recipes [checkpoint: 08f675b]
- [x] Task: Pin the Playwright version in the `justfile`; add a unit test that the CI container tag matches it. [f093cd2]
- [x] Task: Add `just visual-run` (direct), and `just visual` / `just update-visual-baselines` (in the pinned `linux/amd64` container, installing `playwright==<version>`). [d85b948]
- [x] Task: `just update-visual-baselines` regenerates **all** gallery screenshots in one command [08f675b]
  - [x] Write failing tests: update mode rewrites only changed baselines, and deletes orphaned baselines (files no screenshot test produced) after a full run.
  - [x] Implement pruning in the suite's session teardown, only when the whole suite ran in update mode (never on a filtered `-k` run).
- [x] Task: Change `just e2e` to exclude the `visual` marker. [f093cd2]
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 3: Screenshot Coverage
- [x] Task: Capture Scrolling Regions [45ccfcb]
  - [x] The gallery shell scrolls inside the sidebar and main panes, so `full_page` screenshots stop at the viewport height (found in Phase 1 verification: nav items below the fold are cut off). Use a viewport tall enough to show all content, or capture each scroll container's full height separately; add a test that fails if content is clipped.
- [x] Task: Static States [d6519d6]
  - [x] Index, folder, documentation and component pages.
  - [x] Light and dark gallery themes; wide and narrow viewports.
- [x] Task: Interactive States [bd1b89d]
  - [x] Mobile sidebar open; breadcrumb flyout open.
  - [x] Each sandbox toolbar popout open; outline and RTL toggles active.
  - [x] Search results with a query entered.
  - [x] Documentation / sandbox tab switch on a narrow viewport.
  - [x] Make canvas iframe capture deterministic: wait for the canvas-resize loop to converge and replay reports lost before the gallery listener attaches (issue #111).
- [x] Task: Generate baselines with `just update-visual-baselines` against the current `main` gallery and commit them. [d6519d6, bd1b89d] (40 baselines)
- [~] Task: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 4: CI Job
- [ ] Task: Add the `visual-regression` job to `ci.yml`
  - [ ] Run in the pinned container; install with `uv`; run `just visual`.
  - [ ] Upload `actual` screenshots always; upload `expected` / `actual` / `diff` and write a job summary on failure.
  - [ ] Add the job to `ci-complete`'s `needs`.
- [ ] Task: Verify
  - [ ] Re-run the job several times on the same commit; confirm it passes every time.
  - [ ] On a scratch branch, change a gallery colour; confirm the job fails with a useful diff artifact and summary; revert.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 5: Documentation
- [ ] Task: Document running visual tests and updating baselines locally via Docker in `CONTRIBUTING.md`, including the Docker prerequisite and the "explain baseline changes in the PR" rule.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
