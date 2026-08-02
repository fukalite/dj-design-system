def test_iteration_engine_combinations(mocker):
    """Verify the engine yields the correct combinations."""
    from dj_design_system.testing.engine import IterationEngine
    
    # Mock some components
    mock_comp = mocker.Mock()
    mock_comp.name = "button"
    
    engine = IterationEngine(components=[mock_comp], themes=["light", "dark"])
    
    # Let's say variants are 'basic' and 'maximal'
    combinations = list(engine.get_combinations())
    
    assert len(combinations) == 4 # 1 comp * 2 variants * 2 themes
    assert (mock_comp, "basic", "light") in combinations
    assert (mock_comp, "maximal", "dark") in combinations

def test_iteration_engine_filtering(mocker):
    """Verify the engine respects filtering hooks."""
    from dj_design_system.testing.engine import IterationEngine
    
    mock_comp = mocker.Mock()
    mock_comp.name = "button"
    
    def filter_hook(comp, variant, theme):
        return theme == "light"
    
    engine = IterationEngine(components=[mock_comp], themes=["light", "dark"])
    engine.add_filter(filter_hook)
    
    combinations = list(engine.get_combinations())
    assert len(combinations) == 2
    for comp, variant, theme in combinations:
        assert theme == "light"

def test_base_plugin_interface(mocker):
    """Verify the base plugin interface is called correctly."""
    from dj_design_system.testing.engine import IterationEngine, AssessmentPlugin
    
    mock_comp = mocker.Mock()
    mock_comp.name = "button"
    engine = IterationEngine(components=[mock_comp], themes=["light"])
    
    class MockPlugin(AssessmentPlugin):
        def __init__(self):
            self.calls = []
        def run_assessment(self, component, variant, theme):
            self.calls.append((component, variant, theme))
            
    plugin = MockPlugin()
    engine.run_plugins([plugin])
    
    assert len(plugin.calls) == 2
    assert plugin.calls[0] == (mock_comp, "basic", "light")
