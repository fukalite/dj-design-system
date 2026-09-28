# Gallery Rebuild 0 — Visual Baseline & CI Visual Regression

## Overview
This track comes before the gallery rebuild series, which rebuilds the gallery UI (sidebar, navigation, toolbar, sandbox, canvas widget, pages) out of dj-design-system's own components. It captures a Playwright screenshot baseline of the **current** gallery and adds a **CI job that compares fresh screenshots against the committed baselines on every pull request**. Every later track in the series, and every PR within it, is therefore visually regression-tested automatically.

It changes no application code.

### Track series
0. **Visual Baseline & CI Visual Regression** (this track)
1. Internal Component Foundation (`gallery_foundation_20260928`)
2. Primitive Components (`gallery_primitives_20260928`)
3. Navigation & Layout Components (`gallery_nav_layout_20260928`)
4. Sandbox & Canvas Components (`gallery_sandbox_20260928`)
5. Page Composition & Legacy Asset Removal (`gallery_pages_20260928`)
6. Example Project Showcase & Documentation (`gallery_example_docs_20260928`)

Each track ships as its own PR.

## Key Constraint: Rendering Environment
Screenshots are only comparable when taken in the same environment. Fonts, anti-aliasing and browser builds differ between macOS, Windows and Linux, and between Playwright/Chromium versions. Baselines captured on a developer laptop would fail in CI on every run.

Therefore:
- **Baselines are always generated in the CI rendering environment:** the official Playwright Docker image (`mcr.microsoft.com/playwright/python`), pinned to an exact tag. Inside the container, the Python `playwright` package is installed at exactly the image's version (the `dev` extra leaves it unpinned, and a mismatch means Playwright cannot find its browser).
- **Architecture is pinned too:** GitHub-hosted runners are `linux/amd64`, while Apple Silicon Macs default to `linux/arm64` images. Chromium can rasterise differently per architecture, so local runs force `--platform linux/amd64` (emulated; slower, but faithful to CI).
- The CI job runs inside that same pinned container.
- Developers generate and check baselines locally by running the suite **inside the same container** via `just` recipes (requires Docker), never on the host. CI never generates baselines.
- Upgrading Playwright or the image tag is a deliberate change that regenerates all baselines in the same PR.

## Functional Requirements

### 1. Screenshot Coverage
A Playwright screenshot suite under `tests/e2e/visual/`, marked `visual` (a new pytest marker), capturing the gallery as served by the existing e2e setup (`tests/settings.py` with the `live_server` fixtures in `tests/e2e/conftest.py`, gallery mounted at `/dds/`). This deliberately uses the test settings rather than `example_project/settings.py`: the test settings never enable `GALLERY_SHOW_BUILTIN_COMPONENTS`, so the nav tree stays stable while later tracks add built-in components. It captures:
- **Pages:** gallery index, a folder page, a documentation page, a component page (documentation + sandbox).
- **Themes:** light and dark gallery themes.
- **Viewports:** wide (side-by-side panes) and narrow (stacked panes with tabs).
- **Interactive states:**
  - mobile sidebar open;
  - breadcrumb flyout open (narrow viewport, deep path);
  - each sandbox toolbar popout open (background, viewport, zoom);
  - box-model outline and RTL toggles active;
  - search results dropdown with a query entered;
  - documentation / sandbox tab switched on a narrow viewport.

### 2. Stability
- Mask or pin any region whose content legitimately changes during the rebuild series. Because the suite uses the test settings (built-ins hidden), the nav tree and component count should stay stable; masking is a fallback, not the default.
- Wait for canvas iframes to finish loading and resizing, and for web fonts (`document.fonts.ready`), before capturing.
- Disable CSS transitions, animations and caret blinking during capture.
- Load no external network resources during capture. HTMX is served from a local copy, or the route is fulfilled from a vendored file in tests, so a CDN outage cannot fail the job.

