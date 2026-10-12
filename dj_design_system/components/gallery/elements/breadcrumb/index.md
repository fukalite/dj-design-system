## Data Contract (`BreadcrumbItem`)

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
