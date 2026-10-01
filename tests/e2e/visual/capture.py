"""Helpers that make gallery screenshots deterministic and compare them to baselines."""

from collections.abc import Sequence
from pathlib import Path
from typing import Any

from dj_design_system.testing.visual import assert_matches_baseline


# Applied to the page and every iframe so nothing is mid-transition when captured.
FREEZE_CSS = """
*, *::before, *::after {
    transition: none !important;
    animation: none !important;
    caret-color: transparent !important;
}
"""

# Loads lazy iframes, waits for every iframe and web font, then waits until
# iframe heights (which canvas-resize.js adjusts after load) have been
# unchanged for 500ms (up to 15s).
_SETTLE_JS = """
async () => {
    const frames = [...document.querySelectorAll("iframe")];
    frames.forEach(f => { if (f.loading === "lazy") f.loading = "eager"; });
    await Promise.all(frames.map(f => new Promise(resolve => {
        const doc = f.contentDocument;
        const hasSrc = Boolean(f.getAttribute("src"));
        if (doc && doc.readyState === "complete" && (!hasSrc || doc.URL !== "about:blank")) {
            return resolve();
        }
        f.addEventListener("load", () => resolve(), { once: true });
        setTimeout(resolve, 10000);
    })));
    await document.fonts.ready;
    // Basic-mode canvases report their height to the parent (canvas-resize.js),
    // which sets iframe.style.height; the exchange repeats until the applied
    // height equals the reported one. A report sent before the gallery's
    // listener was attached is lost and the preview never resizes (#111), so
    // replay each canvas's latest report (a no-op if it was already handled,
    // and ignored on pages without a listener), then wait for convergence.
    const reports = window.__ddsCanvasReports;
    if (reports) {
        for (const [source, data] of reports) {
            window.dispatchEvent(new MessageEvent("message", { data, source }));
        }
    }
    const converged = f => {
        const doc = f.contentDocument;
        if (!f.getClientRects().length || !doc || !doc.querySelector(".canvas-wrapper--basic")) return true;
        if (reports) {
            if (!reports.has(f.contentWindow)) return false;  // first report not sent yet
            if (!f.style.height) return true;  // this page never applies heights
        }
        return f.style.height === doc.documentElement.scrollHeight + "px";
    };
    const deadline = Date.now() + 15000;
    while (!frames.every(converged)) {
        if (Date.now() > deadline) {
            const pending = frames.filter(f => !converged(f)).map(f => f.dataset.canvasId || f.src);
            throw new Error("Canvas iframes did not finish resizing: " + pending.join(", "));
        }
        await new Promise(r => setTimeout(r, 50));
    }
    // Preview iframes shrink ~2px per frame towards their content height, and
    // slow (emulated) runners can stall mid-way, so require 500ms unchanged.
    const snapshot = () => frames.map(f => f.offsetHeight).join(",") + "|" + document.body.scrollHeight;
    let previous = snapshot();
    let unchanged = 0;
    for (let i = 0; i < 150 && unchanged < 5; i++) {
        await new Promise(r => setTimeout(r, 100));
        const current = snapshot();
        unchanged = current === previous ? unchanged + 1 : 0;
        previous = current;
    }
}
"""


# On-screen elements whose content is taller than their (scrolling) box.
# Off-screen ones (e.g. the closed mobile sidebar) and form controls, whose own
# scrolling is not layout clipping, are ignored.
_CLIPPED_JS = """
() => [...document.querySelectorAll("*")]
    .filter(el => {
        if (!el.getClientRects().length) return false;
        if (el.matches("textarea, select, input")) return false;
        const rect = el.getBoundingClientRect();
        if (rect.right <= 0 || rect.left >= window.innerWidth) return false;
        // Visually hidden text (a 1px box) is meant to be clipped.
        if (rect.width <= 1 && rect.height <= 1) return false;
        const overflowY = getComputedStyle(el).overflowY;
        if (!["auto", "scroll", "hidden"].includes(overflowY)) return false;
        return el.scrollHeight - el.clientHeight > 1;
    })
    .map(el => ({
        name: el.tagName.toLowerCase() + (el.className && typeof el.className === "string"
            ? "." + el.className.trim().split(/\\s+/).join(".") : ""),
        overflow: el.scrollHeight - el.clientHeight,
    }))
"""


def find_clipped_containers(page: Any) -> list[dict]:
    """Return visible elements whose content overflows their height.

    Each entry has ``name`` (tag and classes) and ``overflow`` (hidden
    pixels). The gallery shell is ``100vh`` tall with internally scrolling
    panes, so a full-page screenshot only captures what fits the viewport.
    """
    return page.evaluate(_CLIPPED_JS)


def fit_viewport_to_content(page: Any, *, max_height: int = 12000) -> None:
    """Grow the viewport height until no scrolling container is clipped.

    The width is kept, so responsive layouts are unchanged. Raises
    ``AssertionError`` if content is still clipped at ``max_height``.
    """
    for _ in range(20):
        clipped = find_clipped_containers(page)
        if not clipped:
            return
        size = page.viewport_size
        needed = size["height"] + max(item["overflow"] for item in clipped)
        if needed > max_height:
            break
        page.set_viewport_size({"width": size["width"], "height": needed})
        page.evaluate(_SETTLE_JS)
    clipped = find_clipped_containers(page)
    if clipped:
        names = ", ".join(item["name"] for item in clipped)
        raise AssertionError(
            f"Content still clipped at a {max_height}px viewport: {names}"
        )


