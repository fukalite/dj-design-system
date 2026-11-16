"""Gallery variants for dds_navigation__pagination."""

from django.core.paginator import Paginator
from django.http import QueryDict

from dj_design_system import gallery
from dj_design_system.data import GalleryParameter


def page_of(count: int, number: int):
    """Return page ``number`` of ``count`` items, ten per page."""
    return lambda: Paginator(range(count), 10).page(number)


config = gallery.GalleryConfig(
    variants=[
        gallery.Variant(
            name="basic",
            label="Few pages",
            description="Five pages, on the second.",
            kwargs={"page": GalleryParameter(value=page_of(50, 2), code="page_obj")},
        ),
        gallery.Variant(
            name="maximal",
            label="Long range, keeping the query",
            description="Fifty pages, on page 25. Ellipses shorten the range and "
            "every link keeps `?q=report&sort=-date`.",
            kwargs={
                "page": GalleryParameter(value=page_of(500, 25), code="page_obj"),
                "query": GalleryParameter(
                    value=lambda: QueryDict("q=report&sort=-date&page=25"),
                    code="request.GET",
                ),
                "on_each_side": 1,
                "label": "Search results pages",
            },
        ),
        gallery.Variant(
            name="first_page",
            label="First page",
            description="Previous is shown as disabled text.",
            kwargs={"page": GalleryParameter(value=page_of(80, 1), code="page_obj")},
        ),
    ]
)
