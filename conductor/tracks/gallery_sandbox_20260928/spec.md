# Gallery Rebuild 4 — Sandbox & Canvas Components

## Overview
Part of the gallery rebuild series (see `gallery_visual_baseline_20260928` for the full list). This track builds the built-in components for the component page's interactive half: the canvas widget, usage examples, parameter table, parameter form and sandbox toolbar.

**Depends on:** `gallery_foundation_20260928`, `gallery_primitives_20260928`, `gallery_nav_layout_20260928`.

Follows the conventions defined in `gallery_primitives_20260928/spec.md`.

## Functional Requirements

### 1. Canvas & Documentation Components
| Component | Type | Replaces |
| --- | --- | --- |
| `CanvasWidget` | Tag | `canvas_widget.html`: CSS-only preview / template source / output HTML toggle around an iframe. Params: `unique_id`, `iframe_src` or `iframe_srcdoc`, `iframe_class`, `sandbox_attrs`, `source_html`, `rendered_output_html`, `extra_classes`. Composes `Icon` and `CodeBlock`. |
| `UsageExample` | Tag | `.gallery-usage__block`: heading, optional live preview iframe with an "open in sandbox" `IconButton`, and code block. |
| `ParamsTable` | Tag | Documentation parameters table (name, type, required, default, choices, description). Composes `Table`. |

### 2. Sandbox Components
| Component | Type | Replaces |
| --- | --- | --- |
| `ParamsForm` | Block | `.gallery-params-form` with HTMX attributes (`hx-get`, `hx-target`, `hx-swap`, `hx-trigger`) and the hidden theme input. Includes the resizable drawer wrapper (`data-gallery-drawer`, `data-gallery-resizer`). |
| `FormRow` | Tag | `.gallery-params-form__row`: label, hint, bound field and error list. Takes a Django `BoundField`. |
| `SandboxToolbar` | Block | `.gallery-sandbox-toolbar` container, including `data-measure-script`. |
| `Popout` | Block | Toolbar toggle button with its popout panel (`aria-expanded`, `aria-controls`, `hidden`). Params: `panel_id`, `panel_name`, `title`, `toggle_class`. Toggle content is a slot. |
| `PopoutOption` | Block | `.gallery-sandbox-toolbar__popout-option` with an active state and `data-*` value attribute. |
| `ToggleButton` | Tag | Pressed-state toolbar buttons (outline, measure, RTL). Composes `Button` and `Icon`. |

### 3. Splitting `gallery-toolbar.js`
- The 671-line `gallery-toolbar.js` is split so each component owns its behaviour:
  - `Popout`: open/close, outside-click and Escape handling, focus management.
  - Background, viewport and zoom handlers: attached by `SandboxToolbar`, using `data-gallery-panel`.
  - `ToggleButton`: outline, measure (lazy-loads `gallery-measure.js`) and RTL handlers.
  - Drawer resizing: `ParamsForm`.
  - Iframe resize messaging: `CanvasWidget`, together with the parent side of `canvas-resize.js`.
- State persistence (e.g. localStorage keys) and the `postMessage` protocol with the canvas iframe must be unchanged.
- Behaviour must survive HTMX swaps of the sandbox body. Handlers bind by delegation or re-initialise on `htmx:afterSwap`, as the current script does.

### 4. Canvas Iframe Stays a Plain Template
`templates/dj_design_system/canvas/iframe.html` hosts **consumer** components and must stay free of gallery component CSS/JS. It is not converted to components.

## Non-Functional Requirements
- **No visual or behavioural change:** The track 0 visual baseline and existing e2e sandbox tests pass.
- **HTMX:** Sandbox updates via HTMX continue to work, including URL replacement and toolbar state retention across swaps.
- **Testing:** TDD per `workflow.md`; >80% coverage; e2e tests for each toolbar control.

## Acceptance Criteria
- [ ] All nine components exist with templates, CSS/JS, docstrings and gallery side-cars.
- [ ] `gallery-toolbar.js` and `gallery-toolbar.css` are fully redistributed into component assets.
- [ ] Toolbar state, iframe messaging and HTMX swaps behave exactly as before.
- [ ] `canvas/iframe.html` contains no gallery component assets.
- [ ] The track 0 visual baseline passes; `just check`, `just test` and `just e2e` pass.

## Out of Scope
- Using these components in the gallery templates (track 5).
- New sandbox features.
