import pytest

from dj_design_system import component_registry
from dj_design_system.testing.engine import IterationEngine
from dj_design_system.testing.plugins import (
    AccessibilityPlugin,
    HTMLValidationPlugin,
)


# Axe rules about whole pages; a component canvas is a fragment, not a page.
PAGE_LEVEL_RULES = ["landmark-one-main", "page-has-heading-one", "region"]


@pytest.mark.e2e
def test_all_standard_components(page, base_url):
    """
    Test all standard, non-abstract components shipped by the dj-design-system package itself.
    This runs the accessibility and HTML validation plugins. Screenshots of the
    gallery, rendered deterministically in the pinned Playwright container, are
    covered by the visual regression suite in ``tests/e2e/visual/``.
    """
    components = component_registry.list_by_app("dj_design_system")

    if not components:
        pytest.skip("No standard components shipped by the main package yet.")

    gallery_url = f"{base_url}/dds"
    plugins = [
        AccessibilityPlugin(
            page=page, base_url=gallery_url, disabled_rules=PAGE_LEVEL_RULES
        ),
        HTMLValidationPlugin(page=page, base_url=gallery_url),
    ]

    engine = IterationEngine(components=components)
    engine.run_plugins(plugins)
