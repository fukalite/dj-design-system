from pathlib import Path

import pytest

from dj_design_system.testing.plugins import (
    AccessibilityPlugin,
    HTMLValidationPlugin,
    StrictHTMLParser,
    VisualRegressionPlugin,
)
from dj_design_system.testing.visual import ImageComparison


def _write_fake_screenshot(path: str) -> None:
    Path(path).write_bytes(b"fake image data")


def test_visual_regression_plugin_basic(mocker):
    """Verify the snapshot plugin properly hooks into the iteration engine and captures states."""
    mock_page = mocker.Mock()

    plugin = VisualRegressionPlugin(
        page=mock_page, base_url="http://localhost:8000", enable_diff=False
    )

    mock_comp = mocker.Mock()
    mock_comp.qualified_name = "test_app__test_component"
    mock_comp.gallery_basic_kwargs = {
        "title": "Test Title",
        "is_active": True,
        "count": None,
    }

    plugin.run_assessment(mock_comp, "basic", "light")

    # Check that navigation occurred
    mock_page.goto.assert_called_once()
    url = mock_page.goto.call_args[0][0]
    assert "test_app__test_component" in url
    assert "is_active=true" in url
    assert "count" not in url

    # Check that a screenshot was taken
    mock_wrapper = mock_page.locator.return_value
    mock_wrapper.screenshot.assert_called_once()
    screenshot_kwargs = mock_wrapper.screenshot.call_args[1]

    # The path should include the component, variant, and theme
    path = str(screenshot_kwargs.get("path", ""))
    assert "test_app__test_component" in path
    assert "basic" in path
    assert "light" in path


def test_visual_regression_plugin_maximal(mocker):
    mock_page = mocker.Mock()
    plugin = VisualRegressionPlugin(
        page=mock_page, base_url="http://localhost:8000", enable_diff=False
    )

    mock_comp = mocker.Mock()
    mock_comp.qualified_name = "test_app__test_component"

    class GalleryParam:
        def __init__(self, value):
            self.value = value

    mock_comp.gallery_maximal_kwargs = {
        "param1": GalleryParam("val1"),
        "is_active": False,
    }

    plugin.run_assessment(mock_comp, "maximal", "dark")
    url = mock_page.goto.call_args[0][0]
    assert "param1=val1" in url
    assert "is_active=false" in url


def test_playwright_assessment_plugin_navigates_with_json_params(mocker):
    """Verify Playwright plugins serialise list and dict kwargs as valid JSON in URLs (#95)."""
    mock_page = mocker.Mock()
    plugin = VisualRegressionPlugin(
        page=mock_page, base_url="http://localhost:8000", enable_diff=False
    )

    mock_comp = mocker.Mock()
    mock_comp.qualified_name = "test_app__test_component"
    mock_comp.gallery_basic_kwargs = {
        "links": [{"id": "intro", "text": "Introduction"}],
        "metadata": {"tags": ["ui", "button"]},
    }

    plugin.run_assessment(mock_comp, "basic", "light")
    url = mock_page.goto.call_args[0][0]
    assert (
        "links=%5B%7B%22id%22%3A+%22intro%22%2C+%22text%22%3A+%22Introduction%22%7D%5D"
        in url
    )
    assert "metadata=%7B%22tags%22%3A+%5B%22ui%22%2C+%22button%22%5D%7D" in url


def test_visual_regression_plugin_unknown_variant(mocker):
    mock_page = mocker.Mock()
    plugin = VisualRegressionPlugin(
        page=mock_page, base_url="http://localhost:8000", enable_diff=False
    )

    mock_comp = mocker.Mock()
    mock_comp.qualified_name = "test_app__test_component"

    plugin.run_assessment(mock_comp, "unknown", "light")
    url = mock_page.goto.call_args[0][0]
    assert "test_app__test_component" in url
    assert "_dds_variant=unknown" in url


def test_playwright_assessment_plugin_named_gallery_variant(mocker):
    """Named gallery.py variants pass _dds_variant=<name> in the /_canvas/ query string."""
    mock_page = mocker.Mock()
    mock_axe = mocker.patch("axe_playwright_python.sync_playwright.Axe")
    mock_axe.return_value.run.return_value.violations_count = 0

    plugin = AccessibilityPlugin(page=mock_page, base_url="http://localhost:8000/dds")

    mock_comp = mocker.Mock()
    mock_comp.qualified_name = "dds__badge"

    plugin.run_assessment(mock_comp, "info", "dark")
    url = mock_page.goto.call_args[0][0]
    assert "component=dds__badge" in url
    assert "_dds_variant=info" in url
    assert "_dds_theme=dark" in url


def test_visual_regression_missing_baseline(mocker, tmp_path):
    mock_page = mocker.Mock()
    plugin = VisualRegressionPlugin(
        page=mock_page,
        baseline_dir=tmp_path / "baseline",
        actual_dir=tmp_path / "actual",
        diff_dir=tmp_path / "diff",
    )

    mock_comp = mocker.Mock()
    mock_comp.qualified_name = "test_comp"
    mock_comp.gallery_basic_kwargs = {}

    with pytest.raises(
        AssertionError, match="Missing baseline snapshot for test_comp_basic_light.png"
    ):
        plugin.run_assessment(mock_comp, "basic", "light")


def test_visual_regression_update_snapshot(mocker, tmp_path):
    mock_page = mocker.Mock()
    plugin = VisualRegressionPlugin(
        page=mock_page,
        baseline_dir=tmp_path / "baseline",
        actual_dir=tmp_path / "actual",
        diff_dir=tmp_path / "diff",
        update_snapshots=True,
    )

    mock_page.locator.return_value.screenshot.side_effect = _write_fake_screenshot

    mock_comp = mocker.Mock()
    mock_comp.qualified_name = "test_comp"
    mock_comp.gallery_basic_kwargs = {}

    plugin.run_assessment(mock_comp, "basic", "light")

    # Check that baseline was created
    assert (tmp_path / "baseline" / "test_comp_basic_light.png").exists()


