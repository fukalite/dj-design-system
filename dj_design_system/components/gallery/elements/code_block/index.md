## Client-Side Behaviour (`<dds-code-block>`)

- Queries `[data-copy-trigger]`, `[data-code-content]`, and `[data-copy-status]` strictly within its own Light DOM subtree.
- Clicking `[data-copy-trigger]` writes the text content of `[data-code-content]` to `navigator.clipboard.writeText()`, sets `data-copied="true"` on `<dds-code-block>`, updates `[data-copy-status]` to `"Copied"`, and dispatches a bubbling `dds:copy` `CustomEvent` with `detail: { code }`.
- Cleans up event listeners via an instance `AbortController` and clears any pending status reset timer in `disconnectedCallback()`.
