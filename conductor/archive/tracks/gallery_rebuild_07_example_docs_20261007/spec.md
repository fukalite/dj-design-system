# Specification: `example_project/` Rework & Consumer Shadowing Showcase

## Overview
Audits and refactors `example_project/` to strictly follow `conductor/code_styleguides/example-project.md`, showcases consumer `dds__*` component shadowing and Tier 2 `--dds-*` token theming, and updates user-facing documentation in `docs/`.

## Functional Requirements
1. **`example_project/` Pedagogical Audit & Refactor:**
   - Ensure all components in `example_project/` follow `conductor/code_styleguides/example-project.md`:
     - Realistic domain components with clear docstrings and type annotations.
     - Complete feature coverage across the suite (primitive/enum/collection parameters, `Parameter.resolve`, parameter data factories, required/optional slots, `SlotParam`, co-located `Media`, `gallery.py` variants, and `index.md` with `{% canvas %}` tags).
     - Strict separation from `dds` internal conventions (no `--_dds-*` private token leaks).
2. **Consumer Customization & Shadowing Showcase:**
   - Demonstrate consumer Tier 2 `--dds-*` token theming and `dds__*` component shadowing in `example_project/` (or dedicated showcase configuration).
3. **Documentation:**
   - Document the built-in `dds` component architecture, `GALLERY_SHOW_DDS_COMPONENTS`, `GALLERY_EXCLUDE_APPS`, Tier 2 `--dds-*` token theming, and `dds__*` component shadowing in `docs/`.

## Acceptance Criteria
- All `example_project/` components comply with `conductor/code_styleguides/example-project.md`.
- User-facing documentation in `docs/` covers gallery theming, visibility settings, and `dds__*` shadowing.
- All unit, E2E, and visual tests pass.
