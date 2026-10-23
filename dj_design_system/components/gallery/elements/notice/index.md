# Notice (`dds__notice`)

The `dds__notice` block component renders a callout banner (`<div class="dds-notice">`) with an inline status icon, optional heading, and body content.

## When to Use

- Highlighting informational notes, tips, or configuration guidance in documentation pages.
- Displaying positive confirmation messages (`success`) after an operation succeeds.
- Surfacing deprecation notices or non-blocking cautions (`warning`).
- Presenting validation failures or rendering errors (`error`).

## Accessibility

- `info` and `success` variants render with `role="note"`.
- `warning` and `error` variants automatically upgrade to `role="alert"` so assistive technologies announce urgent messages.
- Use `role="note"` to override static or passive warnings that should not act as interrupting live regions.
- The leading status icon is decorative (`aria-hidden="true"`) because the notice heading and prose convey the message semantics.

## Variants

| Variant | Default Icon | ARIA Role | Purpose |
| :--- | :--- | :--- | :--- |
| `info` | `info` | `note` | Default informational callout or tip. |
| `success` | `success` | `note` | Positive confirmation or verified state. |
| `warning` | `warning` | `alert` | Caution or deprecation notice. |
| `error` | `error` | `alert` | Critical error or blocker alert. |

## Template Usage

```django
{% dds__notice variant="info" title="Note" %}
  Component changes are reflected automatically in the preview canvas.
{% enddds__notice %}

{% dds__notice variant="warning" title="Deprecated" role="note" %}
  Please migrate to <strong>new parameter definitions</strong> before next release.
{% enddds__notice %}

{% dds__notice variant="error" title="Rendering Error" icon="code" %}
  Failed to compile the component template.
{% enddds__notice %}

{# Suppress icon for compact or unadorned notices #}
{% dds__notice variant="info" icon="none" %}
  A minimal inline callout without an icon.
{% enddds__notice %}
```
