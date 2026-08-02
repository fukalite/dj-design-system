import pytest
from pathlib import Path

def test_visual_regression_plugin_basic(mocker):
    """Verify the snapshot plugin properly hooks into the iteration engine and captures states."""
    from dj_design_system.testing.plugins import VisualRegressionPlugin
    
    mock_page = mocker.Mock()
    
    plugin = VisualRegressionPlugin(page=mock_page, base_url="http://localhost:8000", enable_diff=False)
    
    mock_comp = mocker.Mock()
    mock_comp.qualified_name = "test_app__test_component"
    mock_comp.gallery_basic_kwargs = {"title": "Test Title", "is_active": True, "count": None}
    
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
    from dj_design_system.testing.plugins import VisualRegressionPlugin
    
    mock_page = mocker.Mock()
    plugin = VisualRegressionPlugin(page=mock_page, base_url="http://localhost:8000", enable_diff=False)
    
    mock_comp = mocker.Mock()
    mock_comp.qualified_name = "test_app__test_component"
    
    class GalleryParam:
        def __init__(self, value):
            self.value = value
            
    mock_comp.gallery_maximal_kwargs = {"param1": GalleryParam("val1"), "is_active": False}
    
    plugin.run_assessment(mock_comp, "maximal", "dark")
    url = mock_page.goto.call_args[0][0]
    assert "param1=val1" in url
    assert "is_active=false" in url


def test_visual_regression_plugin_unknown_variant(mocker):
    from dj_design_system.testing.plugins import VisualRegressionPlugin
    
    mock_page = mocker.Mock()
    plugin = VisualRegressionPlugin(page=mock_page, base_url="http://localhost:8000", enable_diff=False)
    
    mock_comp = mocker.Mock()
    mock_comp.qualified_name = "test_app__test_component"
    
    plugin.run_assessment(mock_comp, "unknown", "light")
    url = mock_page.goto.call_args[0][0]
    assert "test_app__test_component" in url


def test_visual_regression_missing_baseline(mocker, tmp_path):
    from dj_design_system.testing.plugins import VisualRegressionPlugin
    
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
    
    with pytest.raises(AssertionError, match="Missing baseline snapshot for test_comp_basic_light.png"):
        plugin.run_assessment(mock_comp, "basic", "light")


def test_visual_regression_update_snapshot(mocker, tmp_path):
    from dj_design_system.testing.plugins import VisualRegressionPlugin
    
    mock_page = mocker.Mock()
    plugin = VisualRegressionPlugin(
        page=mock_page,
        baseline_dir=tmp_path / "baseline",
        actual_dir=tmp_path / "actual",
        diff_dir=tmp_path / "diff",
        update_snapshots=True
    )
    
    # Mock screenshot to actually create a file
    def mock_screenshot(path):
        Path(path).write_bytes(b"fake image data")
        
    mock_page.locator.return_value.screenshot.side_effect = mock_screenshot
    
    mock_comp = mocker.Mock()
    mock_comp.qualified_name = "test_comp"
    mock_comp.gallery_basic_kwargs = {}
    
    plugin.run_assessment(mock_comp, "basic", "light")
    
    # Check that baseline was created
    assert (tmp_path / "baseline" / "test_comp_basic_light.png").exists()


def test_visual_regression_diff_mismatch(mocker, tmp_path):
    from dj_design_system.testing.plugins import VisualRegressionPlugin
    
    # Mock Image and pixelmatch
    mock_image = mocker.patch("dj_design_system.testing.plugins.Image")
    mock_img_obj = mocker.Mock()
    mock_img_obj.size = (100, 100)
    mock_image.open.return_value.convert.return_value = mock_img_obj
    
    mock_pixelmatch = mocker.patch("dj_design_system.testing.plugins.pixelmatch")
    mock_pixelmatch.return_value = 50  # 50 pixels differ
    
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
        
    mock_pixelmatch.assert_called_once()


def test_accessibility_plugin_passes(mocker):
    from dj_design_system.testing.plugins import AccessibilityPlugin
    
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
    from dj_design_system.testing.plugins import AccessibilityPlugin
    
    mock_page = mocker.Mock()
    mock_axe = mocker.patch("axe_playwright_python.sync_playwright.Axe")
    mock_axe.return_value.run.return_value.violations_count = 1
    mock_axe.return_value.run.return_value.generate_report.return_value = "Ensure text has sufficient contrast"
    
    plugin = AccessibilityPlugin(page=mock_page)
    
    mock_comp = mocker.Mock()
    mock_comp.qualified_name = "test_comp"
    mock_comp.gallery_basic_kwargs = {}
    
    with pytest.raises(AssertionError, match="Accessibility violations found"):
        plugin.run_assessment(mock_comp, "basic", "light")


def test_html_validation_plugin_passes(mocker):
    from dj_design_system.testing.plugins import HTMLValidationPlugin
    
    mock_page = mocker.Mock()
    # Mock locator().inner_html() to return valid HTML
    mock_page.locator.return_value.inner_html.return_value = "<div><p>Valid HTML</p></div>"
    
    plugin = HTMLValidationPlugin(page=mock_page)
    
    mock_comp = mocker.Mock()
    mock_comp.qualified_name = "test_comp"
    mock_comp.gallery_basic_kwargs = {}
    
    plugin.run_assessment(mock_comp, "basic", "light")


def test_html_validation_plugin_fails(mocker):
    from dj_design_system.testing.plugins import HTMLValidationPlugin
    
    mock_page = mocker.Mock()
    # Mock locator().inner_html() to return invalid HTML (unclosed div)
    mock_page.locator.return_value.inner_html.return_value = "<div><p>Invalid HTML"
    
    plugin = HTMLValidationPlugin(page=mock_page)
    
    mock_comp = mocker.Mock()
    mock_comp.qualified_name = "test_comp"
    mock_comp.gallery_basic_kwargs = {}
    
    with pytest.raises(AssertionError, match="HTML validation failed"):
        plugin.run_assessment(mock_comp, "basic", "light")
