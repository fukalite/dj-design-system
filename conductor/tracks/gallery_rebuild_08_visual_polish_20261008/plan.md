# Implementation Plan: Visual Parity, Token & Typography Polish (`gallery_rebuild_08_visual_polish_20261008`)

> **Iterative Workflow:** Every phase follows a strict **Layer Fix -> Unit/E2E Tests -> `dds-reviewer` Audit -> Visual Capture & Screenshot Inspection (`view_file`) -> Commit** cycle. No fixes are applied as ad-hoc page overrides; every fix must live at its proper token, composition, element, domain, or view layer.

## Phase 1: View Theme Isolation, Safe Prose HTML & Code Block Highlighting Layer
- [x] **View Layer (`views/component.py`, `gallery/component.html`):**
  - Decouple global gallery `active_theme` / `theme_body_class` from component-specific `sandbox_active_theme` / `sandbox_available_themes` so dark-only components (`AlertComponent`) do not force the gallery shell into dark mode during light-mode browsing.
  - Wrap `component_description` and `variant_description` in `mark_safe()` and pass `html=component_description` to `{% dds__prose %}` in `component.html`.
- [x] **Token & Code Block Layer (`gallery-highlight.css`, `elements/code_block`):**
  - Fix `--hl-block-text` in `gallery-highlight.css` to reference `var(--dds-surface-code-text-default-color, #f8f8f2)`.
  - Update `CodeBlock.get_context()` (`code_block.py`) and `code_block.html` to syntax-highlight `code` automatically via `highlight_template_tag` / `highlight_html` / Pygments while preserving plain text `textContent` for clipboard copy.
  - Update `code_block.html` and `code_block.css` so `[data-copy-trigger]` renders as a compact top-right overlay button when `has_title` is `False`, only rendering `<header>` when `has_title` is `True`.
- [x] **Tests & Review (`dds-reviewer`):** Add/update unit tests in `tests/components/test_code_block.py` and `tests/test_views.py`, run `dds-reviewer`, and verify `just check`, `just typecheck`, and `just test`.
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Shell Chrome, Non-Duplicated Sidebar Header, Mobile Breadcrumb Flyout & Split-Pane Framing
- [x] **Shell & Sidebar Layer (`gallery_shell`, `sidebar`):**
  - Remove duplicate `brand_name` from `dds__sidebar` invocation in `gallery_shell.html` while keeping `dds__sidebar`'s `brand_name` parameter functional for standalone usage.
  - Fix `[data-sidebar-brand]` colour token in `sidebar.css` to use `var(--dds-text-prominent-color)` on `[data-surface="sidebar"]` and ensure mobile drawer header contrast is crisp.
- [x] **Responsive Breadcrumb Ellipsis Flyout (`elements/breadcrumb`):**
  - Enhance `breadcrumb.py`, `breadcrumb.html`, and `breadcrumb.css` so paths with `> 2` crumbs render a mobile-only (`< 768px`) `[data-breadcrumb-ellipsis]` `<dds-popout>` menu containing intermediate crumbs while keeping full inline crumbs on desktop/wide viewports.
- [x] **Responsive Topbar Tabs & Full-Bleed Split-Pane (`domain/split_pane`, `domain/gallery_shell`):**
  - Hide topbar Documentation/Sandbox tab switcher in `gallery_shell.css` / `split_pane.css` at `@media (min-width: 100rem)` (`1600px`) when both panes are side-by-side.
  - Refactor `split_pane.css` from an inset bordered card to a full-bleed split container with a flush pane header strip (`DOCUMENTATION` / `SANDBOX`) and consistent page padding matching `index.html`, `folder.html`, and `documentation.html`.
