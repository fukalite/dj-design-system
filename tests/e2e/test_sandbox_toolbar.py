"""Characterisation tests for the sandbox toolbar and parameter drawer.

These pin the current behaviour of ``gallery-toolbar.js`` before it is split
into component-owned scripts (gallery rebuild track 4), so the split can be
checked against them. They describe what the gallery does today, not what it
should do: there is no Escape handling for popouts yet, for example.
"""

import pytest


pytestmark = pytest.mark.e2e

COMPONENT = "demo_components/alert/"
POPOUTS = ["bg", "viewport", "zoom"]

IFRAME = "document.querySelector('.gallery-sandbox__iframe')"
WRAPPER = f"{IFRAME}.contentDocument.querySelector('.canvas-wrapper')"


def _wait_for_canvas(page):
    page.wait_for_function(
        f"""() => {{
            const f = {IFRAME};
            return f && f.contentDocument
                && f.contentDocument.readyState === 'complete'
                && f.contentDocument.querySelector('.canvas-wrapper');
        }}"""
    )


@pytest.fixture()
def sandbox(page, live_server):
    """A component page wide enough to show the sandbox beside the docs."""
    page.set_viewport_size({"width": 1900, "height": 1000})
    page.goto(f"{live_server.url}/dds/{COMPONENT}")
    _wait_for_canvas(page)
    return page


def _panel(page, name):
    return page.locator(f"[data-gallery-panel='{name}']")


def _toggle(page, name):
    return page.locator(f".gallery-sandbox-toolbar__{name}-toggle")


def _choose(page, popout, value):
    _toggle(page, popout).click()
    _panel(page, popout).locator(f"[data-{popout}='{value}']").click()


def _active_options(page, popout):
    return _panel(page, popout).locator(
        ".gallery-sandbox-toolbar__popout-option--active"
    )


class TestPopouts:
    @pytest.mark.parametrize("name", POPOUTS)
    def test_toggle_opens_and_closes(self, sandbox, name):
        toggle, panel = _toggle(sandbox, name), _panel(sandbox, name)
        assert panel.is_hidden()
        assert toggle.get_attribute("aria-expanded") == "false"

        toggle.click()
        assert panel.is_visible()
        assert toggle.get_attribute("aria-expanded") == "true"

        toggle.click()
        assert panel.is_hidden()
        assert toggle.get_attribute("aria-expanded") == "false"

    @pytest.mark.parametrize("name", POPOUTS)
    def test_outside_click_closes(self, sandbox, name):
        _toggle(sandbox, name).click()
        sandbox.locator(".gallery-docs__section-heading").first.click()
        assert _panel(sandbox, name).is_hidden()
        assert _toggle(sandbox, name).get_attribute("aria-expanded") == "false"

    def test_opening_one_closes_the_others(self, sandbox):
        _toggle(sandbox, "bg").click()
        _toggle(sandbox, "zoom").click()
        assert _panel(sandbox, "bg").is_hidden()
        assert _toggle(sandbox, "bg").get_attribute("aria-expanded") == "false"
        assert _panel(sandbox, "zoom").is_visible()

    @pytest.mark.parametrize(
        ("popout", "value"), [("bg", "white"), ("viewport", "320"), ("zoom", "150")]
    )
    def test_choosing_an_option_closes_the_popout(self, sandbox, popout, value):
        _choose(sandbox, popout, value)
        assert _panel(sandbox, popout).is_hidden()
        assert _toggle(sandbox, popout).get_attribute("aria-expanded") == "false"


class TestBackground:
    def test_applies_to_the_canvas_and_swatch(self, sandbox):
        _choose(sandbox, "bg", "dark-grey")
        assert "canvas-bg-dark-grey" in sandbox.evaluate(f"{WRAPPER}.className").split()
        assert sandbox.evaluate(
            """() => getComputedStyle(document.querySelector(
                    '.gallery-sandbox-toolbar__bg-swatch')).backgroundColor
                === getComputedStyle(document.querySelector(
                    "[data-bg='dark-grey'] .gallery-sandbox-toolbar__bg-chip")).backgroundColor"""
        )
        assert _active_options(sandbox, "bg").get_attribute("data-bg") == "dark-grey"

    def test_replaces_the_previous_background(self, sandbox):
        _choose(sandbox, "bg", "dark-grey")
        _choose(sandbox, "bg", "white")
        classes = sandbox.evaluate(f"{WRAPPER}.className").split()
        assert [c for c in classes if c.startswith("canvas-bg-")] == ["canvas-bg-white"]


