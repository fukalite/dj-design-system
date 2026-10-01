# Implementation Plan: Gallery Rebuild 6 — Example Project Showcase & Documentation

Polishes the built-in components' presentation in the example project and documents the gallery rebuild series.

## Phase 1: Example Project Showcase
- [x] Task: Review Labels & Structure [57096db]
  - [x] Set the app `verbose_name` and group labels for the built-in section. (`verbose_name = "Django Design System"`; the group folders already read well.)
  - [x] Add an `index.md` for each built-in group. (And one for the app.)
- [x] Task: Review Docstrings & Gallery Examples [57096db]
  - [x] Audit every built-in for docstring, parameter descriptions and `basic` / `maximal` examples; fill gaps. (No gaps: every built-in has a docstring with usage, every parameter has a description, and all have examples except `Divider`, which has no parameters.)
- [x] Task: Canvas Theming [19b80af]
  - [x] Write a failing test that a built-in previewed under the example "dark" theme receives the dark token class.
  - [x] Implement the theme mapping; confirm the test passes. (Each example theme's `html_attrs` adds the matching `gallery-theme-*` class. Pre-existing dark styling problems this exposes: #129, and the warning Notice, covered by #112.)
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 2: Snapshots & Static Demo
- [ ] Task: Generate and commit built-in component snapshot baselines with the integration testing harness.
- [ ] Task: Confirm the static demo export includes and renders the built-in components.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 3: Documentation
- [ ] Task: Document `GALLERY_EXCLUDE_APPS` and `GALLERY_SHOW_BUILTIN_COMPONENTS` in `docs/api/settings.md`.
- [ ] Task: Document internal components in `docs/components.md` and `docs/registry.md`.
- [ ] Task: Update `docs/gallery.md` (built from DjDS components, stable classes and tokens, deprecated partials, overriding pages).
- [ ] Task: Update the feature list and `CHANGELOG.md`.
- [ ] Task: Confirm `just docs-build` succeeds with no new warnings.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
