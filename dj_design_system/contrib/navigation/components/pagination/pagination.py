"""Pagination links for a Django ``Page``."""

from dataclasses import dataclass
from typing import Any, cast

from django.core.paginator import Page
from django.http import QueryDict
from django.utils.http import urlencode
from django.utils.translation import gettext

from dj_design_system import components, parameters


@dataclass(frozen=True)
class PaginationItem:
    """One entry in the page range: a page link or an ellipsis."""

    label: str
    number: int | None = None
    url: str = ""
    is_current: bool = False

    @property
    def is_ellipsis(self) -> bool:
        return self.number is None


class PaginationComponent(components.TagComponent):
    """Previous, next and numbered page links for a Django ``Page``.

    Long page ranges are shortened with ellipses using
    ``Paginator.get_elided_page_range``. Pass the current query string as
    ``query`` (usually ``request.GET``) to keep filters and searches in every
    link. Renders nothing when there is only one page, unless
    ``hide_single_page`` is ``False``.

    The markup is plain and unstyled: a ``<nav>`` landmark holding a list of
    links, with ``aria-current="page"`` on the current page.

    Usage::

        {% dds_navigation__pagination page_obj query=request.GET %}
    """

    page = parameters.InstanceParam(Page, "The page of results to paginate.")
    query = parameters.InstanceParam(
        (QueryDict, dict),
        "Query parameters to keep in every link, usually request.GET.",
        required=False,
    )
    page_param = parameters.StrParam(
        "Name of the query parameter that holds the page number.",
        required=False,
        default="page",
    )
    on_each_side = parameters.IntParam(
        "Page links to show either side of the current page.",
        required=False,
        default=2,
    )
    on_ends = parameters.IntParam(
        "Page links to show at the start and end of the range.",
        required=False,
        default=1,
    )
    hide_single_page = parameters.BoolParam(
        "Render nothing when there is only one page.",
        required=False,
        default=True,
    )
    label = parameters.StrParam(
        'Accessible name of the navigation landmark. Defaults to a translated "Pagination".',
        required=False,
    )

    class Meta:
        positional_args = ["page"]

    @property
    def current_page(self) -> Page:
        """The ``page`` parameter, typed for the methods below."""
        return cast(Page, self.page)

    def setting(self, name: str) -> Any:
        """Return parameter ``name``, falling back to its default when unset.

        Passing ``None`` (or an empty string) explicitly would otherwise
        leave the attribute empty.
        """
        value = getattr(self, name)
        if value is None or value == "":
            return type(self).get_params()[name].default
        return value

    def page_url(self, number: int) -> str:
        """Return the query string link for page ``number``."""
        page_param = str(self.setting("page_param"))
        if isinstance(self.query, QueryDict):
            query = self.query.copy()
            query[page_param] = str(number)
            return f"?{query.urlencode()}"
        query_dict: dict[str, Any] = dict(self.query or {})
        query_dict[page_param] = number
        return f"?{urlencode(query_dict, doseq=True)}"

    def get_items(self) -> list[PaginationItem]:
        """Return one entry per page link or ellipsis, in order."""
        page = self.current_page
        items: list[PaginationItem] = []
        for number in page.paginator.get_elided_page_range(
            page.number,
            on_each_side=self.setting("on_each_side"),
            on_ends=self.setting("on_ends"),
        ):
            if not isinstance(number, int):
                items.append(PaginationItem(label=str(number)))
                continue
            items.append(
                PaginationItem(
                    label=str(number),
                    number=number,
                    url=self.page_url(number),
                    is_current=number == page.number,
                )
            )
        return items

    def get_context(self) -> dict[str, Any]:
        context = super().get_context()
        page = self.current_page
        context["label"] = self.label or gettext("Pagination")
        context["is_hidden"] = bool(
            self.hide_single_page and page.paginator.num_pages <= 1
        )
        if context["is_hidden"]:
            return context
        context["items"] = self.get_items()
        context["previous_url"] = (
            self.page_url(page.previous_page_number()) if page.has_previous() else ""
        )
        context["next_url"] = (
            self.page_url(page.next_page_number()) if page.has_next() else ""
        )
        return context