class TestZoom:
    def test_zooms_the_canvas(self, sandbox):
        _choose(sandbox, "zoom", "150")
        assert sandbox.evaluate(f"{WRAPPER}.style.zoom") == "1.5"
        assert (
            sandbox.locator(".gallery-sandbox-toolbar__zoom-value").inner_text()
            == "150%"
        )
        assert _active_options(sandbox, "zoom").get_attribute("data-zoom") == "150"


class TestViewport:
    def _iframe_style(self, page):
        return page.evaluate(
            f"""() => {{
                const f = {IFRAME};
                return {{
                    width: f.style.width,
                    transform: f.style.transform,
                    scaled: f.closest('.gallery-sandbox__canvas').classList
                        .contains('gallery-sandbox__canvas--viewport'),
                }};
            }}"""
        )

    def test_narrow_width_is_applied_unscaled(self, sandbox):
        _choose(sandbox, "viewport", "320")
        assert self._iframe_style(sandbox) == {
            "width": "320px",
            "transform": "",
            "scaled": True,
        }
        assert (
            sandbox.locator(".gallery-sandbox-toolbar__viewport-value").inner_text()
            == "320px"
        )

    def test_wider_than_the_pane_is_scaled_down(self, sandbox):
        _choose(sandbox, "viewport", "2560")
        style = self._iframe_style(sandbox)
        assert style["width"] == "2560px"
        assert style["transform"].startswith("scale(0.")

    def test_responsive_resets(self, sandbox):
        _choose(sandbox, "viewport", "2560")
        _choose(sandbox, "viewport", "responsive")
        assert self._iframe_style(sandbox) == {
            "width": "",
            "transform": "",
            "scaled": False,
        }
        assert (
            sandbox.locator(".gallery-sandbox-toolbar__viewport-value").inner_text()
            == "Responsive"
        )


class TestToggles:
    def _pressed(self, page, name):
        btn = _toggle(page, name)
        active = (
            "gallery-sandbox-toolbar__btn--active"
            in (btn.get_attribute("class") or "").split()
        )
        return btn.get_attribute("aria-pressed"), active

    def test_outline(self, sandbox):
        has_style = (
            f"!!{IFRAME}.contentDocument.getElementById('gallery-box-model-outline')"
        )
        _toggle(sandbox, "outline").click()
        assert self._pressed(sandbox, "outline") == ("true", True)
        assert sandbox.evaluate(has_style)

        _toggle(sandbox, "outline").click()
        assert self._pressed(sandbox, "outline") == ("false", False)
        assert not sandbox.evaluate(has_style)

    def test_rtl(self, sandbox):
        direction = f"{IFRAME}.contentDocument.documentElement.getAttribute('dir')"
        _toggle(sandbox, "rtl").click()
        assert self._pressed(sandbox, "rtl") == ("true", True)
        assert sandbox.evaluate(direction) == "rtl"

        _toggle(sandbox, "rtl").click()
        assert self._pressed(sandbox, "rtl") == ("false", False)
        assert sandbox.evaluate(direction) is None

    def test_measure_overlays_on_hover(self, sandbox):
        doc = f"{IFRAME}.contentDocument"
        _toggle(sandbox, "measure").click()
        assert self._pressed(sandbox, "measure") == ("true", True)
        sandbox.wait_for_function(
            f"() => !!{WRAPPER}._galleryMeasureCleanup"
        )  # measure.js has loaded in the canvas

        canvas = sandbox.frame_locator(".gallery-sandbox__iframe")
        canvas.locator(".canvas-wrapper > *").first.hover()
        sandbox.wait_for_function(
            f"() => !!{doc}.getElementById('gallery-measure-container')"
        )

        _toggle(sandbox, "measure").click()
        assert self._pressed(sandbox, "measure") == ("false", False)
        assert sandbox.evaluate(
            f"""() => !{doc}.getElementById('gallery-measure-style')
                && !{doc}.getElementById('gallery-measure-container')
                && !{WRAPPER}._galleryMeasureCleanup"""
        )


