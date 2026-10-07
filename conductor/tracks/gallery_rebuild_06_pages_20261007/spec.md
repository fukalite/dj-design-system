# Specification: Gallery Page Composition, Legacy Asset Removal & Visual Baselines

## Overview
Replaces the legacy monolithic gallery templates and legacy BEM CSS/JS (`dj_design_system/static/dj_design_system/css/gallery.css`, `js/gallery.js`) with thin page templates composed of `{% dds__* %}` components and Every Layout primitives, and updates the visual regression baselines.

## Functional Requirements
1. **Page Template Composition (`dj_design_system/templates/dj_design_system/`):**
   - Rewrite `gallery/base.html`, `gallery/index.html`, `gallery/component_detail.html`, `gallery/document_detail.html`, `gallery/folder_detail.html`, `canvas_widget.html`, and `canvas/preview.html` as thin compositions of `{% dds__* %}` tags and Every Layout `.l-*` classes.
   - Inject `component_registry.get_internal_media()` in `gallery/base.html` so co-located component CSS and compiled `.js` custom elements load automatically.
2. **Legacy Asset Removal:**
   - Remove all legacy BEM rules (`__` / `--`) from `dj_design_system/static/dj_design_system/css/gallery.css` and remove legacy `js/gallery.js`.
3. **Visual Regression Baselines & E2E Verification:**
   - Verify all E2E functional and accessibility (`test_a11y.py`) suites pass.
   - Capture updated Playwright visual regression baselines via `just visual-update` and verify `just visual-test` passes with zero unexpected diffs.

## Acceptance Criteria
- Zero BEM selectors remain anywhere in `dj_design_system/`.
- All unit, E2E, accessibility, and visual regression tests pass (`just test-all` & `just visual-test`).
