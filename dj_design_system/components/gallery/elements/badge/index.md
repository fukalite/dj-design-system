# Badge (`dds__badge`)

The `dds__badge` element renders a compact inline pill (`<span class="dds-badge">`) for status labels, parameter metadata, and technical type annotations.

## When to Use

- Highlighting parameter requirements (`Required`, `Optional`) in parameter tables.
- Displaying parameter data types (`str`, `bool`, `int`) using the `code` variant.
- Indicating semantic status (`info`, `success`, `warning`, `error`) in headers, lists, and cards.

## Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `label` | `str` | *(required)* | Badge text content (positional argument 1). |
| `variant` | `str` | `"neutral"` | Semantic status style (`neutral`, `info`, `success`, `warning`, `error`). |
| `is_code` | `bool` | `False` | Render badge text in semantic `<code>` with monospace typography. |

## Variants

| Variant | Purpose |
| :--- | :--- |
| `neutral` | Default subtle badge styled with control surface tokens. |
| `info` | Informational status pill. |
| `success` | Positive or active status pill. |
| `warning` | Caution or deprecation status pill. |
| `error` | High-priority status or required indicator pill. |

## Template Usage

```django
{% dds__badge "Optional" %}
{% dds__badge "Info" variant="info" %}
{% dds__badge "Active" variant="success" %}
{% dds__badge "Deprecated" variant="warning" %}
{% dds__badge "Required" variant="error" %}
{% dds__badge "str" is_code=True %}
{% dds__badge "DeprecatedType" variant="warning" is_code=True %}
```
