"""Promoted directory demo component for example_project.demo_components."""

from dj_design_system import components


class PromotedDemoComponent(components.BlockComponent):
    """A simple component demonstrating ``DirectorySettings(promote_to_app=True)``."""

    class Meta:
        name = "demo"

    template_format_str = (
        '<div style="padding: 1rem; border: 1px dashed red;">'
        "Promoted Component: {% slot %}</div>"
    )