def block_external_requests(page: Any, allowed_origin: str) -> None:
    """Abort every request that is not to ``allowed_origin`` (or inline data).

    Keeps screenshots independent of CDNs and the network. The gallery's only
    external resource is HTMX, which the gallery JS only listens to events
    from, so blocking it does not change what is rendered.
    """
    allowed_origin = allowed_origin.rstrip("/")

    def handle(route: Any) -> None:
        url = route.request.url
        if url.startswith((allowed_origin + "/", "data:", "blob:", "about:")):
            route.continue_()
        else:
            route.abort()

    page.route("**/*", handle)


# Installed before any page script so canvas size reports sent before the
# gallery's own listener exists are still recorded (see _SETTLE_JS).
_RECORD_REPORTS_JS = """
if (window.top === window) {
    window.__ddsCanvasReports = new Map();
    window.addEventListener("message", event => {
        if (event.data && event.data.type === "canvas-resize") {
            window.__ddsCanvasReports.set(event.source, event.data);
        }
    }, true);
}
"""


def record_canvas_reports(page: Any) -> None:
    """Record canvas size reports from page start; call before navigating.

    Lets ``stabilise`` recover previews whose first report was sent before
    the gallery started listening, instead of capturing them unresized.
    """
    page.add_init_script(_RECORD_REPORTS_JS)


def stabilise(page: Any) -> None:
    """Freeze animations and wait for iframes, fonts and layout to settle."""
    page.add_style_tag(content=FREEZE_CSS)
    page.evaluate(_SETTLE_JS)
    for frame in page.frames[1:]:
        frame.add_style_tag(content=FREEZE_CSS)


class ScreenshotRecorder:
    """Takes named screenshots and compares each one to its committed baseline.

    Actual screenshots are written to ``output_dir/actual/`` and failure
    artefacts to ``output_dir/failures/``. The file names produced during a
    run are collected in ``produced`` so orphaned baselines can be found.
    """

    def __init__(
        self,
        baseline_dir: str | Path,
        output_dir: str | Path,
        *,
        update: bool = False,
        threshold: float = 0.1,
        max_mismatch_ratio: float = 0.0,
    ) -> None:
        self.baseline_dir = Path(baseline_dir)
        self.output_dir = Path(output_dir)
        self.update = update
        self.threshold = threshold
        self.max_mismatch_ratio = max_mismatch_ratio
        self.produced: set[str] = set()

    def check(
        self,
        page: Any,
        name: str,
        *,
        mask: Sequence[str] = (),
        full_page: bool = True,
        fit: bool = True,
    ) -> None:
        """Screenshot ``page`` as ``<name>.png`` and compare it to the baseline.

        ``mask`` is a list of CSS selectors whose regions are painted over
        before capture, for content that legitimately varies between runs.
        With ``fit`` (the default) the viewport is first grown so that no
        internally scrolling pane hides content.
        """
        if fit:
            fit_viewport_to_content(page)
        filename = f"{name}.png"
        actual = self.output_dir / "actual" / filename
        actual.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(
            path=str(actual),
            full_page=full_page,
            animations="disabled",
            caret="hide",
            mask=[page.locator(selector) for selector in mask],
            mask_color="#ff00ff",
        )
        self.produced.add(filename)
        assert_matches_baseline(
            actual,
            self.baseline_dir / filename,
            failure_dir=self.output_dir / "failures",
            threshold=self.threshold,
            max_mismatch_ratio=self.max_mismatch_ratio,
            update=self.update,
        )


def prune_orphaned_baselines(
    baseline_dir: str | Path, produced: set[str]
) -> list[Path]:
    """Delete baseline PNGs that no screenshot in this run produced.

    Returns the deleted paths. Only call this after a full, passing update
    run (see ``should_prune``); otherwise live baselines would be removed.
    """
    baseline_dir = Path(baseline_dir)
    if not baseline_dir.is_dir():
        return []
    removed = []
    for path in sorted(baseline_dir.glob("*.png")):
        if path.name not in produced:
            path.unlink()
            removed.append(path)
    return removed


def should_prune(
    *,
    update: bool,
    args: Sequence[str],
    suite_dir: Path,
    deselected: int,
    failed: int,
) -> bool:
    """Return True only when an update run covered the whole visual suite.

    ``args`` are the absolute paths pytest was invoked with. Any argument that
    targets a single file or test, or a directory outside the suite, means
    some screenshots were not taken, so nothing may be pruned. The same goes
    for deselected (e.g. ``-k``) or failed tests.
    """
    if not update or deselected or failed:
        return False
    for arg in args:
        if "::" in arg:
            return False
        target = Path(arg)
        if target.suffix == ".py":
            return False
        if target != suite_dir and target not in suite_dir.parents:
            return False
    return True
