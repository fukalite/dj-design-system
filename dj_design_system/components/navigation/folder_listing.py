from dj_design_system.components import TagComponent
from dj_design_system.components.navigation.nodes import normalise
from dj_design_system.components.primitives.icon import Icon
from dj_design_system.parameters import ListParam, StrParam
from dj_design_system.services.media import FOUNDATION_CSS


def _icon(name: str) -> str:
    return Icon(
        name=name,
        extra_classes=f"gallery-folder-list__icon gallery-folder-list__icon--{name}",
    ).render()


class FolderListing(TagComponent):
    """A folder's contents: one link per sub-folder, component or document.

    Each item shows an icon for its type. Pass ``NavNode`` objects or dicts
    with ``type``, ``label``, ``url`` and ``children``. With no items it says
    the folder is empty.

    Example usage::

        {% dds__navigation__folder_listing children %}
    """

    template_name = "dj_design_system/ui/navigation/folder_listing.html"

    items = ListParam("The folder's children.")
    title = StrParam("Heading above the list.", required=False, default="Contents")

    class Meta:
        positional_args = ["items"]

    class Media:
        # icon.css first: the listing's icon colour overrides the Icon default.
        css = [
            FOUNDATION_CSS,
            "dj_design_system/ui/primitives/icon.css",
            "dj_design_system/ui/navigation/folder_listing.css",
        ]

    def get_context(self):
        context = super().get_context()
        entries = []
        for node in map(normalise, self.items or []):
            if node["children"]:
                icon = _icon("folder")
            elif node["type"] == "component":
                icon = _icon("component")
            elif node["type"] == "document":
                icon = _icon("doc")
            else:
                icon = ""
            entries.append({**node, "icon": icon})
        context["entries"] = entries
        return context
