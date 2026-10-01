"""Visual regression screenshots of gallery pages."""

import pytest


pytestmark = [pytest.mark.e2e, pytest.mark.visual]


def test_index(gallery, screenshot_recorder):
    page = gallery()
    screenshot_recorder.check(page, "index")
