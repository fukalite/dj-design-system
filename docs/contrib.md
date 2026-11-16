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

## Django admin

`dj_design_system.contrib.django_admin` (tags `{% dds_admin__... %}`) holds admin-styled versions of the generic components, in a "Django plus" look: it uses the admin's own markup and CSS classes and adds small refinements, such as Previous and Next links on the paginator. Use the components to build custom admin pages, or let an admin site use them for its shared partials.

```python
INSTALLED_APPS = [
    "dj_design_system.contrib.django_admin",  # above django.contrib.admin
    "django.contrib.admin",
    # ...
    "dj_design_system",
    "dj_design_system.contrib.navigation",
]
```

It must come before `django.contrib.admin` (check `dj_design_system.E008`) and needs `dj_design_system.contrib.navigation` (check `E007`).

### Turning it on per admin site

Installing the app changes nothing on its own. An admin site opts in by using `DesignSystemAdminSite` (or `DesignSystemAdminSiteMixin` on your own `AdminSite` subclass):

```python
from dj_design_system.contrib.django_admin.sites import DesignSystemAdminSite

site = DesignSystemAdminSite(name="dds_admin")
site.register(Book, BookAdmin)

urlpatterns = [path("admin/", site.urls)]
```

Every other site, including Django's default `admin.site`, keeps Django's templates, so you can run both side by side and compare. Django's admin views, page templates, JavaScript and CSS are always kept. Only shared partials are swapped, through small shim templates in `templates/admin/`. A project or per-model override of the same template still wins.

Partials swapped so far:

| Template                | Component               |
| ----------------------- | ----------------------- |
| `admin/pagination.html` | `dds_admin__pagination` |

### `dds_admin__pagination`

Subclass of `dds_navigation__pagination`. Extra parameters: `cl` (the `ChangeList`, so links keep its filters, search and ordering), `summary` (such as `"120 books"`), `show_all_url` and `show_links`. It shows the summary even for a single page, as the stock admin does.
