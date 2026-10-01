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
# iframe heights (which canvas-resize.js adjusts after load) stop changing.
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
    let previous = "";
    for (let i = 0; i < 50; i++) {
        await new Promise(r => requestAnimationFrame(() => setTimeout(r, 50)));
        const current = frames.map(f => f.offsetHeight).join(",") + "|" + document.body.scrollHeight;
        if (current === previous) break;
        previous = current;
    }
}
"""


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
    ) -> None:
        """Screenshot ``page`` as ``<name>.png`` and compare it to the baseline.

        ``mask`` is a list of CSS selectors whose regions are painted over
        before capture, for content that legitimately varies between runs.
        """
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