def test_visual_regression_diff_mismatch(mocker, tmp_path):
    mock_diff = mocker.Mock()
    mock_compare = mocker.patch(
        "dj_design_system.testing.plugins.compare_images",
        return_value=ImageComparison(
            mismatched_pixels=50, total_pixels=10_000, diff=mock_diff
        ),
    )

    mock_page = mocker.Mock()

    # Create fake baseline so it doesn't fail on missing
    (tmp_path / "baseline").mkdir()
    (tmp_path / "baseline" / "test_comp_basic_light.png").touch()

    plugin = VisualRegressionPlugin(
        page=mock_page,
        baseline_dir=tmp_path / "baseline",
        actual_dir=tmp_path / "actual",
        diff_dir=tmp_path / "diff",
    )

    mock_comp = mocker.Mock()
    mock_comp.qualified_name = "test_comp"
    mock_comp.gallery_basic_kwargs = {}

    with pytest.raises(AssertionError, match="Visual regression detected"):
        plugin.run_assessment(mock_comp, "basic", "light")

    mock_compare.assert_called_once()
    mock_diff.save.assert_called_once_with(
        tmp_path / "diff" / "test_comp_basic_light.png"
    )


def test_accessibility_plugin_passes(mocker):
    mock_page = mocker.Mock()
    mock_axe = mocker.patch("axe_playwright_python.sync_playwright.Axe")
    mock_axe.return_value.run.return_value.violations_count = 0

    plugin = AccessibilityPlugin(page=mock_page)

    mock_comp = mocker.Mock()
    mock_comp.qualified_name = "test_comp"
    mock_comp.gallery_basic_kwargs = {}

    plugin.run_assessment(mock_comp, "basic", "light")
    mock_axe.return_value.run.assert_called_once()


def test_accessibility_plugin_fails(mocker):
    mock_page = mocker.Mock()
    mock_axe = mocker.patch("axe_playwright_python.sync_playwright.Axe")
    mock_axe.return_value.run.return_value.violations_count = 1
    mock_axe.return_value.run.return_value.generate_report.return_value = (
        "Ensure text has sufficient contrast"
    )

    plugin = AccessibilityPlugin(page=mock_page)

    mock_comp = mocker.Mock()
    mock_comp.qualified_name = "test_comp"
    mock_comp.gallery_basic_kwargs = {}

    with pytest.raises(AssertionError, match="Accessibility violations found"):
        plugin.run_assessment(mock_comp, "basic", "light")


def test_html_validation_plugin_passes(mocker):
    mock_page = mocker.Mock()
    # Mock goto().text() to return valid HTML
    mock_page.goto.return_value.text.return_value = "<div><p>Valid HTML</p></div>"

    plugin = HTMLValidationPlugin(page=mock_page)

    mock_comp = mocker.Mock()
    mock_comp.qualified_name = "test_comp"
    mock_comp.gallery_basic_kwargs = {}

    plugin.run_assessment(mock_comp, "basic", "light")


def test_html_validation_plugin_fails(mocker):
    mock_page = mocker.Mock()
    # Mock goto().text() to return invalid HTML (unclosed div)
    mock_page.goto.return_value.text.return_value = "<div><p>Invalid HTML"

    plugin = HTMLValidationPlugin(page=mock_page)

    mock_comp = mocker.Mock()
    mock_comp.qualified_name = "test_comp"
    mock_comp.gallery_basic_kwargs = {}

    with pytest.raises(AssertionError, match="HTML validation failed"):
        plugin.run_assessment(mock_comp, "basic", "light")


def test_html_validation_plugin_fails_on_canvas_error(mocker):
    """HTMLValidationPlugin fails if the canvas rendered a gallery-canvas-error fallback."""
    mock_page = mocker.Mock()
    mock_page.goto.return_value.text.return_value = (
        '<p class="gallery-canvas-error">Could not render: Variant not found</p>'
    )

    plugin = HTMLValidationPlugin(page=mock_page)

    mock_comp = mocker.Mock()
    mock_comp.qualified_name = "dds__badge"
    mock_comp.gallery_basic_kwargs = {}

    with pytest.raises(AssertionError, match="Canvas failed to render component"):
        plugin.run_assessment(mock_comp, "broken_variant", "light")


def test_strict_html_parser_xhtml_self_closing_void_elements():
    """Verify StrictHTMLParser does not raise errors on XHTML self-closing void elements (#96)."""
    parser = StrictHTMLParser()
    parser.feed(
        '<div><input type="range" /><br /><img src="foo.png" /><source srcset="test.webp" /></div>'
    )
    parser.close()
    assert parser.errors == []


def test_strict_html_parser_detects_real_errors_with_void_elements():
    """Verify StrictHTMLParser still detects real errors when void elements are present."""
    # Mismatched tags around void element
    parser = StrictHTMLParser()
    parser.feed('<div><span><input type="checkbox" /></div></span>')
    parser.close()
    assert any("Mismatched closing tag" in err for err in parser.errors)

    # Unclosed tag with void element
    parser2 = StrictHTMLParser()
    parser2.feed('<div><img src="pic.jpg" />')
    parser2.close()
    assert any("Unclosed tags remaining: div" in err for err in parser2.errors)


def test_strict_html_parser_flags_explicit_closing_void_elements():
    """Verify that explicit closing tags on void elements (e.g. </input>) are flagged as errors."""
    parser = StrictHTMLParser()
    parser.feed('<div><input type="text"></input></div>')
    parser.close()
    assert any("</input>" in err for err in parser.errors)
