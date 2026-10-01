"""Tests for the gallery visual regression capture helpers."""

import pytest

from dj_design_system.testing.visual import ScreenshotMismatch
from tests.e2e.visual.capture import (
    ScreenshotRecorder,
    block_external_requests,
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