- [x] **Tests & Review (`dds-reviewer`):** Update unit and E2E tests (`test_breadcrumb.py`, `test_gallery_shell.py`, `test_split_pane.py`), run `dds-reviewer`, and verify `just check`, `just typecheck`, and `just test`.
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Documentation Typography, Section Overlines, Params Table & Sandbox Layout
- [x] **Documentation & Typography Layer (`prose`, `usage_example`, `params_table`, `variant_view`, `component.html`):**
  - Standardise uppercase muted section overlines (`DESCRIPTION`, `USAGE`, `PARAMETERS`, `FURTHER DOCUMENTATION`) and `<hr data-docs-divider>` dividers in `component.html` and `variant_view.html`.
  - Refine `usage_example.css`, `prose.css`, and `params_table.css` heading scales, sub-overline casing (`MINIMAL EXAMPLE`, `ALL PARAMETERS`, `QUALIFIED TAG USAGE`), inline `<code>` surface pills, `h2` bottom rules, and `prominent`/`default`/`muted` text contrast tokens.
  - Update `params_table.html` and `params_table.css` for clean column headers, non-clipping responsive horizontal scroll, and neutral `Yes`/`No` requirement display.
- [x] **Sandbox Stage, Toolbar & Params Form Layer (`sandbox`, `sandbox_toolbar`, `params_form`):**
  - Update `sandbox.css` and `split_pane.css` so the sandbox pane and `[data-sandbox-stage]` flex to fill full viewport height (`flex: 1`), centring the preview canvas widget.
  - Refine `sandbox_toolbar.css` and `params_form.css` so toolbar controls sit in a compact single bar and parameter rows render in a clean two-column (`label + description` | `control`) grid below the splitter handle.
- [x] **Tests & Review (`dds-reviewer`):** Update component unit tests, run `dds-reviewer`, and verify `just check`, `just typecheck`, and `just test`.
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 4: Expanded Visual Baselines, Iterative Visual Inspection Loop & Stacked PR
- [x] **Expand Visual Suite (`tests/e2e/visual/test_gallery_interactions.py`):**
  - Add `test_desktop_sandbox_tab` (`component--desktop--sandbox-tab`), `test_sandbox_template_tab` (`component--wide--template-tab`), and `test_sandbox_html_tab` (`component--wide--html-tab`).
- [x] **Iterative Visual Inspection, Token-Tier Enforcement & Per-Iteration `dds-reviewer` Loop:**
  - For each iteration `N`:
    1. **Visual Capture & Inspection (`view_file`):** Compare live rendering against Track 1 (`origin/visual/rebuild-baselines`) across all 49 captures (`index`, `folder`, `document`, `component`, `variant`, `component-docs`, and all interactive captures across `mobile`, `desktop`, `wide`, `light`, `dark`) and inspect the Before/After/Diff PNGs via `view_file`.
    2. **Architectural & Token-Tier Fix:** Address every visual discrepancy at its proper architectural layer (`tokens.css` Tier 2 `--dds-*` semantic tokens -> `composition.css` `<l-*>` primitives -> component Tier 3 `--_<component>-*` tokens -> templates/views). Never introduce hardcoded CSS values (colours, spacing, radii, font sizes) or Tier 1 `--_dds-*` leaks in component stylesheets.
    3. **Per-Iteration `dds-reviewer` Audit & Test Gate:** Run `dds-reviewer` (auditing against `dds-components.md`, `html-css.md`, `python.md`, `javascript.md`, and `layered-architecture.md`) plus `just check`, `just typecheck`, and `just test` at the end of *every* iteration before re-capturing screenshots.
    4. **Repeat Until Converged:** Continue iterating until all 49 screenshots are visually cohesive, surprise-free, and pass the `dds-reviewer` audit with zero violations.
- [x] **Final Baselines, Visual Assets & Stacked Draft PR:**
  - Regenerate final baselines (`tests/e2e/visual/baselines/*.png`), verify `just check`, `just typecheck`, `just test`, `just e2e`, and `just visual-run`.
  - Generate Before (Track 1) / After (Track 8) / Diff PNG triplets, push them to `origin/visual/pr8-assets`, open the stacked draft PR (`gallery-rebuild/visual-polish -> gallery-rebuild/example-docs`), and run Gemini Code Review (`/review`) until green.
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

