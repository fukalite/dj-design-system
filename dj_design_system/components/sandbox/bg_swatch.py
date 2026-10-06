from dj_design_system.components import TagComponent
from dj_design_system.parameters import StrParam
from dj_design_system.services.media import FOUNDATION_CSS


class BgSwatch(TagComponent):
    """A colour swatch for the sandbox toolbar's background popout.

    Without a ``value`` it is the toggle's swatch, which the toolbar's script
    paints with the current background. With a ``value`` (a canvas background
    slug) it is that option's colour chip, followed by its ``label`` if given.

    Example usage::

        {% dds__sandbox__bg_swatch %}
        {% dds__sandbox__bg_swatch value="dark-grey" label="Dark grey" %}
    """

    template_name = "dj_design_system/ui/sandbox/bg_swatch.html"

    value = StrParam(
        "The background's slug, for an option's chip.", required=False, default=""
    )
    label = StrParam(
        "The option's label, shown after its chip.", required=False, default=""
    )

    class Media:
        css = [FOUNDATION_CSS, "dj_design_system/ui/sandbox/bg_swatch.css"]
