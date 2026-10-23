"""Built-in topbar / header toolbar domain component for the dds gallery."""

import typing

from django.utils import safestring

from dj_design_system import components, parameters, slots


DEFAULT_BRAND_NAME = "Design System"
DEFAULT_BRAND_URL = "/"
DEFAULT_ACTIVE_THEME = "light"


class Toolbar(components.BlockComponent):
    """Top gallery header bar composing navigation toggle, brand, breadcrumbs, search, and theme selector.

    Renders a ``<header class="dds-toolbar" data-surface="topbar">`` landmark
    wrapping an Every Layout ``<l-cluster data-toolbar-inner>`` container split
    into leading navigation/breadcrumb items (``<l-cluster data-toolbar-leading>``)
    and trailing action controls (``<l-cluster data-toolbar-actions>``).

    Delegates child UI primitives in ``toolbar.html`` via template tags:
    - Mobile drawer toggle button via ``{% dds__button %}`` when ``show_menu_toggle=True``.
    - Breadcrumb trail via ``{% dds__breadcrumb %}`` when ``breadcrumbs`` is non-empty
      (unless overridden by ``{% slot "leading" %}``).
    - Instant search box via ``{% dds__search_box %}`` when ``show_search=True``.
    - Theme selector via ``{% dds__theme_select %}`` when ``themes`` is non-empty.

    Args:
        brand_name: Design system brand title displayed in the leading link.
        brand_url: Destination URL for the brand link.
        breadcrumbs: Optional list of breadcrumb trail items passed to ``dds__breadcrumb``.
        themes: Optional list of available themes passed to ``dds__theme_select``.
        active_theme: Active theme identifier passed to ``dds__theme_select``.
        search_index: Optional list of search index entries passed to ``dds__search_box``.
        show_search: Whether to render the search box in the toolbar.
        show_menu_toggle: Whether to render the mobile navigation drawer toggle button.

    Example usage::

        {% dds__toolbar brand_name="Acme Design System" breadcrumbs=breadcrumbs themes=themes active_theme="dark" %}{% enddds__toolbar %}

        {% dds__toolbar brand_name="Docs" show_search=False %}
            {% slot "leading" %}
                <span>v2.0</span>
            {% endslot %}
            {% slot "actions" %}
                {% dds__button "GitHub" variant="ghost" size="sm" href="https://example.com" %}
            {% endslot %}
        {% enddds__toolbar %}
    """

    template_name = "dj_design_system/components/domain/toolbar/toolbar.html"
    _template_name = template_name

    brand_name = parameters.StrParam(
        description="Design system brand title.",
        default=DEFAULT_BRAND_NAME,
        required=False,
    )
    brand_url = parameters.StrParam(
        description="URL for the brand link.",
        default=DEFAULT_BRAND_URL,
        required=False,
    )
    breadcrumbs = parameters.ListParam(
        description="Breadcrumb trail items passed to dds__breadcrumb.",
        default=None,
        required=False,
    )
    themes = parameters.ListParam(
        description="Available themes passed to dds__theme_select.",
        default=None,
        required=False,
    )
    active_theme = parameters.StrParam(
        description="Active theme identifier.",
        default=DEFAULT_ACTIVE_THEME,
        required=False,
    )
    search_index = parameters.ListParam(
        description="Search index entries passed to dds__search_box.",
        default=None,
        required=False,
    )
    show_search = parameters.BoolParam(
        description="Whether to render the search box in the toolbar.",
        default=True,
        required=False,
    )
    show_menu_toggle = parameters.BoolParam(
        description="Whether to render the mobile navigation drawer toggle button.",
        default=True,
        required=False,
    )

    class Meta:
        slots = {
            "leading": slots.Slot(
                required=False,
                description="Optional custom leading/breadcrumb markup.",
            ),
            "actions": slots.Slot(
                required=False,
                description="Optional extra toolbar action controls.",
            ),
        }

    class Media:
        css = "dj_design_system/components/domain/toolbar/toolbar.css"

    def __init__(
        self,
        content: safestring.SafeString | str | None = None,
        *,
        slots: dict[str, safestring.SafeString] | None = None,
        **kwargs: typing.Any,
    ) -> None:
        """Initialise the toolbar component and preserve slot and block content.

        Args:
            content: Optional trailing toolbar action markup.
            slots: Optional mapping of named slot values (``"leading"``, ``"actions"``).
            **kwargs: Component parameter keyword arguments.
        """
        normalized_slots = {
            name: safestring.SafeString(val) if val else val
            for name, val in (slots or {}).items()
        }
        normalized_content = (
            safestring.SafeString(content) if content is not None else ""
        )
        super().__init__(
            content=normalized_content,
            slots=normalized_slots,
            **kwargs,
        )
        self.content = normalized_content

    def get_context(self) -> dict[str, typing.Any]:
        """Compute normalized template context for toolbar regions, slots, and child controls.

        Returns:
            Dictionary containing resolved toolbar parameters, boolean visibility
            flags, ``slots``, and ``content``.
        """
        context = super().get_context()
        brand_name = self.brand_name or DEFAULT_BRAND_NAME
        brand_url = self.brand_url or DEFAULT_BRAND_URL
        breadcrumbs = (
            list(self.breadcrumbs) if self.breadcrumbs is not None else []
        )
        themes = list(self.themes) if self.themes is not None else []
        search_index = (
            list(self.search_index) if self.search_index is not None else []
        )
        active_theme = self.active_theme or DEFAULT_ACTIVE_THEME
        has_breadcrumbs = bool(breadcrumbs)
        has_themes = bool(themes)
        has_leading_slot = bool(self.slots and self.slots.get("leading"))
        has_actions_slot = bool(self.slots and self.slots.get("actions"))
        has_content = bool(self.content and str(self.content).strip())

        context["brand_name"] = brand_name
        context["brand_url"] = brand_url
        context["breadcrumbs"] = breadcrumbs
        context["themes"] = themes
        context["search_index"] = search_index
        context["active_theme"] = active_theme
        context["show_search"] = bool(self.show_search)
        context["show_menu_toggle"] = bool(self.show_menu_toggle)
        context["has_breadcrumbs"] = has_breadcrumbs
        context["has_themes"] = has_themes
        context["has_leading_slot"] = has_leading_slot
        context["has_actions_slot"] = has_actions_slot
        context["has_content"] = has_content
        context["slots"] = self.slots
        context["content"] = self.content or ""
        return context
