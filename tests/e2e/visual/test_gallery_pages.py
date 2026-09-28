"""Visual regression screenshots of every gallery page type.

Each page is captured at every viewport in both gallery themes. Screenshot
names are ``<page>--<viewport>--<theme>``.
"""

import pytest

from tests.e2e.visual.conftest import GALLERY_THEMES, VIEWPORTS


pytestmark = [pytest.mark.e2e, pytest.mark.visual]

PAGES = {
    "index": "",
    "folder": "demo_nav/generic/",
    "document": "demo_nav/design_guidelines/",
    "component": "demo_components/alert/",
    # A component with further documentation (index.md) and a sub-page.
    "component-docs": "demo_nav/elements/icon/",
}


@pytest.mark.parametrize("theme", GALLERY_THEMES)
@pytest.mark.parametrize("viewport", VIEWPORTS)
@pytest.mark.parametrize("page_name", PAGES)
def test_page(gallery, screenshot_recorder, page_name, viewport, theme):
    page = gallery(PAGES[page_name], viewport=viewport, theme=theme)
    screenshot_recorder.check(page, f"{page_name}--{viewport}--{theme}")


def test_component_with_theme_selector(gallery, screenshot_recorder, settings):
    """The toolbar's component-theme selector only renders with 2+ themes."""
    settings.DJ_DESIGN_SYSTEM = {
        "GALLERY_THEMES": {
            "default": {"label": "Default"},
            "dark": {"label": "Dark"},
        },
    }
    page = gallery(PAGES["component"])
    screenshot_recorder.check(page, "component--desktop--light--theme-selector")
