import pytest

from dj_design_system import component_registry
from dj_design_system.testing.engine import IterationEngine
from dj_design_system.testing.plugins import (
    AccessibilityPlugin,
    HTMLValidationPlugin,
)


# Axe rules about whole pages; a component canvas is a fragment, not a page.
PAGE_LEVEL_RULES = ["landmark-one-main", "page-has-heading-one", "region"]

# Known issues carried over unchanged from the legacy gallery design, which
# the gallery rebuild moves into components without restyling:
# (component, example) -> extra axe rules to skip for that example only.
LEGACY_EXEMPTIONS = {
    # The debug hint's faded muted text (opacity: 0.6) is below WCAG AA
    # contrast; see issue #115. The maximal example renders the hint variant.
    ("dds__primitives__notice", "maximal"): ["color-contrast"],
    # Breadcrumb links are told apart from the surrounding text by colour
    # only; see issue #117. The maximal example has text around its link.
    ("dds__layout__toolbar", "maximal"): ["link-in-text-block"],
    # Folders put a link inside <summary> (nested interactive controls);
    # fixed by #112. The nav's pale text is designed for the sidebar's dark
    # background, which a standalone canvas doesn't have, so contrast can
    # only be judged in the gallery.
    ("dds__navigation__nav_tree", "basic"): ["nested-interactive", "color-contrast"],
    ("dds__navigation__nav_tree", "maximal"): ["nested-interactive", "color-contrast"],
}


def _run(page, gallery_url, components, *, disabled_rules, include) -> None:
    engine = IterationEngine(components=components)
    engine.add_filter(lambda comp, variant, theme: include(comp, variant))
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
    This runs the accessibility and HTML validation plugins. Screenshots of the
    gallery, rendered deterministically in the pinned Playwright container, are
    covered by the visual regression suite in ``tests/e2e/visual/``.
    """
    components = component_registry.list_by_app("dj_design_system")

    if not components:
        pytest.skip("No standard components shipped by the main package yet.")

    gallery_url = f"{base_url}/dds"

    def exempt(comp, variant):
        return (comp.qualified_name, variant) in LEGACY_EXEMPTIONS

    _run(
        page,
        gallery_url,
        components,
        disabled_rules=PAGE_LEVEL_RULES,
        include=lambda comp, variant: not exempt(comp, variant),
    )
    for (name, example), rules in LEGACY_EXEMPTIONS.items():
        _run(
            page,
            gallery_url,
            [c for c in components if c.qualified_name == name],
            disabled_rules=PAGE_LEVEL_RULES + rules,
            include=lambda comp, variant, example=example: variant == example,
        )
