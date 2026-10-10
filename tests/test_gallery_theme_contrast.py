"""WCAG AA contrast checks for the gallery design tokens.

The gallery theme tokens are consumed by axe (through the example project's
AccessibilityPlugin) and by the visual regression snapshots. These tests keep
the token values themselves compliant, so a future token change cannot silently
reintroduce a contrast failure. See issue #129.
"""

import re
from pathlib import Path

import pytest


GALLERY_CSS = (
    Path(__file__).resolve().parent.parent
    / "dj_design_system"
    / "static"
    / "dj_design_system"
    / "gallery.css"
)

AA_TEXT_THRESHOLD = 4.5
THEME_SELECTORS = (":root", ".gallery-theme-light", ".gallery-theme-dark")


@pytest.fixture(scope="module")
def css() -> str:
    return GALLERY_CSS.read_text(encoding="utf-8")


def theme_block(css: str, selector: str) -> dict[str, str]:
    """Return the custom properties declared inside a theme block."""
    match = re.search(rf"^{re.escape(selector)}\s*\{{([^}}]*)\}}", css, re.MULTILINE)
    assert match, f"missing theme block for {selector!r}"
    return dict(re.findall(r"(--[\w-]+)\s*:\s*([^;]+);", match.group(1)))


def rule_body(css: str, pattern: str) -> str:
    """Return the declaration block for the first rule matching ``pattern``."""
    match = re.search(rf"{pattern}[^{{]*\{{([^}}]*)\}}", css)
    assert match, f"no rule matching {pattern!r}"
    return match.group(1)


def relative_luminance(hex_color: str) -> float:
    channels = [int(hex_color.lstrip("#")[i : i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [
        c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(foreground: str, background: str) -> float:
    first, second = relative_luminance(foreground), relative_luminance(background)
    lighter, darker = max(first, second), min(first, second)
    return (lighter + 0.05) / (darker + 0.05)


@pytest.mark.parametrize("selector", THEME_SELECTORS)
def test_muted_text_meets_aa_on_content_background(css, selector):
    """Muted text sits on the content pane, so it must reach 4.5:1."""
    tokens = theme_block(css, selector)
    ratio = contrast_ratio(
        tokens["--gallery-text-muted"], tokens["--gallery-content-bg"]
    )
    assert ratio >= AA_TEXT_THRESHOLD, (
        f"{selector}: --gallery-text-muted on --gallery-content-bg is {ratio:.2f}:1"
    )


@pytest.mark.parametrize("selector", THEME_SELECTORS)
def test_input_tokens_are_defined(css, selector):
    """Every theme must define the sandbox form input tokens."""
    tokens = theme_block(css, selector)
    for token in (
        "--gallery-input-bg",
        "--gallery-input-text",
        "--gallery-input-border",
    ):
        assert token in tokens, f"{selector} does not define {token}"


@pytest.mark.parametrize("selector", THEME_SELECTORS)
def test_input_text_meets_aa_on_input_background(css, selector):
    """The value typed into a sandbox input must be readable."""
    tokens = theme_block(css, selector)
    ratio = contrast_ratio(tokens["--gallery-input-text"], tokens["--gallery-input-bg"])
    assert ratio >= AA_TEXT_THRESHOLD, (
        f"{selector}: input text on input background is {ratio:.2f}:1"
    )


def test_sandbox_inputs_use_the_themed_tokens(css):
    """Inputs must not fall back to the browser's white background."""
    body = rule_body(css, r'\.gallery-params-form__field input\[type="text"\]')
    assert "background: var(--gallery-input-bg)" in body
    assert "color: var(--gallery-input-text)" in body
    assert "border: 1px solid var(--gallery-input-border)" in body


def test_sandbox_checkboxes_follow_the_accent(css):
    """Checkbox controls are tinted rather than left as native white boxes."""
    body = rule_body(css, r'\.gallery-params-form__field input\[type="checkbox"\]')
    assert "accent-color: var(--gallery-accent)" in body
