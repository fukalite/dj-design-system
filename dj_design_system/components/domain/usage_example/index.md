# Usage Example (`dds__usage_example`)

A domain gallery component that renders a component usage example block combining an optional section heading, an optional isolated preview stage iframe (with an "Open in sandbox" action button), and a formatted template tag code snippet.

## When to Use

- Displaying minimal, maximal, or variant usage examples on a component documentation page.
- Pairing a live component canvas preview (`<iframe>` on `data-surface="stage"`) with its corresponding copyable `dds__code_block` template tag invocation.
- Rendering standalone template tag snippets when an interactive preview URL is omitted.

## Parameters

- **`title` (`str`, optional, default `""`, positional):** Heading for the usage example block rendered inside `<h4 data-usage-title>` when non-empty.
- **`code` (`str`, optional, default `""`, positional):** Raw template tag usage snippet string (or a `TagSignature` object normalised via its `.minimal` attribute) passed to `dds__code_block` when non-blank.
- **`preview_url` (`str`, optional, default `""`):** Optional iframe preview URL. When non-empty, renders `<div data-usage-preview data-surface="stage">` containing the preview `<iframe>`.
- **`canvas_id` (`str`, optional, default `"preview"`):** Identifier applied to the preview iframe's `name` and `data-canvas-id` attributes (e.g. `"minimal"`, `"maximal"`, `"variant"`).
- **`sandbox_href` (`str`, optional, default `"#pane-sandbox"`):** Link anchor for the "Open in sandbox" icon button inside the preview stage. Pass `""` to hide the sandbox link button.
- **`language` (`str`, optional, default `"django"`):** Code language identifier forwarded to `dds__code_block`.

## Behaviour & Accessibility

- Renders `<section class="dds-usage-example">` wrapping an Every Layout `<l-stack>`.
- Computes an accessible `title` attribute on the `<iframe>` (`"<title> preview"` when `title` is provided, or `"Component example preview"` otherwise).
- Renders the sandbox link via `{% dds__button label="Open in sandbox" icon="external-link" icon_only=True variant="ghost" size="sm" href=sandbox_href %}` so screen readers announce `"Open in sandbox"` via `aria-label`.

## Example Usage

```django
{% load design_components %}

{% dds__usage_example "Minimal example" signature.minimal preview_url=minimal_canvas_url canvas_id="minimal" %}
{% dds__usage_example title="Maximal example" code=signature.maximal preview_url=maximal_canvas_url canvas_id="maximal" %}
```
