# Prose (`dds__prose`)

`dds__prose` is the built-in domain component responsible for rendering trusted HTML prose (such as compiled Markdown from `index.md` files and standalone documentation pages) on the `docs` surface.

## When to Use

- Rendering Markdown documentation pages (`document` view) or component overview docs inside `dds__variant_view`.
- Presenting long-form technical writing with consistent typographic hierarchy (`h1`–`h4`, `p`, `ul`, `ol`, `li`, `a`, `code`, `pre`, `blockquote`, `table`, `hr`) and comfortable reading width (`--dds-layout-prose-measure`).

## Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `html` | `str` | `""` | Optional pre-rendered HTML prose string (trusted Markdown output). Also accepted as the first positional argument. |
| `title` | `str` | `""` | Optional document or section heading title (`<h1 data-prose-title>`). |
| `measure` | `bool` | `True` | Whether to constrain reading width to `--dds-layout-prose-measure` (`data-measure="constrained"`). |

## Variants

- **`basic`**: Default constrained prose surface with a document title and standard typographic elements.
- **`rich_elements`**: Demonstrates tables, preformatted code blocks, blockquotes, links, and section dividers.
- **`unconstrained`**: Disables the `65ch` reading width constraint (`measure=False`) for wide documentation layouts.

## Example Usage

```django
{% load design_components %}

{% dds__prose html=doc_html title="Getting Started" %}
{% enddds__prose %}

{% dds__prose title="Inline Notes" measure=False %}
  <p>Block content fallback when <code>html</code> parameter is omitted.</p>
{% enddds__prose %}
```