### 3. Comparison
- Compare with `pixelmatch` + `Pillow`, reusing (or extracting a shared helper from) the comparison logic in `dj_design_system.testing.plugins.VisualRegressionPlugin`.
- Two documented tolerances: a per-pixel colour `threshold`, and a maximum mismatched-pixel ratio per screenshot. Start strict (e.g. `threshold=0.1`, ratio `0`) and loosen only with evidence of flakiness.
- A size mismatch is a failure.
- On failure, write `expected`, `actual` and `diff` PNGs for each failing screenshot into an output directory.
- A **missing** baseline is a failure in CI; it is only created when running in update mode.

### 4. CI Job
A new `visual-regression` job in `.github/workflows/ci.yml`:
- Runs on every pull request and push to `main`, alongside the existing jobs.
- Runs inside the pinned Playwright container (`container:` on the job).
- Installs dependencies with `uv` (as other jobs do) and runs `just visual`.
- **Blocking:** added to `ci-complete`'s `needs`.
- On failure:
  - uploads the `expected` / `actual` / `diff` images as a workflow artifact (e.g. `visual-regression-diffs`);
  - writes a job summary (`$GITHUB_STEP_SUMMARY`) listing each failing screenshot and its mismatched-pixel count, with a link to the artifact.
- Always uploads the `actual` screenshots as an artifact, so reviewers can inspect the rendered gallery even when the job passes.

### 5. Updating Baselines
Baselines are generated **locally only**, never by CI. CI only compares.
- When a visual change is intended, the developer runs `just update-visual-baselines`. It runs the suite in update mode inside the pinned container and writes new baselines into the working tree. The developer commits and pushes them as normal.
- `just update-visual-baselines` is the single command for regenerating **all** baselines at any later date. It rewrites only baselines whose pixels changed, and deletes orphaned baselines that no screenshot test produces any more. Pruning only happens on a full, unfiltered update run.
- A PR that changes baselines must explain why in its description. Reviewers inspect the changed PNGs in the PR diff and the `actual` screenshots uploaded by CI.

### 6. Local Developer Recipes
| Recipe | Purpose |
| --- | --- |
| `just visual` | Run the visual suite in the pinned container and compare (same as CI). |
| `just update-visual-baselines` | Regenerate baselines in the pinned container. |
| `just e2e` | Existing recipe, changed to exclude the `visual` marker, so it stays fast and host-runnable. |

The Playwright version lives in one place in the `justfile` (`playwright_version`). The CI workflow necessarily repeats the container tag; a unit test asserts the two agree. A `just visual-run` recipe runs the suite directly (used inside the container by both the Docker recipes and CI); `just visual` and `just update-visual-baselines` wrap it in `docker run`.

### 7. Dependencies
- `pixelmatch` and `Pillow` already reach the `dev` extra via `dj-design-system[testing-all]`; no change needed.
- Register the `visual` marker in `pyproject.toml`.

## Non-Functional Requirements
- **Deterministic:** The CI job passes on repeated runs of the same commit (verified by re-running it several times before merging this track).
- **Fast enough:** The job should complete in a few minutes. Parallelise with `pytest-xdist` only if needed.
- **Follows existing conventions:** Reuse `tests/e2e/conftest.py` fixtures (live server, `gallery_url`) and the existing snapshot comparison code where possible.

## Acceptance Criteria
- [ ] Screenshot suite covers every page, theme, viewport and interactive state listed above.
- [ ] Baselines are generated in the pinned Playwright container and committed.
- [ ] `visual-regression` CI job runs on PRs, is blocking via `ci-complete`, and uploads diffs plus a summary on failure.
- [ ] Deliberately changing a gallery colour on a scratch branch makes the job fail with a useful diff artifact (verified, then reverted).
- [ ] The job passes on several consecutive re-runs of the same commit.
- [ ] `just visual` and `just update-visual-baselines` work locally via Docker.
- [ ] `just e2e` no longer runs the visual suite.
- [ ] Baseline update process (local Docker only) is documented in `CONTRIBUTING.md`, including the Docker prerequisite.

## Out of Scope
- Any change to gallery templates, CSS, JS or Python.
- Running the example project's per-component snapshot tests (`just test-demo`) in CI. Worth doing, but a separate decision.
- Cross-browser screenshots (Chromium only).
