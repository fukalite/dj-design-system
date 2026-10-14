# Specification: CSS Architecture, 3-Tier Design Tokens & TypeScript Pipeline

## Overview
Implements the CUBE CSS `@layer` cascade, the complete Tier 1 (`--_dds-*`) and Tier 2 (`--dds-*`) design token system across all 6 domains, the 7 Every Layout composition primitives, and the TypeScript compilation pipeline (`tsconfig.json` + `just build-ts`) for co-located `<dds-*>` Light DOM web components.

## Functional Requirements
1. **CSS Cascade Layers (`@layer`):**
   - Establish `@layer reset, tokens, global, composition, blocks, utilities;` in `dj_design_system/static/dj_design_system/css/tokens.css` and `composition.css` (or loaded via base gallery stylesheet).
2. **Tier 1 Private Scale Literals (`--_dds-<category>-<step>`) & Tier 2 Public Semantic Tokens (`--dds-<domain>-<role>-<property>`):**
   - Author the literal CSS Custom Properties inside `@layer tokens` per `conductor/code_styleguides/dds-components.md`:
     - **Domain 1 — Surfaces & Layers (`--dds-surface-*`):** `sunken`, `base`, `raised`, `floating`, `overlay`, plus named gallery surfaces (`stage`, `code`, `docs`, `sandbox`, `topbar`, `sidebar`, `popout`) and `[data-surface='<name>']` contextual re-aliasing.
     - **Domain 2 — Typography & Text (`--dds-font-*`, `--dds-type-*`, `--dds-text-*`):** `ui`, `prose`, `technical` font families; `title`, `heading`, `subheading`, `overline`, `prose`, `body`, `control`, `caption`, `code` type roles; `prominent`, `default`, `muted` text colours.
     - **Domain 3 — Spacing & Layout (`--dds-space-*`, `--dds-layout-*`):** `3xs` through `3xl`, `gap-tight`/`gap-default`/`gap-loose`/`gap-section`, `inset-compact`/`inset-default`/`inset-spacious`, `sidebar-width`, `prose-measure`.
     - **Domain 4 — States (`--dds-state-*`):** Uniform schema (`bg`, `color`, `border-color`, `border-width`, `border-style`, `shadow`, `outline`, `opacity`, `cursor`, `transition-duration`, `transition-easing`) across `interactive`, `hover`, `focus`, `active`, `selected`, `disabled`, plus `entry-duration`, `entry-easing`, `exit-duration`, `exit-easing`.
     - **Domain 5 — Controls (`--dds-control-*`):** Control box (`bg`, `color`, `placeholder-color`, `border-color`, `border-width`, `border-style`, `radius`, `shadow`, `padding-inline`, `padding-block`, `min-height`, `gap`) + `accent-color`.
     - **Domain 6 — Status (`--dds-status-*`):** `info`, `success`, `warning`, `error` (`bg`, `color`, `border-color`, `icon-color`).
   - Provide `.gallery-theme-dark` overrides for all Tier 2 colour/surface/shadow tokens.
3. **Every Layout Composition Primitives (`@layer composition`):**
   - Implement `.l-stack`, `.l-cluster`, `.l-sidebar`, `.l-switcher`, `.l-center`, `.l-box`, and `.l-grid` parameterized by Tier 2 spacing/layout tokens.
4. **TypeScript Build Pipeline:**
   - Add `tsconfig.json` and `package.json` (or `esbuild`/`tsc` tooling) so `dj_design_system/components/**/*.ts` compile to gitignored `<name>.js` sibling files.
   - Add `just build-ts` recipe and hook it into `just test-all` / CI before E2E tests.

## Acceptance Criteria
- All Tier 1 (`--_dds-*`) and Tier 2 (`--dds-*`) tokens in `dds-components.md` are defined and verified by automated CSS token contract tests.
- All 7 Every Layout `.l-*` primitives are defined in `@layer composition`.
- `just build-ts` compiles co-located `.ts` files cleanly with strict type checking.
