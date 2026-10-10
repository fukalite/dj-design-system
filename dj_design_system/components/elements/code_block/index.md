# Code Block (`dds__code_block`)

The `dds__code_block` tag component renders formatted source code inside a `<dds-code-block>` Light DOM custom element on the `code` surface (`data-surface="code"`), complete with `<pre>`/`<code>` typography resets, an optional header bar, and one-click copy-to-clipboard support.

## When to Use

- Displaying Django template tag invocations (`language="django"`) in component gallery documentation and usage examples.
- Presenting Python, CSS, HTML, or shell snippets with consistent monospace formatting (`white-space: pre`, `tab-size: 4`, `font-variant-ligatures: none`).
- Providing one-click clipboard copy functionality with accessible status feedback (`Copy` → `Copied`) and bubbling `dds:copy` custom events.

## Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `code` | `str` | *(required)* | Source code snippet to render (positional argument 0). Leading and trailing newlines are stripped and syntax-highlighted via Pygments. |
| `language` | `str` | `"django"` | Code language identifier exposed via `data-language` and used for Pygments lexer selection. |
| `title` | `str` | `""` | Optional header title or filename. When set, renders a full `<header>` bar with `[data-code-label]`. |
| `copyable` | `bool` | `True` | Whether to render the `[data-copy-trigger]` copy-to-clipboard button (inside `<header>` when `title` is set, or as a compact `[data-copy-overlay]` button when `title` is omitted). |

## Client-Side Behaviour (`<dds-code-block>`)

- Queries `[data-copy-trigger]`, `[data-code-content]`, and `[data-copy-status]` strictly within its own Light DOM subtree.
- Clicking `[data-copy-trigger]` writes the text content of `[data-code-content]` to `navigator.clipboard.writeText()`, sets `data-copied="true"` on `<dds-code-block>`, updates `[data-copy-status]` to `"Copied"`, and dispatches a bubbling `dds:copy` `CustomEvent` with `detail: { code }`.
- Cleans up event listeners via an instance `AbortController` and clears any pending status reset timer in `disconnectedCallback()`.

## Template Usage

```django
{% load design_components %}

{% dds__code_block "{% dds__button 'Save' variant='primary' %}" %}

{% dds__code_block code=snippet language="python" title="components/card.py" %}

{% dds__code_block code="just check" language="bash" copyable=False %}
```
