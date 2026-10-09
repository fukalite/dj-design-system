"""Built-in gallery shell layout domain component for the dds gallery."""

import typing

from dj_design_system import components, parameters, slots


DEFAULT_BRAND_NAME = "Design System"
DEFAULT_BRAND_URL = "/"
DEFAULT_ACTIVE_THEME = "light"


class GalleryShell(components.BlockComponent):
    """Top-level gallery application shell composing topbar, responsive drawer sidebar, and main content.

    Renders a ``<dds-gallery-shell class="dds-gallery-shell">`` Light DOM
    custom element wrapping:
    - Top header bar region (``[data-shell-topbar]``), defaulting to
      ``{% dds__toolbar %}`` or overridden via ``{% slot "topbar" %}``.
    - Every Layout ``.l-sidebar`` body (``[data-shell-body]``) containing the
      mobile scrim backdrop (``[data-shell-backdrop]``), navigation drawer
      (``[data-shell-sidebar]``, defaulting to ``{% dds__sidebar %}`` or
      overridden via ``{% slot "sidebar" %}``), and primary document surface
      (``<main class="dds-gallery-shell-main" data-surface="docs" data-shell-main>``).

    Args:
        brand_name: Design system name displayed in the topbar and sidebar.
        brand_url: Root gallery URL for brand links.
        nodes: Navigation tree nodes delegated to ``dds__sidebar``.
        active_path: Active route path delegated to ``dds__sidebar``.
        active_variant: Active variant slug or ``Variant`` instance.
        breadcrumbs: Breadcrumb trail items delegated to ``dds__toolbar``.
        themes: Available gallery themes delegated to ``dds__toolbar``.
        active_theme: Active gallery theme identifier.
        search_index: Client-side search index entries delegated to ``dds__toolbar``.

    Example usage::

        {% dds__gallery_shell brand_name="Acme DS" nodes=nav_tree breadcrumbs=breadcrumbs themes=themes active_theme="dark" %}
            {% slot "main" %}
                <h1>Welcome</h1>
            {% endslot %}
        {% enddds__gallery_shell %}
    """

    brand_name = parameters.StrParam(
        description="Design system name.",
        default=DEFAULT_BRAND_NAME,
        required=False,
    )
    brand_url = parameters.StrParam(
        description="Root gallery URL.",
        default=DEFAULT_BRAND_URL,
        required=False,
    )
    nodes = parameters.ListParam(
        description="Navigation tree nodes.",
        default=None,
        required=False,
    )
    active_path = parameters.StrParam(
        description="Active route path.",
        default="",
        required=False,
    )
    active_variant = parameters.StrParam(
        description="Active variant slug or Variant instance.",
        default="",
        required=False,
    )
    breadcrumbs = parameters.ListParam(
        description="Breadcrumb trail items.",
        default=None,
        required=False,
    )
    themes = parameters.ListParam(
        description="Available gallery themes.",
        default=None,
        required=False,
    )
    active_theme = parameters.StrParam(
        description="Active gallery theme identifier.",
        default=DEFAULT_ACTIVE_THEME,
        required=False,
    )
    search_index = parameters.ListParam(
        description="Client-side search index entries.",
        default=None,
        required=False,
    )

    class Meta:
        slots = {
            "topbar": slots.Slot(
                required=False,
                description="Optional custom topbar override.",
            ),
            "sidebar": slots.Slot(
                required=False,
                description="Optional custom sidebar override.",
            ),
            "toolbar_actions": slots.Slot(
                required=False,
                description="Optional extra actions injected into the default toolbar.",
            ),
            "main": slots.Slot(
                required=False,
                description="Optional main content slot (falls back to block body content when instantiated in Python).",
            ),
        }

    def __init__(
        self,
        content: str | None = None,
        *,
        slots: dict[str, typing.Any] | None = None,
        **kwargs: typing.Any,
    ) -> None:
        """Initialise the gallery shell component, normalising variant objects.

        Args:
            content: Optional main body markup when instantiated directly in Python.
            slots: Optional mapping of named slot values (``"topbar"``, ``"sidebar"``,
                ``"toolbar_actions"``, ``"main"``).
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
        """Compute normalized template context for the gallery shell regions and child components.

        Returns:
            Dictionary containing resolved parameters, slot flags, and main content.
        """
        context = super().get_context()
        brand_name = self.brand_name or DEFAULT_BRAND_NAME
        brand_url = self.brand_url or DEFAULT_BRAND_URL
        resolved_theme = self.active_theme or DEFAULT_ACTIVE_THEME
        nodes = list(self.nodes) if self.nodes is not None else []
        breadcrumbs = (
            list(self.breadcrumbs) if self.breadcrumbs is not None else []
        )
        themes = list(self.themes) if self.themes is not None else []
        search_index = (
            list(self.search_index) if self.search_index is not None else []
        )
        has_topbar_slot = bool(self.slots and self.slots.get("topbar"))
        has_sidebar_slot = bool(self.slots and self.slots.get("sidebar"))
        has_toolbar_actions_slot = bool(
            self.slots and self.slots.get("toolbar_actions")
        )
        toolbar_actions_content = (
            self.slots.get("toolbar_actions") if self.slots else None
        ) or ""
        main_slot_val = self.slots.get("main") if self.slots else None
        main_content = main_slot_val if main_slot_val else (self.content or "")
        has_main_content = bool(main_content and str(main_content).strip())

        context["brand_name"] = brand_name
        context["brand_url"] = brand_url
        context["resolved_theme"] = resolved_theme
        context["active_theme"] = resolved_theme
        context["nodes"] = nodes
        context["active_path"] = self.active_path or ""
        context["active_variant"] = self.active_variant or ""
        context["breadcrumbs"] = breadcrumbs
        context["themes"] = themes
        context["search_index"] = search_index
        context["has_topbar_slot"] = has_topbar_slot
        context["has_sidebar_slot"] = has_sidebar_slot
        context["has_toolbar_actions_slot"] = has_toolbar_actions_slot
        context["toolbar_actions_content"] = toolbar_actions_content
        context["main_content"] = main_content
        context["has_main_content"] = has_main_content
        context["slots"] = self.slots
        context["content"] = self.content or ""
        return context
