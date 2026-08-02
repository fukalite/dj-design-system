import os
import pytest

from dj_design_system import component_registry
from dj_design_system.testing.engine import IterationEngine
from dj_design_system.testing.plugins import (
    AccessibilityPlugin,
    HTMLValidationPlugin,
    VisualRegressionPlugin,
)


@pytest.mark.e2e
def test_all_standard_components(page, base_url):
    """
    Test all standard, non-abstract components shipped by the dj-design-system package itself.
    This will run against all plugins (A11y, HTML Validation, and Visual Regression).
    """
    # Collect components that belong to the main 'dj_design_system' package
    components = [
        info.component_class for info in component_registry.list_all()
        if info.app_label == "dj_design_system"
    ]

    if not components:
        pytest.skip("No standard components shipped by the main package yet.")

    plugins = [
        AccessibilityPlugin(page=page, base_url=base_url),
        HTMLValidationPlugin(page=page, base_url=base_url),
        VisualRegressionPlugin(
            page=page,
            base_url=base_url,
            update_snapshots=os.environ.get("UPDATE_SNAPSHOTS") == "1",
            baseline_dir="tests/e2e/snapshots/baseline",
            actual_dir="tests/e2e/snapshots/actual",
            diff_dir="tests/e2e/snapshots/diff",
        ),
    ]

    engine = IterationEngine(components=components)
    engine.run_plugins(plugins)
