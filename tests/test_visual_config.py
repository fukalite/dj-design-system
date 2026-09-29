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


def _recipe_body(name: str) -> str:
    match = re.search(
        rf"^{re.escape(name)}(?:\s[^:\n]*)?:[^\n]*\n((?:[ \t]+.*\n|\n(?=[ \t]))+)",
        JUSTFILE.read_text(),
        re.MULTILINE,
    )
    assert match, f"justfile must define a '{name}' recipe"
    return match.group(1)


def test_visual_recipes_exist():
    for name in ("visual-run", "visual", "update-visual-baselines"):
        assert _recipe_body(name)


def test_docker_recipes_use_pinned_image_platform_and_playwright():
    """Local runs must render exactly as CI does."""
    text = JUSTFILE.read_text()
    assert "--platform linux/amd64" in text
    assert "mcr.microsoft.com/playwright/python:v{{playwright_version}}-noble" in text
    assert '"playwright=={{playwright_version}}"' in text


def test_update_recipe_enables_update_mode():
    assert "_visual-docker 1" in _recipe_body("update-visual-baselines")
    assert "_visual-docker 0" in _recipe_body("visual")
    assert "UPDATE_VISUAL_BASELINES={{update}}" in _recipe_body("_visual-docker")


def test_visual_output_is_gitignored():
    ignored = (ROOT / ".gitignore").read_text().splitlines()
    assert "tests/e2e/visual/output/" in ignored


def _ci_jobs() -> dict:
    import yaml

    return yaml.safe_load((WORKFLOWS / "ci.yml").read_text())["jobs"]


def test_ci_visual_regression_job_runs_in_pinned_container():
    job = _ci_jobs()["visual-regression"]
    image = job["container"]["image"]
    assert image == (
        f"mcr.microsoft.com/playwright/python:v{_justfile_playwright_version()}-noble"
    )
    assert job["runs-on"] == "ubuntu-latest"  # linux/amd64, as baselines expect


def test_ci_visual_regression_job_runs_suite_and_uploads_artefacts():
    steps = _ci_jobs()["visual-regression"]["steps"]
    commands = "\n".join(step.get("run", "") for step in steps)
    assert "just visual-run" in commands
    assert "playwright==$(just --evaluate playwright_version)" in commands

    uploads = [s for s in steps if s.get("uses", "").startswith("actions/upload-artifact")]
    paths = {s["with"]["path"]: s.get("if") for s in uploads}
    assert paths.get("tests/e2e/visual/output/actual") == "always()"
    assert paths.get("tests/e2e/visual/output/failures") == "failure()"


def test_ci_visual_regression_job_writes_summary_on_failure():
    steps = _ci_jobs()["visual-regression"]["steps"]
    assert any(
        s.get("if") == "failure()" and "GITHUB_STEP_SUMMARY" in s.get("run", "")
        for s in steps
    )


def test_ci_complete_requires_visual_regression():
    assert "visual-regression" in _ci_jobs()["ci-complete"]["needs"]


def test_ci_runs_on_pull_requests_to_any_branch():
    """Stacked PRs (based on another PR's branch) must get CI too."""
    import yaml

    workflow = yaml.safe_load((WORKFLOWS / "ci.yml").read_text())
    triggers = workflow.get("on", workflow.get(True))  # PyYAML parses `on` as True
    assert "pull_request" in triggers
    assert not (triggers["pull_request"] or {}).get("branches")
