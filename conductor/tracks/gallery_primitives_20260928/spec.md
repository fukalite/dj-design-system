# Gallery Rebuild 2 — Primitive Components

## Overview
Part of the gallery rebuild series (see `gallery_visual_baseline_20260928` for the full list). This track builds the low-level built-in components that later tracks compose into navigation, layout and sandbox UI. It also establishes the shared foundation stylesheet and the "move, don't copy" CSS migration pattern used by tracks 2–4.

**Depends on:** `gallery_visual_baseline_20260928`, `gallery_foundation_20260928`.

## Conventions (apply to tracks 2–4)
- **Location:** Python in `dj_design_system/components/<group>/`; templates in `templates/dj_design_system/ui/<group>/`; CSS/JS in `static/dj_design_system/ui/<group>/`. No co-located assets (enforced by the track 1 convention test).
- **Naming:** Qualified tags with the `dds` prefix, e.g. `{% dds__primitives__icon %}`. Internal components have no short names.
- **Class names & tokens:** Components emit the **existing** `.gallery-*` BEM class names and consume the existing `--gallery-*` custom properties, so consumer CSS overrides keep working.
- **Move, don't copy:** When a component takes ownership of CSS rules, those rules are **removed** from the legacy stylesheet (`gallery.css`, `gallery-toolbar.css`, etc.) in the same change. Because class names are unchanged, the moved rules keep styling the legacy templates, and the track 0 visual baseline verifies each move. Responsive (`@media`) rules are split out and moved alongside the component they affect.
- **Sandbox examples:** Every component ships a `*_gallery.py` side-car (`basic_kwargs` / `maximal_kwargs`) so it renders well in the example project's gallery as soon as it lands.
- **Docstrings:** Every component and parameter has a docstring/description; these become its gallery documentation.

## Functional Requirements

### 1. Foundation Stylesheet & Internal Media Loading
- Extract the theme tokens (`:root`, `.gallery-theme-light`, `.gallery-theme-dark`), icon mask variables, typography variables and the scoped reset from `gallery.css` into `static/dj_design_system/ui/foundation.css`.
- Every built-in component's `Media.css` lists `foundation.css` first. Media merging de-duplicates it.
- `gallery/base.html` loads internal component media (via the track 1 internal-media accessor) **before** the legacy stylesheets, so the cascade order is unchanged.
- `canvas_iframe_view` loads the previewed component's own media even when it is internal, so built-ins render correctly in their own sandbox in the example project.

### 2. Components
| Component | Type | Replaces |
| --- | --- | --- |
| `Icon` | Tag | Inline SVGs (external link, eye, code, file-code, monitor, box-model, ruler, RTL) and mask icons (component, doc, folder, folder-open). `name` choice param; `size` param. |
| `Button` | Block | `.gallery-sandbox-toolbar__btn` and similar plain buttons. Params: `variant`, `pressed` (renders `aria-pressed`), `expanded`/`controls` (renders `aria-expanded`/`aria-controls`), `title`. |
| `IconButton` | Tag | Pill-style icon overlay buttons/links (`.gallery-doc-preview__sandbox-link`). Composes `Icon`. `href` renders an `<a>`, otherwise a `<button>`. |
| `Divider` | Tag | `.gallery-docs__divider`. |
| `SectionHeading` | Block | `.gallery-docs__section-heading` and `.gallery-usage__heading`. `level` param. |
| `CodeBlock` | Block | `.gallery-usage__pre` / `<pre><code>` blocks; supports pre-highlighted HTML input. |
| `Notice` | Block | Static snapshot notice and debug hint. `variant` param (`warning`, `hint`). Owns `gallery-snapshot-notice.js` for the snapshot variant. |
| `Table` | Block (slots: `head`, `body`) | `.gallery-params` table styling (the parameter-specific table is composed in track 4). |

### 3. Accessibility
- Decorative icons render `aria-hidden="true"`. `IconButton` requires an accessible label (`title` / `aria-label`).
- Component templates reproduce the ARIA attributes present in the legacy templates exactly.

## Non-Functional Requirements
- **No visual change:** track 0 visual baseline passes after every CSS move.
- **Zero new runtime dependencies.**
- **Testing:** Unit tests assert rendered HTML (classes, ARIA, escaping); TDD per `workflow.md`; >80% coverage.

## Acceptance Criteria
- [x] `foundation.css` exists and is loaded first via internal media; legacy token definitions removed from `gallery.css`.
- [x] All eight components exist with templates, CSS, docstrings and gallery side-cars.
- [x] Their CSS rules have been moved (not copied) out of the legacy stylesheets.
- [x] Built-ins render in their own sandbox in the example project with correct styles.
- [x] track 0 visual baseline passes; `just check` and `just test` pass.

## Out of Scope
- Using these components in the gallery templates (track 5).
