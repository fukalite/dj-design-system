## Client-Side Behaviour (`<dds-theme-select>`)

The `{% dds__theme_select %}` component renders an accessible theme switcher popout.

- Queries `[data-theme-select]` strictly within its own Light DOM subtree.
- Updates `data-active-theme` on `<dds-theme-select>`, persists the selected theme, and dispatches a bubbling `dds:theme-change` `CustomEvent` when the selection changes.
