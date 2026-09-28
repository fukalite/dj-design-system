# Implementation Plan: Gallery Rebuild 0 — Visual Baseline & CI Visual Regression

Captures a deterministic Playwright screenshot baseline of the current gallery in a pinned container, and adds a blocking CI job that compares fresh screenshots against it on every pull request.

## Phase 1: Harness & Comparison
- [ ] Task: Write Failing Tests (`Red Phase`)
  - [ ] The comparison helper passes identical images, fails on differences beyond tolerance, fails on size mismatch, and writes `expected` / `actual` / `diff` files.
  - [ ] A missing baseline fails normally and is created in update mode.
- [ ] Task: Implement to Pass Tests (`Green Phase`)
  - [ ] Extract or add a shared `pixelmatch` comparison helper (reusing `VisualRegressionPlugin` logic).
  - [ ] Add the `visual` marker; add `pixelmatch` and `Pillow` to the `dev` extra.
  - [ ] Add capture helpers: wait for iframes and `document.fonts.ready`, disable animations, mask dynamic regions, block external network.
- [ ] Task: Refactor and Verify Coverage
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 2: Pinned Rendering Environment & Recipes
- [ ] Task: Pin the Playwright Docker image tag to match the project's Playwright version.
- [ ] Task: Add `just visual` and `just update-visual-baselines`, both running inside the pinned container.
- [ ] Task: Change `just e2e` to exclude the `visual` marker.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 3: Screenshot Coverage
- [ ] Task: Static States
  - [ ] Index, folder, documentation and component pages.
  - [ ] Light and dark gallery themes; wide and narrow viewports.
- [ ] Task: Interactive States
  - [ ] Mobile sidebar open; breadcrumb flyout open.
  - [ ] Each sandbox toolbar popout open; outline and RTL toggles active.
  - [ ] Search results with a query entered.
  - [ ] Documentation / sandbox tab switch on a narrow viewport.
- [ ] Task: Generate baselines with `just update-visual-baselines` against the current `main` gallery and commit them.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

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
