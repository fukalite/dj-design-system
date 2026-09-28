# Gallery Rebuild 6 — Example Project Showcase & Documentation

## Overview
Final track of the gallery rebuild series (see `gallery_visual_baseline_20260928` for the full list). It polishes how the built-in components appear in the example project's gallery and documents everything the series introduced.

**Depends on:** `gallery_pages_20260928`.

## Functional Requirements

### 1. Example Project Showcase
- The example project already sets `GALLERY_SHOW_BUILTIN_COMPONENTS = True` (track 1). Review the built-in section of its gallery end to end:
  - app label and folder labels (`verbose_name`, `COMPONENT_DIRECTORIES` labels) read well, e.g. "DjDS Gallery UI" → Primitives / Navigation / Layout / Sandbox;
  - every built-in has a clear docstring, parameter descriptions and `basic` / `maximal` gallery examples;
  - add `index.md` pages for each built-in group explaining what it is for and that these are internal components.
- **Theming in canvases:** Built-in components previewed in the example project's canvas react to the example project's gallery themes. Map the example themes to the `.gallery-theme-light` / `.gallery-theme-dark` token classes via `APP_CANVAS_HTML_ATTRS` / theme `html_attrs` for `dj_design_system`, or equivalent.
- **Snapshots:** Add visual regression baselines for built-in components to `example_project/tests/snapshots/baseline/` using the existing integration testing harness.

### 2. Static Demo
- Ensure the published static demo (`docs` workflow / `save_canvas_pages.py`) includes the built-in components.

### 3. Documentation
- `docs/api/settings.md`: document `GALLERY_EXCLUDE_APPS` and `GALLERY_SHOW_BUILTIN_COMPONENTS`, including how they combine.
- `docs/components.md` / `docs/registry.md`: document internal components: `Meta.internal = True`, qualified-name-only tags, exclusion from short-name lookups and merged media.
- `docs/gallery.md`: explain that the gallery is built from DjDS's own components; which `.gallery-*` classes and `--gallery-*` tokens are stable for customisation; the legacy include paths (deprecated); and how to override a gallery page.
- `CHANGELOG.md`: new settings, internal components, the `components` package, deprecated partials, and the note that projects that **override** gallery templates may need to update.
- Update the feature list in the main documentation.

## Non-Functional Requirements
- `just docs-build` succeeds with no new warnings.
- Documentation follows the existing tone and structure in `docs/`.

## Acceptance Criteria
- [ ] Built-in components are well labelled, documented and themed in the example project's gallery.
- [ ] Built-in component snapshot baselines are committed and pass.
- [ ] The static demo includes the built-in components.
- [ ] Settings, internal components and gallery customisation are documented; changelog updated.
- [ ] `just check`, `just test`, `just e2e` and `just docs-build` pass.

## Out of Scope
- Making built-in components a supported public API for consumer pages. They remain internal and may change without deprecation.
