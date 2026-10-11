from dj_design_system.gallery import GalleryConfig, Variant
from dj_design_system.testing.engine import AssessmentPlugin, IterationEngine


def _light_theme_only(comp, variant, theme) -> bool:
    return theme == "light"


def test_iteration_engine_combinations(mocker):
    """Verify the engine yields the correct combinations."""
    # Mock some components
    mock_comp = mocker.Mock()
    mock_comp.name = "button"

    engine = IterationEngine(components=[mock_comp], themes=["light", "dark"])

    # Let's say variants are 'basic' and 'maximal'
    combinations = list(engine.get_combinations())

    assert len(combinations) == 4  # 1 comp * 2 variants * 2 themes
    assert (mock_comp, "basic", "light") in combinations
    assert (mock_comp, "maximal", "dark") in combinations


def test_iteration_engine_filtering(mocker):
    """Verify the engine respects filtering hooks."""
    mock_comp = mocker.Mock()
    mock_comp.name = "button"

    engine = IterationEngine(components=[mock_comp], themes=["light", "dark"])
    engine.add_filter(_light_theme_only)

    combinations = list(engine.get_combinations())
    assert len(combinations) == 2
    for comp, variant, theme in combinations:
        assert theme == "light"


def test_base_plugin_interface(mocker):
    """Verify the base plugin interface is called correctly."""
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


def test_iteration_engine_includes_gallery_config_variants(mocker):
    """When variants=None, IterationEngine includes all component gallery_config.variants."""
    mock_comp = mocker.Mock()
    mock_comp.name = "badge"
    mock_comp.gallery_config = GalleryConfig(
        variants=[
            Variant(name="basic", kwargs={"label": "Basic"}),
            Variant(name="info", kwargs={"label": "Info", "variant": "info"}),
            Variant(name="warning", kwargs={"label": "Warn", "variant": "warning"}),
            Variant(name="maximal", kwargs={"label": "Max"}),
        ]
    )

    engine = IterationEngine(components=[mock_comp], themes=["light", "dark"])
    combinations = list(engine.get_combinations())

    variants_seen = [v for _, v, t in combinations if t == "light"]
    assert variants_seen == ["basic", "maximal", "info", "warning"]
    assert len(combinations) == 8


def test_iteration_engine_explicit_variants_override_gallery_config(mocker):
    """Explicit variants=[...] restricts iteration to those variants only."""
    mock_comp = mocker.Mock()
    mock_comp.name = "badge"
    mock_comp.gallery_config = GalleryConfig(
        variants=[
            Variant(name="basic", kwargs={"label": "Basic"}),
            Variant(name="info", kwargs={"label": "Info"}),
        ]
    )

    engine = IterationEngine(
        components=[mock_comp],
        themes=["light"],
        variants=["basic"],
    )
    combinations = list(engine.get_combinations())
    assert combinations == [(mock_comp, "basic", "light")]
