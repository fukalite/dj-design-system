from dj_design_system.components import BlockComponent


class PromotedDemoComponent(BlockComponent):
    """
    A simple component used to demonstrate the `promote_to_app` configuration
    in `COMPONENT_DIRECTORIES`.
    """

    class Meta:
        name = "demo"

    template_format_str = '<div style="padding: 1rem; border: 1px dashed red;">Promoted Component: {% slot %}</div>'
