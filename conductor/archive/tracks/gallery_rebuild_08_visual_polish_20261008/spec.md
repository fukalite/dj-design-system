# Specification: Visual Parity, Token & Typography Polish (`gallery_rebuild_08_visual_polish_20261008`)

## Overview
Address all visual, structural, typographic, and token-layer regressions surfaced by the Track 6 Before/After visual comparison (`#221`) across the rebuilt `dds` gallery UI. Fixes must be applied at the appropriate architectural layer (`tokens.css` & `gallery-highlight.css` -> `composition.css` -> `elements/*` -> `domain/*` -> `views/*` & `gallery/*.html`) without altering public component parameter contracts, verified iteratively against Track 1 (`origin/visual/rebuild-baselines`) screenshots across all viewports (`mobile`, `desktop`, `wide`), themes (`light`, `dark`), and interactive states.

## Scope & Architectural Layer Mapping

### 1. View & Theme Isolation Layer (`dj_design_system/views/component.py`, `gallery/base.html`)
- **Decouple Global Gallery Chrome Theme from Sandbox Component Theme:**
  - In `views/component.py`, `_resolve_sandbox_theme()` resolves the component's sandbox theme (e.g. `AlertComponent` with `Meta.available_themes = ["dark"]`).
  - `context["active_theme"]` and `context["theme_body_class"]` for the gallery shell (`<html>` / `<body>` and global topbar theme selector) must remain the user's global gallery theme from `get_base_context()`, while `sandbox_active_theme` and `sandbox_available_themes` govern only the sandbox toolbar and canvas preview URLs.
- **Safe HTML Rendering for Component & Variant Descriptions:**
  - Wrap `component_description` and `variant_description` in `django.utils.safestring.mark_safe()` in `views/component.py` and pass `html=component_description` to `{% dds__prose %}` in `component.html` so docstrings render as formatted HTML paragraphs and inline `<code>` elements rather than escaped markup.

### 2. Design Tokens, Syntax Highlighting & Code Block Layer (`tokens.css`, `gallery-highlight.css`, `elements/code_block`)
- **Fix `--hl-block-text` Token Resolution (`gallery-highlight.css`):**
  - Map `--hl-block-text` to `var(--dds-surface-code-text-default-color, #f8f8f2)` instead of `var(--dds-text-default-color, #f8f8f2)` so code inside `[data-surface="code"]` never inherits dark charcoal `#212529` text on a dark `#1e1e2e` code background in light mode.
- **Server-Side Pygments Syntax Highlighting in `CodeBlock` (`code_block.py`, `code_block.html`):**
  - Enhance `CodeBlock.get_context()` to automatically syntax-highlight `self.code` based on `self.language` (`"django"` via `highlight_template_tag`, `"html"` via `highlight_html`, or Pygments lexer fallback) into `highlighted_code` (marked safe), while preserving plain `stripped_code` text content inside `<code data-code-content>` so client-side clipboard copy (`code_block.ts`) copies unescaped plain text without changing `CodeBlock`'s parameter signature.
- **Compact Overlay Copy Button Chrome (`code_block.html`, `code_block.css`):**
  - When `title` is not explicitly provided (`has_title=False`), do not render a separate full-width header bar for `language`; instead, position the `[data-copy-trigger]` button as a compact overlay in the top-right corner of the code block (rendering the full `<header>` bar only when `has_title=True`).

