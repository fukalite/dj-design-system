# Breadcrumb (`dds__breadcrumb`)

An accessible hierarchical trail navigation primitive for displaying location context within nested collections, folders, and documentation pages.

## When to Use

- Showing the current component or document's position inside the gallery hierarchy.
- Providing quick upward navigation to parent folders or collection indexes.
- Indicating non-clickable namespace prefixes alongside linked parent directories.

## Parameters

- **`items` (`list`, optional, positional):** Ordered trail items. Each entry can be a dictionary (`{"label": "...", "url": "...", "icon": "..."}` or `"href"`), an object with `.label`, `.url`/`.href`, and `.icon` attributes, or a plain string.
- **`aria_label` (`str`, optional, default `"Breadcrumb"`):** Accessible label applied to the `<nav>` landmark.
- **`separator_icon` (`str`, optional, default `"chevron-right"`):** Icon from `ICON_NAMES` rendered at `size="xs"` between trail items.

## Behaviour & Accessibility

- Renders `<nav class="dds-breadcrumb" aria-label="...">` wrapping `<ol class="l-cluster">`.
- The final item in `items` is always normalized in `get_context()` as the active page (`is_current=True`, `url=None`) and rendered as `<span aria-current="page">`.
- Preceding items with a `url` or `href` render as `<a href="...">`; items without a URL render as `<span>`.

## Example Usage

```django
{% load design_components %}

{% dds__breadcrumb items %}
{% dds__breadcrumb items=trail aria_label="Component hierarchy" separator_icon="chevron-right" %}
```
