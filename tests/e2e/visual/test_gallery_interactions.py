"""Visual regression screenshots of the gallery's interactive states.

Captured in the light theme. Screenshot names are
``<page>--<viewport>--<state>``.
"""

import pytest

from tests.e2e.visual.capture import stabilise


pytestmark = [pytest.mark.e2e, pytest.mark.visual]

COMPONENT = "demo_components/alert/"
# Four crumbs (Gallery / Demo nav / Elements / Icon), so the collapsed
# breadcrumb shows an ellipsis on narrow viewports.
DEEP_COMPONENT = "demo_nav/elements/icon/"


def _settle(page):
    """Re-stabilise after an interaction changed the page."""
    stabilise(page)
    return page


def test_mobile_sidebar_open(gallery, screenshot_recorder):
    page = gallery(viewport="mobile")
    page.click(".gallery-hamburger")
    screenshot_recorder.check(_settle(page), "index--mobile--sidebar-open")


def test_mobile_breadcrumb_flyout_open(gallery, screenshot_recorder):
    page = gallery(DEEP_COMPONENT, viewport="mobile")
    page.click(".gallery-breadcrumb__ellipsis")
    screenshot_recorder.check(
        _settle(page), "component-docs--mobile--breadcrumb-flyout"
    )


def test_mobile_sandbox_tab(gallery, screenshot_recorder):
    page = gallery(COMPONENT, viewport="mobile")
    page.click("label[for='gallery-tab-sandbox']")
    screenshot_recorder.check(_settle(page), "component--mobile--sandbox-tab")


def test_search_results(gallery, screenshot_recorder):
    page = gallery()
    page.fill("#gallery-search-input", "button")
    page.wait_for_selector("#gallery-search-results:not([hidden])")
    screenshot_recorder.check(_settle(page), "index--desktop--search-results")


@pytest.mark.parametrize("popout", ["bg", "viewport", "zoom"])
def test_sandbox_toolbar_popout_open(gallery, screenshot_recorder, popout):
    page = gallery(COMPONENT, viewport="wide")
    page.click(f".gallery-sandbox-toolbar__{popout}-toggle")
    page.wait_for_selector(f"[data-gallery-panel='{popout}']:not([hidden])")
    screenshot_recorder.check(_settle(page), f"component--wide--{popout}-popout")


@pytest.mark.parametrize("toggle", ["outline", "rtl"])
def test_sandbox_toolbar_toggle_active(gallery, screenshot_recorder, toggle):
    page = gallery(COMPONENT, viewport="wide")
    button = f".gallery-sandbox-toolbar__{toggle}-toggle"
    page.click(button)
    page.wait_for_selector(f"{button}[aria-pressed='true']")
    screenshot_recorder.check(_settle(page), f"component--wide--{toggle}-on")
