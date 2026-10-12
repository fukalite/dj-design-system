## Client-Side Behaviour (`<dds-search-box>`)

- Reads the JSON search index from its internal `<script data-search-index>` element without querying outside its subtree.
- Pressing `/` (outside editable fields) focuses `[data-search-input]`.
- Typing filters the index and populates `[data-search-results]`, setting `data-state="open"` and `aria-expanded="true"`.
- Arrow keys navigate result options, `Enter` activates the selected option (dispatching `dds:search-select`), and `Escape` or outside click closes the results popover.
