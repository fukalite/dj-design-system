from dj_design_system.components import TagComponent
from dj_design_system.parameters import ListParam, StrParam
from dj_design_system.services.media import FOUNDATION_CSS


class Tabs(TagComponent):
    """The toolbar's segmented switch between a ``SplitPane``'s two panes.

    CSS radio tabs: pass the tabs as dicts with the radio's ``id`` and a
    ``label``; ``checked`` is the id of the selected tab (the first by
    default). Its script expects the ``gallery-tab-docs`` and
    ``gallery-tab-sandbox`` ids: it shows the matching pane on narrow
    screens and keeps the ``#pane-sandbox`` URL hash in step. Hidden from
    1800px wide, where both panes show side by side.

    Example usage::

        {% dds__navigation__tabs tabs %}
    """

    template_name = "dj_design_system/ui/navigation/tabs.html"

    items = ListParam("The tabs, each a dict with ``id`` and ``label``.")
    checked = StrParam(
        "The id of the selected tab. Defaults to the first.",
        required=False,
        default="",
    )

    class Meta:
        positional_args = ["items"]

    class Media:
        css = [FOUNDATION_CSS, "dj_design_system/ui/navigation/tabs.css"]
        js = "dj_design_system/ui/navigation/tabs.js"

    def validate_params(self) -> None:
        ids = [tab["id"] for tab in self.items or []]
        if self.checked and self.checked not in ids:
            raise ValueError(f"Tabs 'checked' is not a tab id: {self.checked!r}.")

    def get_context(self):
        context = super().get_context()
        items = list(self.items or [])
        checked = self.checked or (items[0]["id"] if items else "")
        context["tabs"] = [{**tab, "checked": tab["id"] == checked} for tab in items]
        return context
