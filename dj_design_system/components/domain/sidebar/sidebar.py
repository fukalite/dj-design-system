"""Built-in gallery sidebar domain component for the dds gallery."""

import typing

from dj_design_system import components, parameters, slots


DEFAULT_ARIA_LABEL = "Gallery sidebar"
DEFAULT_BRAND_NAME = "Design System"
DEFAULT_BRAND_URL = "/"


class Sidebar(components.BlockComponent):
    """Primary gallery navigation sidebar landmark with header, search, nav tree, and footer.

    Renders an ``<aside class="dds-sidebar" data-surface="sidebar">`` landmark
    containing a brand header (or custom ``header`` slot), optional
    ``{% dds__search_box %}`` instant search, a scrollable body housing
    ``{% dds__nav_tree %}`` and optional block content, and an optional custom
    ``footer`` slot.

    Args:
        brand_name: Design system title shown in the default sidebar header.
        brand_url: Destination URL for the default sidebar brand link.
        nodes: Navigation tree nodes passed to ``dds__nav_tree``.
        active_path: Current active gallery route path.
        active_variant: Optional active variant slug or ``Variant`` instance.
        search_index: Optional search index entries passed to ``dds__search_box``.
        show_search: Whether to render the search box inside the sidebar.
        aria_label: Accessible ``aria-label`` for the ``<aside>`` landmark.

    Example usage::

        {% dds__sidebar brand_name="Design System" nodes=nav_tree active_path=active_path %}
        {% enddds__sidebar %}
    """

    brand_name = parameters.StrParam(
        description="Design system title shown in the sidebar header.",
        default=DEFAULT_BRAND_NAME,
        required=False,
    )
    brand_url = parameters.StrParam(
        description="URL for the sidebar brand link.",
        default=DEFAULT_BRAND_URL,
        required=False,
    )
    nodes = parameters.ListParam(
        description="Navigation tree nodes passed to dds__nav_tree.",
        default=None,
        required=False,
    )
    active_path = parameters.StrParam(
        description="Current active gallery route path.",
        default="",
        required=False,
    )
    active_variant = parameters.StrParam(
        description="Optional active variant slug or Variant instance.",
        default="",
        required=False,
    )
    search_index = parameters.ListParam(
        description="Optional search index entries for sidebar search.",
        default=None,
        required=False,
    )
    show_search = parameters.BoolParam(
        description="Whether to render the search box inside the sidebar.",
        default=False,
        required=False,
    )
    aria_label = parameters.StrParam(
        description="Accessible label for the sidebar landmark.",
        default=DEFAULT_ARIA_LABEL,
        required=False,
    )

    class Meta:
        slots = {
            "header": slots.Slot(
                required=False,
                description="Optional custom sidebar header content.",
            ),
            "footer": slots.Slot(
                required=False,
                description="Optional custom sidebar footer content.",
            ),
        }

    def __init__(
        self,
        content: str | None = None,
        *,
        slots: dict[str, typing.Any] | None = None,
        **kwargs: typing.Any,
    ) -> None:
        """Initialise the sidebar component, normalising variant objects.

        Args:
            content: Optional additional body markup rendered after the nav tree.
            slots: Optional mapping of named slot values (``"header"``, ``"footer"``).
            **kwargs: Component parameter keyword arguments.
        """
        if (
            "active_variant" in kwargs
            and kwargs["active_variant"] is not None
            and not isinstance(kwargs["active_variant"], str)
        ):
            kwargs["active_variant"] = str(
                getattr(
                    kwargs["active_variant"],
                    "name",
                    kwargs["active_variant"],
                )
            )
        super().__init__(
            content=content,
            slots=slots,
            **kwargs,
        )

    def get_context(self) -> dict[str, typing.Any]:
        """Compute normalized template context for the sidebar landmark and slots.

        Returns:
            Dictionary containing normalized sidebar parameters, slot flags,
            and child component data.
        """
        context = super().get_context()
        brand_name = self.brand_name or DEFAULT_BRAND_NAME
        brand_url = self.brand_url or DEFAULT_BRAND_URL
        aria_label = self.aria_label or DEFAULT_ARIA_LABEL
        nodes = list(self.nodes) if self.nodes is not None else []
        search_index = (
            list(self.search_index) if self.search_index is not None else []
        )
        has_header_slot = bool(self.slots and self.slots.get("header"))
        has_footer_slot = bool(self.slots and self.slots.get("footer"))
        has_content = bool(self.content and str(self.content).strip())
        show_search = bool(self.show_search)

        context["brand_name"] = brand_name
        context["brand_url"] = brand_url
        context["aria_label"] = aria_label
        context["nodes"] = nodes
        context["active_path"] = self.active_path or ""
        context["active_variant"] = self.active_variant or ""
        context["search_index"] = search_index
        context["show_search"] = show_search
        context["has_header_slot"] = has_header_slot
        context["has_footer_slot"] = has_footer_slot
        context["has_content"] = has_content
        context["slots"] = self.slots
        context["content"] = self.content or ""
        return context
