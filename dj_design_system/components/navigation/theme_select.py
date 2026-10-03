from dj_design_system.components import TagComponent
from dj_design_system.parameters import ListParam, StrParam
from dj_design_system.services.media import FOUNDATION_CSS


def _option(theme) -> dict:
    if isinstance(theme, dict):
        return {"value": theme["value"], "label": theme["label"]}
    return {"value": theme.value, "label": theme.label}


class ThemeSelect(TagComponent):
    """The toolbar's global theme picker.

    Pass the available themes (``Theme`` objects or dicts with ``value`` and
    ``label``) and the active theme's value. Choosing a theme saves it in the
    ``dds_theme`` cookie and reloads the page with ``?theme=``. With fewer
    than two themes there is nothing to choose, so it renders nothing.

    Example usage::

        {% dds__navigation__theme_select available_themes active_theme %}
    """

    template_name = "dj_design_system/ui/navigation/theme_select.html"

    themes = ListParam("The themes to choose from.")
    active = StrParam("The active theme's value.", required=False, default="")

    class Meta:
        positional_args = ["themes", "active"]

    class Media:
        css = [FOUNDATION_CSS, "dj_design_system/ui/navigation/theme_select.css"]
        js = "dj_design_system/ui/navigation/theme_select.js"

    def get_context(self):
        context = super().get_context()
        context["options"] = [_option(theme) for theme in self.themes or []]
        return context
