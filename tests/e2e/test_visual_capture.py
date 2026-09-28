"""Tests for the gallery visual regression capture helpers."""

import pytest

from dj_design_system.testing.visual import ScreenshotMismatch
from tests.e2e.visual.capture import (
    ScreenshotRecorder,
    block_external_requests,
    find_clipped_containers,
    fit_viewport_to_content,
    stabilise,
)


pytestmark = pytest.mark.e2e


class TestBlockExternalRequests:
    def test_external_requests_are_aborted(self, page, live_server):
        block_external_requests(page, live_server.url)
        failed: list[str] = []
        page.on("requestfailed", lambda request: failed.append(request.url))

        page.goto(f"{live_server.url}/dds/")
        page.evaluate(
            """() => new Promise(resolve => {
                const img = new Image();
                img.onerror = img.onload = resolve;
                img.src = "https://example.invalid/blocked.png";
            })"""
        )

        assert "https://example.invalid/blocked.png" in failed

    def test_same_origin_requests_are_allowed(self, page, live_server):
        block_external_requests(page, live_server.url)
        response = page.goto(f"{live_server.url}/dds/")
        assert response is not None and response.ok


class TestStabilise:
    def test_disables_transitions_and_animations(self, page, gallery_url):
        page.goto(gallery_url)
        stabilise(page)
        durations = page.evaluate(
            """() => {
                const style = getComputedStyle(document.querySelector(".gallery-sidebar"));
                return [style.transitionDuration, style.animationDuration];
            }"""
        )
        assert durations == ["0s", "0s"]

    def test_waits_for_fonts_and_iframes(self, page, live_server):
        page.goto(f"{live_server.url}/dds/demo_components/alert/")
        stabilise(page)
        state = page.evaluate(
            """() => ({
                fonts: document.fonts.status,
                iframes: [...document.querySelectorAll("iframe")].map(
                    f => f.contentDocument && f.contentDocument.readyState
                ),
            })"""
        )
        assert state["fonts"] == "loaded"
        assert state["iframes"]
        assert all(ready == "complete" for ready in state["iframes"])


class TestScreenshotRecorder:
    @pytest.fixture
    def recorder_factory(self, tmp_path):
        def make(update: bool) -> ScreenshotRecorder:
            return ScreenshotRecorder(
                baseline_dir=tmp_path / "baselines",
                output_dir=tmp_path / "output",
                update=update,
            )

        return make

    def test_missing_baseline_fails(self, page, gallery_url, recorder_factory):
        page.goto(gallery_url)
        with pytest.raises(ScreenshotMismatch, match="Missing baseline"):
            recorder_factory(update=False).check(page, "index")

    def test_update_then_compare_round_trip(
        self, page, gallery_url, recorder_factory, tmp_path
    ):
        page.goto(gallery_url)
        recorder_factory(update=True).check(page, "index")
        assert (tmp_path / "baselines" / "index.png").is_file()

        recorder = recorder_factory(update=False)
        recorder.check(page, "index")
        assert recorder.produced == {"index.png"}
        assert (tmp_path / "output" / "actual" / "index.png").is_file()

    def test_masked_regions_are_ignored(self, page, gallery_url, recorder_factory):
        page.goto(gallery_url)
        recorder_factory(update=True).check(page, "index", mask=["h1"])

        page.evaluate("() => { document.querySelector('h1').textContent = 'Changed'; }")
        recorder_factory(update=False).check(page, "index", mask=["h1"])


class TestFitViewportToContent:
    """The gallery shell is 100vh with internally scrolling panes."""

    @pytest.fixture
    def short_page(self, page, live_server):
        block_external_requests(page, live_server.url)
        page.set_viewport_size({"width": 1280, "height": 400})
        page.goto(f"{live_server.url}/dds/")
        stabilise(page)
        return page

    def test_detects_clipped_nav_tree(self, short_page):
        """The nav tree scrolls inside the sidebar."""
        clipped = find_clipped_containers(short_page)
        assert any(item["name"] == "nav.gallery-nav" for item in clipped)

    def test_grows_viewport_until_nothing_is_clipped(self, short_page):
        fit_viewport_to_content(short_page)
        assert find_clipped_containers(short_page) == []
        assert short_page.viewport_size["height"] > 400
        assert short_page.viewport_size["width"] == 1280

    def test_is_a_no_op_when_nothing_is_clipped(self, page, live_server):
        block_external_requests(page, live_server.url)
        page.set_viewport_size({"width": 1280, "height": 4000})
        page.goto(f"{live_server.url}/dds/")
        stabilise(page)
        fit_viewport_to_content(page)
        assert page.viewport_size["height"] == 4000

    def test_fails_loudly_beyond_max_height(self, short_page):
        with pytest.raises(AssertionError, match="still clipped"):
            fit_viewport_to_content(short_page, max_height=500)

    def test_check_fits_before_capturing(self, short_page, tmp_path):
        recorder = ScreenshotRecorder(
            baseline_dir=tmp_path / "baselines",
            output_dir=tmp_path / "output",
            update=True,
        )
        recorder.check(short_page, "index")
        assert find_clipped_containers(short_page) == []

    def test_check_can_skip_fitting(self, short_page, tmp_path):
        recorder = ScreenshotRecorder(
            baseline_dir=tmp_path / "baselines",
            output_dir=tmp_path / "output",
            update=True,
        )
        recorder.check(short_page, "index", fit=False)
        assert short_page.viewport_size["height"] == 400

    def test_ignores_off_screen_containers(self, page, live_server):
        """On mobile the sidebar is translated off-screen until opened."""
        block_external_requests(page, live_server.url)
        page.set_viewport_size({"width": 390, "height": 300})
        page.goto(f"{live_server.url}/dds/")
        stabilise(page)
        clipped = find_clipped_containers(page)
        assert not any(item["name"] == "nav.gallery-nav" for item in clipped)
