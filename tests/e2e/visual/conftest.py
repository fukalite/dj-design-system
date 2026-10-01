"""Fixtures for the gallery visual regression suite.

Run it with `just visual` (compare) or `just update-visual-baselines`
(regenerate), which render in the pinned Playwright container. Screenshots
taken outside that container will not match the committed baselines.
"""

import os
import shutil
from pathlib import Path

import pytest

from tests.e2e.visual.capture import (
    ScreenshotRecorder,
    block_external_requests,
    prune_orphaned_baselines,
    record_canvas_reports,
    should_prune,
    stabilise,
)


SUITE_DIR = Path(__file__).resolve().parent
BASELINE_DIR = SUITE_DIR / "baselines"
OUTPUT_DIR = SUITE_DIR / "output"

# Shared between the session fixture and the session-finish hook.
_run: dict = {"recorder": None, "deselected": 0}


def update_mode() -> bool:
    """Return True when baselines should be regenerated instead of compared."""
    return os.environ.get("UPDATE_VISUAL_BASELINES", "") not in ("", "0")


@pytest.fixture(scope="session")
def screenshot_recorder() -> ScreenshotRecorder:
    """A recorder shared by the whole run; output from previous runs is cleared."""
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    recorder = ScreenshotRecorder(BASELINE_DIR, OUTPUT_DIR, update=update_mode())
    _run["recorder"] = recorder
    return recorder


def pytest_deselected(items):
    """Count deselected suite tests (e.g. via ``-k``) so pruning is skipped."""
    _run["deselected"] += sum(
        1 for item in items if SUITE_DIR in Path(str(item.path)).parents
    )


def pytest_sessionfinish(session, exitstatus):
    """After a full update run, delete baselines no screenshot produced."""
    recorder = _run["recorder"]
    if recorder is None:
        return
    invocation_dir = session.config.invocation_params.dir
    args = [str(invocation_dir / arg) for arg in session.config.args]
    if should_prune(
        update=recorder.update,
        args=args or [str(invocation_dir)],
        suite_dir=SUITE_DIR,
        deselected=_run["deselected"],
        failed=session.testsfailed,
    ):
        for path in prune_orphaned_baselines(BASELINE_DIR, recorder.produced):
            print(f"\nRemoved orphaned baseline: {path.relative_to(SUITE_DIR)}")


VIEWPORTS = {
    "desktop": {"width": 1280, "height": 800},
    # >= 1800px shows the documentation and sandbox panes side by side.
    "wide": {"width": 1920, "height": 1080},
    # <= 768px collapses the sidebar behind the hamburger menu.
    "mobile": {"width": 390, "height": 844},
}

GALLERY_THEMES = ("light", "dark")


@pytest.fixture
def gallery(page, live_server):
    """Return a function that opens a gallery path ready for a stable screenshot.

    ``theme`` switches the gallery chrome between the ``gallery-theme-light``
    and ``gallery-theme-dark`` classes on ``<html>``, the hook projects use to
    theme the gallery.
    """
    block_external_requests(page, live_server.url)
    record_canvas_reports(page)

    def open_path(path: str = "", *, viewport: str = "desktop", theme: str = "light"):
        page.set_viewport_size(VIEWPORTS[viewport])
        page.goto(f"{live_server.url}/dds/{path}")
        page.evaluate(
            "theme => { document.documentElement.className = `gallery-theme-${theme}`; }",
            theme,
        )
        stabilise(page)
        return page

    return open_path
