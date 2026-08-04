import os

from dj_design_system import component_registry
from dj_design_system.testing.engine import IterationEngine
from dj_design_system.testing.plugins import (
    AccessibilityPlugin,
    HTMLValidationPlugin,
    VisualRegressionPlugin,
)


def test_all_components(page, live_server):
    """
    Run all registered components through our assessment plugins.
    This acts as a full integration test of the components and the testing engine itself.
    """
    # Check if we should update snapshots based on env var (default False)
    update_snapshots = os.environ.get("UPDATE_SNAPSHOTS") == "1"

    # In the example project, the design system is mounted at the root
    base_url = live_server.url

    plugins = [
        AccessibilityPlugin(
            page=page,
            base_url=base_url,
            # Disable page-level rules since components are rendered in an empty canvas
            disabled_rules=["landmark-one-main", "page-has-heading-one", "region"],
        ),
        HTMLValidationPlugin(page=page, base_url=base_url),
        VisualRegressionPlugin(
            page=page,
            base_url=base_url,
            update_snapshots=update_snapshots,
            enable_diff=True,
            threshold=0.1,
            # We save snapshots in a central tests/snapshots directory inside example_project
            baseline_dir="example_project/tests/snapshots/baseline",
            actual_dir="example_project/tests/snapshots/actual",
            diff_dir="example_project/tests/snapshots/diff",
        ),
    ]

    engine = IterationEngine(components=component_registry.list_all())
    engine.run_plugins(plugins)
