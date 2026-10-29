## Client-Side Behaviour (`<dds-popout>`)

- Clicking `[data-popout-trigger]` toggles `data-state` (`"open"` / `"closed"`), `aria-expanded`, and `menu.hidden`.
- Pressing `Escape` or clicking outside `<dds-popout>` closes the menu and returns focus to the active trigger element.
- Clicking an enabled `[data-popout-option]` dispatches a bubbling `dds:popout-select` `CustomEvent` with `detail: { value, label }` and closes the menu.
- If the clicked option has `role="menuitemradio"`, radio group selection and the `[data-popout-trigger] > span` trigger label are updated automatically. Calling `selectValue(value)` programmatically synchronises `aria-checked` and `[data-popout-trigger] > span` without piercing internal DOM from parent components. If `role="menuitemcheckbox"`, checked state toggles. Links and standard action `role="menuitem"` elements do not receive `aria-checked`.
