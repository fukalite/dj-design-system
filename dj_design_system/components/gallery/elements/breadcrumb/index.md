# Breadcrumb (`dds__breadcrumb`)

An accessible hierarchical trail navigation primitive for displaying location context within nested collections, folders, and documentation pages.

## When to Use

- Showing the current component or document's position inside the gallery hierarchy.
- Providing quick upward navigation to parent folders or collection indexes.
- Indicating non-clickable namespace prefixes alongside linked parent directories.

## Parameters

- **`items` (`list`, optional, positional):** Ordered trail items. Recommended format is a list of typed `BreadcrumbItem` dataclass instances (`from dj_design_system.components.gallery.elements.breadcrumb import BreadcrumbItem`). Also accepts dictionaries (`{"label": "...", "url": "...", "icon": "..."}` or `"href"`), objects with `.label`, `.url`/`.href`, and `.icon` attributes, or plain strings.
- **`aria_label` (`str`, optional, default `"Breadcrumb"`):** Accessible label applied to the `<nav>` landmark.
- **`separator_icon` (`str`, optional, default `"chevron-right"`):** Icon from `ICON_NAMES` rendered at `size="xs"` between trail items.

### Data Contract (`BreadcrumbItem`)

```python
from dj_design_system.components.gallery.elements.breadcrumb import BreadcrumbItem

trail = [
    BreadcrumbItem(label="Home", url="/", icon="home"),
    BreadcrumbItem(label="Elements", url="/gallery/elements/"),
    BreadcrumbItem(label="Breadcrumb"),  # Final item: active page
]
```

## Behaviour & Accessibility

- When `items` is populated, renders `<nav class="dds-breadcrumb" aria-label="...">` wrapping `<ol class="l-cluster">`. When `items` is empty, nothing is rendered to avoid emitting an empty `<nav>` landmark.
- The final item in `items` is always normalized in `get_context()` as the active page (`is_current=True`, `url=None`) and rendered as `<span aria-current="page">`.
- Preceding items with a `url` or `href` render as `<a href="...">`; items without a URL render as `<span>`.
- When more than two items are present, intermediate crumbs (`items[1:-1]`) collapse on narrow viewports (`<= 48rem`) behind a `<dds-popout>` ellipsis trigger (`[data-breadcrumb-ellipsis]`) that opens a flyout menu (`[data-breadcrumb-flyout role="group"]`).

## Example Usage

```django
{% load design_components %}

{% dds__breadcrumb items %}
{% dds__breadcrumb items=trail aria_label="Component hierarchy" separator_icon="chevron-right" %}
```
