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
    stabilise,
)


SUITE_DIR = Path(__file__).resolve().parent
BASELINE_DIR = SUITE_DIR / "baselines"
OUTPUT_DIR = SUITE_DIR / "output"


def update_mode() -> bool:
    """Return True when baselines should be regenerated instead of compared."""
    return os.environ.get("UPDATE_VISUAL_BASELINES", "") not in ("", "0")


@pytest.fixture(scope="session")
def screenshot_recorder() -> ScreenshotRecorder:
    """A recorder shared by the whole run; output from previous runs is cleared."""
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    return ScreenshotRecorder(BASELINE_DIR, OUTPUT_DIR, update=update_mode())


@pytest.fixture
def gallery(page, live_server):
    """Return a function that opens a gallery path ready for a stable screenshot."""
    block_external_requests(page, live_server.url)

    def open_path(path: str = ""):
        page.goto(f"{live_server.url}/dds/{path}")
        stabilise(page)
        return page

    return open_path
