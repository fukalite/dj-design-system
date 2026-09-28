"""Guards that keep the visual regression tooling's pinned versions in sync."""

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
JUSTFILE = ROOT / "justfile"
WORKFLOWS = ROOT / ".github" / "workflows"
IMAGE_RE = re.compile(r"mcr\.microsoft\.com/playwright/python:v([0-9.]+)-noble")


def _justfile_playwright_version() -> str:
    match = re.search(
        r'^playwright_version\s*:=\s*"([0-9]+\.[0-9]+\.[0-9]+)"$',
        JUSTFILE.read_text(),
        re.MULTILINE,
    )
    assert match, 'justfile must define playwright_version := "X.Y.Z"'
    return match.group(1)


def test_justfile_pins_playwright_version():
    assert _justfile_playwright_version()


def test_workflow_playwright_images_match_justfile():
    """The CI container must render with exactly the version baselines use."""
    version = _justfile_playwright_version()
    for workflow in WORKFLOWS.glob("*.yml"):
        for found in IMAGE_RE.findall(workflow.read_text()):
            assert found == version, (
                f"{workflow.name} uses Playwright image v{found}, "
                f"but the justfile pins {version}"
            )


def test_e2e_recipe_excludes_visual_suite():
    recipe = re.search(r"^e2e:\n((?:[ \t]+.*\n)+)", JUSTFILE.read_text(), re.MULTILINE)
    assert recipe, "justfile must define an e2e recipe"
    assert "not visual" in recipe.group(1)
