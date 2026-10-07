# Specification: Visual Regression Harness & `dds` Component Foundation

## Overview
Establishes the automated Playwright visual regression harness and the internal component discovery, registration, co-located asset resolution, and gallery visibility infrastructure required to build the gallery UI out of `dj_design_system`'s own component system.

## Functional Requirements
1. **Code Styleguides:**
   - Codify the `dds` built-in component architecture in `conductor/code_styleguides/dds-components.md`.
   - Codify the `example_project/` pedagogical component rules in `conductor/code_styleguides/example-project.md`.
2. **Visual Regression Harness:**
   - Provide `dj_design_system/testing/visual.py` and `dj_design_system/testing/plugins.py` (`assert_visual_match`) for Playwright screenshot comparison with configurable pixel thresholds.
   - Add visual test suites under `tests/e2e/visual/` and `just visual-*` commands in `justfile`.
3. **Built-in `dds` Component Package & Flattening:**
   - Promote `dj_design_system/components.py` to `dj_design_system/components/` (`base.py`, `elements/`, `domain/`).
   - Register built-in `dj_design_system` components under the `dds` prefix using `FlattenStrategy.ALL` so both `elements/` and `domain/` flatten to `{% dds__<name> %}`.
   - Allow consumer apps to shadow any `dds__<name>` component cleanly without requiring `override=True`.
   - Automatically register `ComponentsTemplateLoader` and `ComponentsStaticFinder` in `DjangoDesignSystemConfig.ready()` after `component_registry.autodiscover()` so co-located `.html`, `.css`, and compiled `.js` assets resolve automatically.
   - Aggregate internal component media via `component_registry.get_internal_media()`.
4. **Gallery Visibility:**
   - Add `dj_design_system/services/visibility.py` supporting `GALLERY_SHOW_DDS_COMPONENTS` (default `False`) and `GALLERY_EXCLUDE_APPS`.
   - Add `example_project/settings_dds.py` with `GALLERY_SHOW_DDS_COMPONENTS = True`.

## Acceptance Criteria
- `just test` and `just check` pass with 100% of unit tests, `ruff`, `djlint`, and `mypy` succeeding.
- Co-located `.js` files inside `dj_design_system/components/**/*.js` are gitignored.