class TestDrawer:
    @pytest.fixture()
    def sandbox(self, sandbox):
        # At this width the sandbox canvas is ~1100px tall, so in a shorter
        # window the drawer is clipped below the fold and can't be dragged.
        sandbox.set_viewport_size({"width": 1900, "height": 1600})
        sandbox.wait_for_function(
            """() => document.querySelector('[data-gallery-drawer]')
                .getBoundingClientRect().bottom <= innerHeight"""
        )
        return sandbox

    def _drag(self, page, dy):
        box = page.locator("[data-gallery-resizer]").bounding_box()
        x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
        page.mouse.move(x, y)
        page.mouse.down()
        page.mouse.move(x, y + dy, steps=5)
        page.mouse.up()

    def _height(self, page):
        return page.locator("[data-gallery-drawer]").evaluate(
            "d => d.getBoundingClientRect().height"
        )

    def test_dragging_up_grows_the_drawer(self, sandbox):
        before = self._height(sandbox)
        self._drag(sandbox, -60)
        assert self._height(sandbox) == pytest.approx(before + 60, abs=1)

    def test_is_at_least_48px(self, sandbox):
        # Drag to the bottom edge of the window, which is far enough to take
        # the drawer below 48px. Pointer events past the window edge aren't
        # reliably delivered, so don't drag beyond it.
        box = sandbox.locator("[data-gallery-resizer]").bounding_box()
        centre = box["y"] + box["height"] / 2
        bottom = sandbox.viewport_size["height"] - 1
        assert bottom - centre > self._height(sandbox) - 48
        self._drag(sandbox, bottom - centre)
        assert self._height(sandbox) == pytest.approx(48, abs=1)

    def test_resets_the_cursor_after_dragging(self, sandbox):
        self._drag(sandbox, -20)
        assert sandbox.evaluate("document.body.style.cursor") == ""


class TestStateAcrossParameterChange:
    """The sandbox body is swapped by HTMX when a parameter changes. The
    toolbar is re-rendered and must restore every selection."""

    def test_selections_survive_the_swap(self, sandbox):
        sandbox.wait_for_function("() => !!window.htmx")
        _choose(sandbox, "bg", "dark-grey")
        _choose(sandbox, "zoom", "150")
        _choose(sandbox, "viewport", "320")
        for name in ["outline", "rtl", "measure"]:
            _toggle(sandbox, name).click()

        sandbox.evaluate(f"{IFRAME}.dataset.beforeSwap = '1'")
        sandbox.select_option("#id_level", "warning")
        sandbox.wait_for_function(
            f"() => {IFRAME} && !{IFRAME}.dataset.beforeSwap", timeout=10_000
        )
        _wait_for_canvas(sandbox)
        sandbox.wait_for_function(
            f"() => !!{IFRAME}.contentDocument.getElementById('gallery-measure-style')"
        )

        doc = f"{IFRAME}.contentDocument"
        state = sandbox.evaluate(
            f"""() => ({{
                level: {WRAPPER}.innerHTML.includes('warning'),
                bg: {WRAPPER}.className.split(' ').includes('canvas-bg-dark-grey'),
                zoom: {WRAPPER}.style.zoom,
                width: {IFRAME}.style.width,
                outline: !!{doc}.getElementById('gallery-box-model-outline'),
                dir: {doc}.documentElement.getAttribute('dir'),
            }})"""
        )
        assert state == {
            "level": True,
            "bg": True,
            "zoom": "1.5",
            "width": "320px",
            "outline": True,
            "dir": "rtl",
        }

        labels = {
            name: sandbox.locator(
                f".gallery-sandbox-toolbar__{name}-value"
            ).inner_text()
            for name in ["zoom", "viewport"]
        }
        assert labels == {"zoom": "150%", "viewport": "320px"}
        for popout, value in [
            ("bg", "dark-grey"),
            ("zoom", "150"),
            ("viewport", "320"),
        ]:
            assert (
                _active_options(sandbox, popout).get_attribute(f"data-{popout}")
                == value
            )
        for name in ["outline", "rtl", "measure"]:
            assert _toggle(sandbox, name).get_attribute("aria-pressed") == "true"
