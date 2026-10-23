# Badge (`dds__badge`)

The `dds__badge` element renders a compact inline pill (`<span class="dds-badge">`) for status labels, parameter metadata, and technical type annotations.

## When to Use

- Highlighting parameter requirements (`Required`, `Optional`) in parameter tables.
- Displaying parameter data types (`str`, `bool`, `int`) using the `code` variant.
- Indicating semantic status (`info`, `success`, `warning`, `error`) in headers, lists, and cards.

## Variants

| Variant | Purpose |
| :--- | :--- |
| `neutral` | Default subtle badge styled with control surface tokens. |
| `info` | Informational status pill. |
| `success` | Positive or active status pill. |
| `warning` | Caution or deprecation status pill. |
| `error` | High-priority status or required indicator pill. |
| `code` | Monospace technical pill for type names and identifiers. |

## Template Usage

```django
{% dds__badge "Optional" %}
{% dds__badge "Info" variant="info" %}
{% dds__badge "Active" variant="success" %}
{% dds__badge "Deprecated" variant="warning" %}
{% dds__badge "Required" variant="error" %}
{% dds__badge "str" variant="code" %}
```
