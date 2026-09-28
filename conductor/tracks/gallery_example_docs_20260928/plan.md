# Implementation Plan: Gallery Rebuild 6 — Example Project Showcase & Documentation

Polishes the built-in components' presentation in the example project and documents the gallery rebuild series.

## Phase 1: Example Project Showcase
- [ ] Task: Review Labels & Structure
  - [ ] Set the app `verbose_name` and group labels for the built-in section.
  - [ ] Add an `index.md` for each built-in group.
- [ ] Task: Review Docstrings & Gallery Examples
  - [ ] Audit every built-in for docstring, parameter descriptions and `basic` / `maximal` examples; fill gaps.
- [ ] Task: Canvas Theming
  - [ ] Write a failing test that a built-in previewed under the example "dark" theme receives the dark token class.
  - [ ] Implement the theme mapping; confirm the test passes.
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
