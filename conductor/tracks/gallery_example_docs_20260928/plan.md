# Implementation Plan: Gallery Rebuild 6 — Example Project Showcase & Documentation

Polishes the built-in components' presentation in the example project and documents the gallery rebuild series.

## Phase 1: Example Project Showcase [checkpoint: 19b80af]
- [x] Task: Review Labels & Structure [57096db]
  - [x] Set the app `verbose_name` and group labels for the built-in section. (`verbose_name = "Django Design System"`; the group folders already read well.)
  - [x] Add an `index.md` for each built-in group. (And one for the app.)
- [x] Task: Review Docstrings & Gallery Examples [57096db]
  - [x] Audit every built-in for docstring, parameter descriptions and `basic` / `maximal` examples; fill gaps. (No gaps: every built-in has a docstring with usage, every parameter has a description, and all have examples except `Divider`, which has no parameters.)
- [x] Task: Canvas Theming [19b80af]
  - [x] Write a failing test that a built-in previewed under the example "dark" theme receives the dark token class.
  - [x] Implement the theme mapping; confirm the test passes. (Each example theme's `html_attrs` adds the matching `gallery-theme-*` class. Pre-existing dark styling problems this exposes: #129, and the warning Notice, covered by #112.)
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) [19b80af]

---

## Phase 2: Snapshots & Static Demo [checkpoint: 0f71c42]
- [x] Task: Generate and commit built-in component snapshot baselines with the integration testing harness. [0f71c42] (Not done with the harness: its baselines only match the machine that made them, and it fails for other reasons; see #130. The built-ins' snapshots are covered by `tests/e2e/visual/test_builtin_components.py`, which renders every built-in's basic and maximal examples in light and dark in the pinned Playwright image and runs in CI.)
- [x] Task: Confirm the static demo export includes and renders the built-in components. [0f71c42] (`save_canvas_pages.py` now gives canvases with HTML in their parameters safe file names; before, those previews were empty. All 38 built-in pages and their 98 previews load.)
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) [0f71c42]

---

## Phase 3: Documentation [checkpoint: f120ec1]
- [x] Task: Document `GALLERY_EXCLUDE_APPS` and `GALLERY_SHOW_BUILTIN_COMPONENTS` in `docs/api/settings.md`. [8024543]
- [x] Task: Document internal components in `docs/components.md` and `docs/registry.md`. [6e4b24d]
- [x] Task: Update `docs/gallery.md` (built from DjDS components, stable classes and tokens, deprecated partials, overriding pages). [6d2b6f1]
- [x] Task: Update the feature list and `CHANGELOG.md`. [f120ec1]
- [x] Task: Confirm `just docs-build` succeeds with no new warnings. [f120ec1] (No new messages. The existing `#security-fields-all` anchor in `components.md` is broken because `attr_list` isn't enabled, so the new links use heading anchors.)
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) [f120ec1]
