# Specification: Built-in `elements` Collection

## Overview
Implements the general-purpose UI primitives in `dj_design_system/components/elements/<name>/`, flattened under `{% dds__<name> %}`, with 100% co-located `.py`, `.html`, `.css`, `.ts` (where interactive), `gallery.py`, and `index.md` files.

## Functional Requirements
1. **Static Element Components (`dj_design_system/components/elements/`):**
   - `icon` (`{% dds__icon %}`): Inline SVG icon primitive with semantic size and accessibility support.
   - `button` (`{% dds__button %}`): Action and toggle button primitive supporting variants, icon-only mode, `aria-pressed`, and link (`href`) rendering, with parameter interactions resolved in `get_context()`.
   - `badge` (`{% dds__badge %}`): Compact status/metadata pill mapped to Tier 2 control/status tokens.
   - `notice` (`{% dds__notice %}`): Callout/alert box mapped to `--dds-status-{info|success|warning|error}-*` tokens.
   - `table` (`{% dds__table %}`): Data table primitive with slot support for headers/rows.
   - `breadcrumb` (`{% dds__breadcrumb %}`): Hierarchical trail navigation element.
   - `form_field` (`{% dds__form_field %}`): Label, control slot, and description/error wrapper using `--dds-control-*` tokens.
2. **Interactive Element Components (Light DOM `<dds-*>` Web Components in TypeScript):**
   - `code_block` (`{% dds__code_block %}` + `<dds-code-block>`): Syntax-highlighted code block with `<pre>`/`<code>` formatting reset (`white-space: pre`, `tab-size: 4`, `font-variant-ligatures: none`) and copy-to-clipboard custom element.
   - `tabs` (`{% dds__tabs %}` + `<dds-tabs>`): Accessible tab list + tab panel switcher with keyboard navigation (`ArrowLeft`/`ArrowRight`/`Home`/`End`).
   - `popout` & `popout_option` (`{% dds__popout %}`, `{% dds__popout_option %}` + `<dds-popout>`): Accessible dropdown menu / popover trigger and floating menu (`data-surface="popout"`) with `Escape` and outside-click dismissal via `AbortController`.

## Acceptance Criteria
- Every component in `dj_design_system/components/elements/` adheres strictly to `conductor/code_styleguides/dds-components.md`:
  - 100% co-located directory (`<name>.py`, `<name>.html`, `<name>.css`, `<name>.ts` if interactive, `gallery.py`, `index.md`).
  - Zero BEM (`__` or `--`) in CSS/HTML; CUBE CSS `@layer blocks` + Tier 3 `--_<component>-*` tokens mapped exclusively from Tier 2 `--dds-*` tokens.
  - Python-biased `get_context()` with zero template filters for value computation.
  - Full unit test and gallery render coverage.
