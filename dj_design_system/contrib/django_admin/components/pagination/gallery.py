"""Gallery variants for dds_admin__pagination."""

from collections.abc import Callable

from django.core.paginator import Page, Paginator

from dj_design_system import gallery
from dj_design_system.data import GalleryParameter


def page_of(count: int, number: int) -> Callable[[], Page]:
    """Return page ``number`` of ``count`` rows, 100 per page like the admin."""
    return lambda: Paginator(range(count), 100).page(number)


config = gallery.GalleryConfig(
    variants=[
        gallery.Variant(
            name="basic",
            label="Change list pages",
            kwargs={
                "page": GalleryParameter(value=page_of(1240, 3), code="page_obj"),
                "summary": "1240 books",
            },
        ),
        gallery.Variant(
            name="maximal",
            label="With Show all",
            description="The admin offers Show all when the list is short enough.",
            kwargs={
                "page": GalleryParameter(value=page_of(450, 1), code="page_obj"),
                "summary": "450 books",
                "show_all_url": "?all=",
                "label": "Pagination books",
            },
        ),
        gallery.Variant(
            name="single_page",
            label="One page",
            description="Only the count is shown, as in the stock admin.",
            kwargs={
                "page": GalleryParameter(value=page_of(12, 1), code="page_obj"),
                "summary": "12 books",
            },
        ),
    ]
)
