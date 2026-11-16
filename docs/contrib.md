# Contrib apps

`dj_design_system.contrib` holds optional apps of ready-made components built on Django objects: forms, pages of results, messages and so on. They give you building blocks for pages such as custom admin views, without writing the markup each time.

Each app is opt-in. Nothing changes until you add it to `INSTALLED_APPS`.

| App                                   | Label            | Tags                    | For                                   |
| ------------------------------------- | ---------------- | ----------------------- | ------------------------------------- |
| `dj_design_system.contrib.forms`      | `dds_forms`      | `{% dds_forms__... %}`      | `Form`, `BoundField`, fieldsets       |
| `dj_design_system.contrib.navigation` | `dds_navigation` | `{% dds_navigation__... %}` | `Page` (pagination), links, breadcrumbs |
| `dj_design_system.contrib.display`    | `dds_display`    | `{% dds_display__... %}`    | messages, dates, images               |
| `dj_design_system.contrib.data`       | `dds_data`       | `{% dds_data__... %}`       | tables and lists of data              |

## Installation

```python
INSTALLED_APPS = [
    # ...
    "dj_design_system",
    "dj_design_system.contrib.forms",
    "dj_design_system.contrib.navigation",
    "dj_design_system.contrib.display",
    "dj_design_system.contrib.data",
]
```

Install only the apps you need. Each one requires `dj_design_system`; system check `dj_design_system.E007` tells you if a required app is missing.

## Tag names

The contrib apps declare a tag prefix (see [Declaring a tag prefix](registry.md#declaring-a-tag-prefix)), so their tags always carry it, for example `{% dds_navigation__pagination %}`. They never register a short name, so they cannot clash with your own components.

## Components

### `dds_navigation__pagination`

Previous, next and numbered links for a Django `Page`, with ellipses for long ranges.

```django
{% dds_navigation__pagination page_obj query=request.GET %}
```

| Parameter          | Default        | Description                                                   |
| ------------------ | -------------- | ------------------------------------------------------------- |
| `page`             | required       | The `Page` to paginate (positional)                           |
| `query`            | `None`         | `QueryDict` or `dict` of parameters to keep in every link     |
| `page_param`       | `"page"`       | Name of the page-number query parameter                       |
| `on_each_side`     | `2`            | Links either side of the current page                         |
| `on_ends`          | `1`            | Links at the start and end of the range                       |
| `hide_single_page` | `True`         | Render nothing when there is only one page                    |
| `label`            | `"Pagination"` | Accessible name of the `<nav>` landmark                       |

It renders a `<nav>` with a `<ul>` of links, `aria-current="page"` on the current page, `rel="prev"`/`rel="next"` on the arrows, and a disabled `<span>` when there is no previous or next page.

## Styling

The components are unstyled for now. They render plain, semantic HTML and accept CSS classes and attributes like any other component, so you can style them from your own stylesheet.

## Extending

Subclass a contrib component to change its template or defaults, in your own app:

```python
from dj_design_system.contrib.navigation.components.pagination import (
    PaginationComponent,
)


class MyPagination(PaginationComponent):
    template_name = "myapp/pagination.html"
```

Remember that `Meta` is not inherited, so set `Meta.name` again if you need one.
