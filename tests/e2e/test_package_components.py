import pytest

from dj_design_system import component_registry
from dj_design_system.testing.engine import IterationEngine
from dj_design_system.testing.plugins import (
    AccessibilityPlugin,
    HTMLValidationPlugin,
)
from tests.settings import INTERNAL_COMPONENT_GALLERY_THEMES


# Axe rules about whole pages; a component canvas is a fragment, not a page.
PAGE_LEVEL_RULES = ["landmark-one-main", "page-has-heading-one", "region"]

# Sub-components that carry child ARIA roles (e.g. menuitemradio) whose required
# parent role (role="menu") is provided by their parent component (dds__popout).
STANDALONE_SUBCOMPONENT_EXEMPTIONS = {
    "dds__popout_option": ["aria-required-parent"],
}


def _run_assessment(page, gallery_url, components, *, disabled_rules) -> int:
    engine = IterationEngine(
        components=components,
        themes=list(INTERNAL_COMPONENT_GALLERY_THEMES.keys()),
    )
    combinations = list(engine.get_combinations())
    engine.run_plugins(
        [
            AccessibilityPlugin(
                page=page, base_url=gallery_url, disabled_rules=disabled_rules
            ),
            HTMLValidationPlugin(page=page, base_url=gallery_url),
        ]
    )
    return len(combinations)


@pytest.mark.e2e
def test_all_standard_components(page, base_url, settings):
    """
    Test all standard, non-abstract components shipped by the dj-design-system package itself.
    This runs the accessibility and HTML validation plugins across all 26 built-in components
    and all of their gallery.py variants across light and dark themes.
    """
    settings.DJ_DESIGN_SYSTEM = {
        "GALLERY_THEMES": INTERNAL_COMPONENT_GALLERY_THEMES,
        "GALLERY_DEFAULT_THEME": "light",
    }

    components = component_registry.list_by_app("dj_design_system")
    assert len(components) >= 26, (
        f"Expected at least 26 built-in dj_design_system components, found {len(components)}"
    )

    gallery_url = f"{base_url}/dds"
    top_level = [
        c
        for c in components
        if c.qualified_name not in STANDALONE_SUBCOMPONENT_EXEMPTIONS
    ]
    total_combinations = _run_assessment(
        page=page,
        gallery_url=gallery_url,
        components=top_level,
        disabled_rules=PAGE_LEVEL_RULES,
    )

    for qualified_name, extra_rules in STANDALONE_SUBCOMPONENT_EXEMPTIONS.items():
        sub_components = [c for c in components if c.qualified_name == qualified_name]
        if sub_components:
            total_combinations += _run_assessment(
                page=page,
                gallery_url=gallery_url,
                components=sub_components,
                disabled_rules=PAGE_LEVEL_RULES + extra_rules,
            )

    # Every component has at least basic + maximal + custom gallery.py variants across 2 themes
    assert total_combinations > len(components) * 4
