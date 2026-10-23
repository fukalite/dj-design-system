import pytest

from dj_design_system import component_registry
from dj_design_system.testing.engine import IterationEngine
from dj_design_system.testing.plugins import (
    AccessibilityPlugin,
    HTMLValidationPlugin,
)


# Axe rules about whole pages; a component canvas is a fragment, not a page.
PAGE_LEVEL_RULES = ["landmark-one-main", "page-has-heading-one", "region"]

# Sub-components that carry child ARIA roles (e.g. menuitemradio) whose required
# parent role (role="menu") is provided by their parent component (dds__popout).
STANDALONE_SUBCOMPONENT_EXEMPTIONS = {
    "dds__popout_option": ["aria-required-parent"],
}


def _run_assessment(page, gallery_url, components, *, disabled_rules) -> None:
    engine = IterationEngine(components=components)
    engine.run_plugins(
        [
            AccessibilityPlugin(
                page=page, base_url=gallery_url, disabled_rules=disabled_rules
            ),
            HTMLValidationPlugin(page=page, base_url=gallery_url),
        ]
    )


@pytest.mark.e2e
def test_all_standard_components(page, base_url):
    """
    Test all standard, non-abstract components shipped by the dj-design-system package itself.
    This runs the accessibility and HTML validation plugins across all built-in components.
    """
    components = component_registry.list_by_app("dj_design_system")

    if not components:
        pytest.skip("No standard components shipped by the main package yet.")

    gallery_url = f"{base_url}/dds"
    top_level = [
        c
        for c in components
        if c.qualified_name not in STANDALONE_SUBCOMPONENT_EXEMPTIONS
    ]
    _run_assessment(
        page,
        gallery_url,
        top_level,
        disabled_rules=PAGE_LEVEL_RULES,
    )

    for qualified_name, extra_rules in STANDALONE_SUBCOMPONENT_EXEMPTIONS.items():
        sub_components = [c for c in components if c.qualified_name == qualified_name]
        if sub_components:
            _run_assessment(
                page,
                gallery_url,
                sub_components,
                disabled_rules=PAGE_LEVEL_RULES + extra_rules,
            )
