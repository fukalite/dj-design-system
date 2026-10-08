# Specification: Gallery Page Composition, Legacy Asset Removal & Visual Baselines

## Overview
Replaces the legacy monolithic gallery templates and legacy BEM CSS/JS (`dj_design_system/static/dj_design_system/css/gallery.css`, `js/gallery.js`) with thin page templates composed of `{% dds__* %}` components and Every Layout primitives, and updates the visual regression baselines.

## Functional Requirements
1. **Page Template Composition (`dj_design_system/templates/dj_design_system/`):**
   - Rewrite `gallery/base.html`, `gallery/index.html`, `gallery/component_detail.html`, `gallery/document_detail.html`, `gallery/folder_detail.html`, `canvas_widget.html`, and `canvas/preview.html` as thin compositions of `{% dds__* %}` tags and Every Layout `.l-*` classes.
   - Inject `component_registry.get_internal_media()` in `gallery/base.html` so co-located component CSS and compiled `.js` custom elements load automatically.
2. **Pre-Removal Visual Comparison Review:**
   - Once the new gallery templates are composed and before deleting legacy assets, run the Playwright visual comparison suite (`just visual` / `just visual-run`) against the legacy gallery baselines and include a detailed breakdown of the visual diffs in the Track 6 PR description.
3. **Legacy Asset Removal:**
   - Remove all legacy BEM rules (`__` / `--`) from `dj_design_system/static/dj_design_system/gallery.css` and `gallery-toolbar.css` and remove obsolete legacy JS files.
4. **E2E & Accessibility Verification:**
   - Verify all E2E functional and accessibility (`test_a11y.py`) suites pass (`just e2e`).

## Acceptance Criteria
- Zero BEM selectors remain anywhere in `dj_design_system/`.
- Visual comparison between the rebuilt gallery and legacy gallery is executed prior to legacy asset removal and documented in the PR.
- All unit, E2E, and accessibility tests pass (`just test` & `just e2e`).
