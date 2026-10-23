# Specification: Built-in `domain` Collection — Sandbox, Controls & Canvas

## Overview
Implements the interactive component sandbox, parameter controls form, resizable split pane, and isolated canvas preview widget in `dj_design_system/components/domain/<name>/`.

## Functional Requirements
1. **Interactive Sandbox & Controls (`dj_design_system/components/domain/`):**
   - `split_pane` (`{% dds__split_pane %}` + `<dds-split-pane>`): Resizable two-pane layout separating the preview stage (`data-surface="stage"`) and the parameter inspector (`data-surface="sandbox"`), with pointer drag and keyboard resize support.
   - `sandbox_toolbar` (`{% dds__sandbox_toolbar %}`): Toolbar composing `{% dds__popout %}`, `{% dds__button %}`, and `{% dds__icon %}` for viewport width presets, canvas background selection, theme selection, reset, and new-tab/fullscreen actions.
   - `params_form` (`{% dds__params_form %}` + `<dds-params-form>`): Live parameter editor form composing `{% dds__form_field %}` that serialises control changes and dispatches `dds:params-change`.
2. **Isolated Canvas Widget (`dj_design_system/components/domain/`):**
   - `canvas_widget` (`{% dds__canvas_widget %}` + `<dds-canvas-widget>`): Isolated preview `<iframe>` container with automatic height resizing, viewport width constraints, background/theme synchronisation, and collapsible source code drawer (`data-surface="code"` composing `{% dds__code_block %}`).

## Acceptance Criteria
- All components in `dj_design_system/components/domain/{split_pane,sandbox_toolbar,params_form,canvas_widget}/` adhere strictly to `conductor/code_styleguides/dds-components.md`:
  - 100% co-located directory (`<name>.py`, `<name>.html`, `<name>.css`, `<name>.ts`, `gallery.py`, `index.md`).
  - Light DOM `<dds-*>` custom elements written in TypeScript with strict `this.querySelector` scoping, upward `CustomEvent` communication, and `AbortController` listener cleanup.
  - Zero BEM (`__` or `--`) in CSS/HTML; Tier 3 `--_<component>-*` tokens mapped exclusively from Tier 2 `--dds-*` tokens.
