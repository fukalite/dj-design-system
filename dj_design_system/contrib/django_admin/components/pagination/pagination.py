"""Admin-styled pagination built on the generic ``dds_navigation__pagination``."""

from __future__ import annotations

from typing import Any

from dj_design_system import parameters
from dj_design_system.contrib.navigation.components.pagination.pagination import (
    PaginationComponent,
)


class AdminPaginationComponent(PaginationComponent):
    """Pagination for admin change lists, in the "Django plus" look.

    Uses Django admin's own ``paginator`` markup and classes, so it picks up
    the admin's CSS, and adds Previous and Next links. The range defaults
    match the stock admin (3 links either side, 2 at each end). Pass ``cl`` (the admin
    ``ChangeList``) to build links with ``cl.get_query_string``, keeping the
    list's filters, search and ordering.

    Usage::

        {% dds_admin__pagination page_obj summary="120 books" %}
    """

    cl = parameters.InstanceParam(
        "django.contrib.admin.views.main.ChangeList",
        "The admin change list. Links then keep its filters and ordering.",
        required=False,
    )
    summary = parameters.StrParam(
        'Text after the links, such as "120 books".',
        required=False,
        default="",
    )
    show_all_url = parameters.StrParam(
        'Link for the "Show all" button. Leave empty to hide it.',
        required=False,
        default="",
    )
    show_links = parameters.BoolParam(
        "Show the page links. The admin hides them when showing all rows.",
        required=False,
        default=True,
    )
    on_each_side = parameters.IntParam(
        "Page links to show either side of the current page.",
        required=False,
        default=3,
    )
    on_ends = parameters.IntParam(
        "Page links to show at the start and end of the range.",
        required=False,
        default=2,
    )
    hide_single_page = parameters.BoolParam(
        "Render nothing when there is only one page.",
        required=False,
        default=False,
    )

    class Meta:
        name = "pagination"
        positional_args = ["page"]

    def page_url(self, number: int) -> str:
        if self.cl is not None:
            from django.contrib.admin.views.main import PAGE_VAR

            return self.cl.get_query_string({PAGE_VAR: number})
        return super().page_url(number)

    def get_context(self) -> dict[str, Any]:
        context = super().get_context()
        multi_page = self.current_page.paginator.num_pages > 1
        context["show_links"] = bool(self.show_links) and multi_page
        return context
