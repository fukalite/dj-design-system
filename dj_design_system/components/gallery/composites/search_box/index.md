## Client-Side Behaviour (`<dds-search-box>`)

- Reads the JSON search index from its internal `<script data-search-index>` element without querying outside its subtree.
- Exposes `focusInput()` so shell managers can focus `[data-search-input]` in response to global shortcuts (`/` or `⌘K`/`Ctrl+K`).
- Typing filters the index and populates `[data-search-results]`, setting `data-state="open"` and `aria-expanded="true"`.
- Arrow keys navigate result options, updating `aria-activedescendant` and scrolling the active option into view (`scrollIntoView({ block: 'nearest' })`), `Enter` activates the selected option (dispatching `dds:search-select`), and `Escape` or outside click closes the results popover.