### 3. Shell, Topbar, Sidebar, Breadcrumb & Split-Pane Chrome (`gallery_shell`, `sidebar`, `breadcrumb`, `tabs`, `split_pane`)
- **Full-Width Topbar & Non-Duplicated Sidebar Header (`gallery_shell`, `sidebar`):**
  - Retain the full-width topbar (`Brand + Breadcrumbs` on the left, `Search + Theme Select + Tabs` on the right).
  - Omit the duplicate brand title from the desktop sidebar inside `gallery_shell.html` (while preserving `dds__sidebar`'s `brand_name` rendering when explicitly passed in standalone tests, and ensuring `sidebar.css` styles `[data-sidebar-brand]` with `--dds-text-prominent-color` on `[data-surface="sidebar"]` so mobile/standalone headers are high-contrast light-on-dark).
- **Responsive Mobile Breadcrumb Ellipsis Flyout (`breadcrumb`):**
  - When `crumbs|length > 2`, render a responsive ellipsis trigger (`[data-breadcrumb-ellipsis]`) using `<dds-popout>` on narrow/mobile viewports (`< 768px`) that collapses intermediate crumbs into a popout menu while keeping the root (`Gallery`), parent/ellipsis, and current page on a single compact row.
- **Responsive Tab Switcher & Full-Bleed Split-Pane Framing (`tabs`, `split_pane`, `gallery_shell.css`):**
  - Hide the topbar Documentation/Sandbox tab switcher at wide split-pane viewports (`>= 1600px`) where both Documentation and Sandbox panes are simultaneously visible side-by-side.
  - Make `dds-split-pane` sit flush within `<main>` (full-bleed pane header strip with `border-bottom` and consistent inner content padding matching `index.html`, `folder.html`, and `documentation.html`) rather than wrapping panes in an inset bordered card (box-in-a-box).

### 4. Documentation Hierarchy, Typography, Casing & Sandbox Layout (`prose`, `usage_example`, `params_table`, `variant_view`, `sandbox`, `sandbox_toolbar`, `params_form`, `component.html`)
- **Consistent Typographic Hierarchy, Capitalisation & Text Contrast (`prominent` / `default` / `muted`):**
  - Standardise section headings in `component.html`, `usage_example`, `params_table`, and `variant_view`:
    - Use uppercase muted overline headings (`--dds-text-overline-*`, `text-transform: uppercase`, `color: var(--dds-text-muted-color)`) with `<hr data-docs-divider>` section dividers for `DESCRIPTION`, `USAGE`, `PARAMETERS`, and `FURTHER DOCUMENTATION` (and sub-overlines `MINIMAL EXAMPLE`, `ALL PARAMETERS`, `QUALIFIED TAG USAGE`, `PREVIEW`).
    - Ensure prose headings (`h1`, `h2` with subtle bottom border, `h3`) use `--dds-text-prominent-color`, body copy uses `--dds-text-default-color`, and secondary captions/overlines/table headers use `--dds-text-muted-color`.
    - Style inline `<code>` in `prose.css` and `params_table.css` with a subtle surface pill background and balanced inline padding.
    - In `params_table`, style uppercase muted column headers and neutral `Yes`/`No` (or subtle muted/info badge) for `Required` instead of an error-red pill that mimics a validation error, and ensure the table wrapper scrolls horizontally on mobile without clipping cell text.
- **Full-Height Sandbox Stage & Two-Column Parameter Controls (`sandbox`, `sandbox_toolbar`, `params_form`):**
  - Make `dds-sandbox` a full-height flex column (`100%` of the sandbox pane height) so the preview stage (`[data-sandbox-stage]`) flexes (`flex: 1`) to fill available vertical space with the preview iframe centred.
  - Arrange `dds-params-form` rows as a clean two-column parameter table/grid (`name + description` on the left, form control on the right) separated by subtle row borders below the resizable splitter bar.

### 5. Expanded Visual Baseline Coverage & Iterative Verification Loop (`tests/e2e/visual/`)
- Expand `tests/e2e/visual/test_gallery_interactions.py` to also capture:
  - `component--desktop--sandbox-tab` (Desktop `1280px` switched to the Sandbox tab)
  - `component--wide--template-tab` (Wide `1920px` Sandbox switched to the Template code tab)
  - `component--wide--html-tab` (Wide `1920px` Sandbox switched to the HTML code tab)
- **Strict Per-Iteration Architectural & Standards Gate (Phase 4 Loop):**
  - Every visual polish iteration in Phase 4 MUST execute a mandatory internal code review (`dds-reviewer` auditing against `conductor/code_styleguides/dds-components.md`, `html-css.md`, `python.md`, `javascript.md`, and `layered-architecture.md`) **before** re-running the visual capture:
    1. **Inspect Visual Diffs (`view_file`):** Inspect the actual Before/After/Diff PNGs across viewports and themes.
    2. **Classify Layer & Token Tier First:** Never hardcode raw colours (`#...`, `rgb`/`rgba`), raw `px`/`rem` dimensions, or reference Tier 1 `--_dds-*` primitives inside component CSS (`dj_design_system/components/**/*.css`). If a visual adjustment requires a new semantic value (e.g. a border, surface, spacing, or typography role), define a proper Tier 2 `--dds-*` semantic token in `tokens.css` (mapped from Tier 1 `--_dds-*` across `:root`, `.gallery-theme-dark`, and `[data-surface]`) and map it into the component's Tier 3 `--_<component>-*` token block.
    3. **Per-Iteration `dds-reviewer` Audit & Automated Checks:** Delegate to `dds-reviewer` on every iteration to catch any hardcoded literals, token-tier violations, selector specificity breaches (`<= 0,2,0`), or styleguide drift immediately, and run `just check`, `just typecheck`, and `just test`.
    4. **Re-Capture & Verify:** Re-run the visual comparison against Track 1 (`origin/visual/rebuild-baselines`) and repeat the loop until all 49 captures are visually cohesive and 100% compliant with all styleguides.

## Acceptance Criteria
- [ ] All component docstrings and variant descriptions render as formatted HTML paragraphs and inline `<code>` tags (zero escaped `<p>` or `<code>` tags).
- [ ] All code blocks across component docstrings, usage examples, variant views, markdown docs, and sandbox Template/HTML tabs render with Pygments syntax highlighting, readable contrast in both light and dark themes, and a compact top-right overlay Copy button when no explicit `title` is set.
- [ ] Viewing a component with restricted `Meta.available_themes` (e.g. `AlertComponent` with `available_themes = ["dark"]`) in light mode keeps the global gallery chrome in light mode while scoping `sandbox_active_theme` to the sandbox.
- [ ] Full-width topbar renders without a duplicate brand header in the desktop sidebar; mobile breadcrumb collapses intermediate items into an interactive `[data-breadcrumb-ellipsis]` flyout; topbar Documentation/Sandbox tabs hide at `>= 1600px`.
- [ ] Documentation sections (`DESCRIPTION`, `USAGE`, `PARAMETERS`, `FURTHER DOCUMENTATION`), subheadings, inline code pills, and parameter tables use consistent overline casing, `<hr>` dividers, left alignment, and `prominent`/`default`/`muted` text tokens.
- [ ] Sandbox preview stage flexes to fill vertical space and parameter controls render in a clean two-column layout.
- [ ] Every visual iteration in Phase 4 passes an internal `dds-reviewer` audit confirming zero hardcoded CSS values, zero Tier 1 (`--_dds-*`) leaks in components, and strict 3-Tier token adherence (`--_dds-*` -> `--dds-*` -> `--_<component>-*`).
- [ ] All 49 visual baselines (46 existing + 3 new sandbox/code-tab captures) are inspected via `view_file`, updated on the Track 8 branch, and embedded as Before/After/Diff comparisons in the Track 8 PR description.
- [ ] `just check`, `just typecheck`, `just test`, `just e2e`, and `just visual-run` pass with 0 errors.

