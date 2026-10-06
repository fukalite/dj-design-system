"""Tests for the gallery visual regression capture helpers."""

import pytest

from dj_design_system.testing.visual import ScreenshotMismatch
from tests.e2e.visual.capture import (
    ScreenshotRecorder,
    block_external_requests,
    find_clipped_containers,
    fit_viewport_to_content,
    record_canvas_reports,
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
        record_canvas_reports(page)
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

    def test_waits_through_pauses_in_iframe_resizing(self, page, gallery_url):
        """Preview iframes shrink ~2px per frame; slow runners can stall mid-way."""
        page.goto(gallery_url)
        page.evaluate(
            """() => {
                const f = document.createElement("iframe");
                f.id = "shrinking";
                f.srcdoc = "<p>hi</p>";
                f.style.height = "150px";
                document.querySelector(".gallery-content-area").append(f);
                let h = 150;
                const step = () => {
                    h -= 2;
                    f.style.height = h + "px";
                    if (h <= 60) return;
                    // Stall for 200ms half-way, as a throttled frame would.
                    if (h === 106) setTimeout(() => requestAnimationFrame(step), 200);
                    else requestAnimationFrame(step);
                };
                f.addEventListener("load", () => requestAnimationFrame(step), { once: true });
            }"""
        )
        stabilise(page)
        assert (
            page.evaluate("document.getElementById('shrinking').style.height") == "60px"
        )

    def test_waits_for_delayed_canvas_resize_to_converge(self, page, live_server):
        """Under CPU contention the first resize report can arrive late."""
        record_canvas_reports(page)
        page.goto(f"{live_server.url}/dds/demo_components/alert/")
        stabilise(page)  # let the page's own previews finish first
        page.evaluate(
            """() => {
                const srcdoc = `<!DOCTYPE html><html><head><style>
                    html, body { margin: 0; height: 100%; }
                    .canvas-wrapper { min-height: 100%; box-sizing: border-box; padding: 16px; }
                </style></head><body>
                <div class="canvas-wrapper canvas-wrapper--basic">hi</div>
                <script>
                    setTimeout(() => new ResizeObserver(() => parent.postMessage({
                        type: "canvas-resize", id: "delayed",
                        height: document.documentElement.scrollHeight,
                    }, "*")).observe(document.querySelector(".canvas-wrapper")), 800);
                </scr` + `ipt></body></html>`;
                const f = document.createElement("iframe");
                f.className = "gallery-canvas gallery-doc-preview__iframe";
                f.dataset.canvasId = "delayed";
                f.srcdoc = srcdoc;
                document.querySelector(".gallery-doc-preview").append(f);
            }"""
        )
        stabilise(page)
        state = page.evaluate(
            """() => {
                const f = document.querySelector("iframe[data-canvas-id='delayed']");
                return [f.style.height, f.contentDocument.documentElement.scrollHeight];
            }"""
        )
        assert state[0] == f"{state[1]}px"

    def test_recovers_resize_report_sent_before_listener(self, page, live_server):
        """If a preview reports its size before gallery-preview-resize.js is
        listening, the report is lost and the preview never resizes (#111)."""
        import time

        def delay_listener(route):
            time.sleep(1)
            route.continue_()

        page.route("**/gallery-preview-resize.js", delay_listener)
        record_canvas_reports(page)
        page.goto(f"{live_server.url}/dds/demo_components/alert/")
        stabilise(page)
        heights = page.evaluate(
            """() => [...document.querySelectorAll("iframe.gallery-doc-preview__iframe")]
                .map(f => [f.style.height, f.contentDocument.documentElement.scrollHeight])"""
        )
        assert heights == [["58px", 58], ["58px", 58]]

    def test_does_not_hang_on_a_lost_report_without_the_recorder(
        self, page, live_server
    ):
        """Without record_canvas_reports a lost first report can't be replayed,
        so the preview's height is never applied. stabilise() must still finish
        rather than wait for a resize that will never come."""
        import time

        def delay_listener(route):
            time.sleep(1)
            route.continue_()

        page.route("**/gallery-preview-resize.js", delay_listener)
        page.goto(f"{live_server.url}/dds/demo_components/alert/")
        started = time.monotonic()
        stabilise(page)
        assert time.monotonic() - started < 10


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

    def test_ignores_form_controls(self, page, live_server):
        """A textarea's own scrollback is not layout clipping."""
        block_external_requests(page, live_server.url)
        page.goto(f"{live_server.url}/dds/")
        page.evaluate(
            """() => {
                const t = document.createElement("textarea");
                t.rows = 1;
                t.value = "line\\n".repeat(20);
                document.querySelector(".gallery-content-area").append(t);
            }"""
        )
        clipped = find_clipped_containers(page)
        assert not any(item["name"].startswith("textarea") for item in clipped)
