# Variant View (`dds__variant_view`)

A domain gallery component that renders the documentation, live preview stage, and template tag usage snippet for an individual component variant.

## When to Use

- Displaying a single named component variant on a variant detail page or inside a component documentation view.
- Presenting a variant's heading and categorical badge alongside optional prose notes, an isolated preview iframe (`data-surface="stage"`), a sandbox quick-link, and a copyable Django template snippet.

## Parameters

- **`variant_label` (`str` or `Variant`, optional, default `""`, positional):** Display label of the active variant rendered inside `<h2 data-variant-title>`. Falls back to `"Variant"` when empty, and automatically extracts `.label` or `.name` when given a `Variant` instance.
- **`description_html` (`str`, optional, default `""`):** Optional pre-rendered HTML description rendered inside `<div data-variant-description>`.
- **`preview_url` (`str`, optional, default `""`):** Optional URL for the variant preview `<iframe>` inside `<div data-variant-preview data-surface="stage">`.
- **`code` (`str` or `TagSignature`, optional, default `""`):** Optional template tag usage snippet rendered via `{% dds__code_block %}`. Automatically extracts `.minimal` when given a `TagSignature` object.
- **`badge_label` (`str`, optional, default `"Variant"`):** Label text passed to the leading `{% dds__badge variant="info" %}` pill.
- **`sandbox_href` (`str`, optional, default `"#pane-sandbox"`):** Target URL or anchor for the `"Open in sandbox"` icon button inside the preview stage.

## Behaviour & Accessibility

- Renders `<section class="dds-variant-view" data-surface="docs">` containing an Every Layout `<l-stack>`.
- Computes an accessible `title="<variant_label> preview"` attribute on the preview `<iframe name="variant" data-canvas-id="variant">`.
- Delegates badge, icon button, and code block rendering to `{% dds__badge %}`, `{% dds__button %}`, and `{% dds__code_block %}` with zero template filters.

## Example Usage

```django
{% load design_components %}

{% dds__variant_view "Primary Action" description_html=desc_html preview_url=canvas_url code=tag_snippet %}
{% dds__variant_view variant_label=variant code=signature sandbox_href="#pane-sandbox" %}
```
