import pytest

def test_visual_regression_plugin_basic(mocker):
    """Verify the snapshot plugin properly hooks into the iteration engine and captures states."""
    from dj_design_system.testing.plugins import VisualRegressionPlugin
    
    mock_page = mocker.Mock()
    
    plugin = VisualRegressionPlugin(page=mock_page, base_url="http://localhost:8000")
    
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
    mock_page.screenshot.assert_called_once()
    screenshot_kwargs = mock_page.screenshot.call_args[1]
    
    # The path should include the component, variant, and theme
    path = str(screenshot_kwargs.get("path", ""))
    assert "test_app__test_component" in path
    assert "basic" in path
    assert "light" in path


def test_visual_regression_plugin_maximal(mocker):
    from dj_design_system.testing.plugins import VisualRegressionPlugin
    
    mock_page = mocker.Mock()
    plugin = VisualRegressionPlugin(page=mock_page, base_url="http://localhost:8000")
    
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
    plugin = VisualRegressionPlugin(page=mock_page, base_url="http://localhost:8000")
    
    mock_comp = mocker.Mock()
    mock_comp.qualified_name = "test_app__test_component"
    
    plugin.run_assessment(mock_comp, "unknown", "light")
    url = mock_page.goto.call_args[0][0]
    assert "test_app__test_component" in url
