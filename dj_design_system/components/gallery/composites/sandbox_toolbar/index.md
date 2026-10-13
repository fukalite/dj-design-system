## Client-Side Behaviour (`<dds-sandbox-toolbar>`)

The `{% dds__sandbox_toolbar %}` component renders an accessible toolbar (`<dds-sandbox-toolbar>`) for controlling the sandbox preview canvas. It exports the `SandboxControlOption` dataclass alongside `SandboxToolbar` for typed control option entries.

- **Semantic Events**: Dispatches `dds:sandbox-bg`, `dds:sandbox-viewport`, `dds:sandbox-zoom`, `dds:sandbox-variant`, `dds:sandbox-toggle`, and `dds:sandbox-reset` without directly reading/writing `sessionStorage` or mutating `window.location`.
- **Programmatic State (`applyState`)**: Exposes `applyState(state)` to synchronise child `<dds-popout>` selections via `selectValue(value)` and update `[data-action]` toggle `aria-pressed` states.
