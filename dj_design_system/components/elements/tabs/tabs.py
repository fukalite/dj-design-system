"""Built-in accessible tabs and tabpanel switcher element component."""

from typing import Any

from dj_design_system.components import BlockComponent
from dj_design_system.parameters import ListParam, StrParam


DEFAULT_ARIA_LABEL = "Tabs"
TAB_DOM_ID_PREFIX = "dds-tab-"
PANEL_DOM_ID_PREFIX = "dds-panel-"


class Tabs(BlockComponent):
    """Accessible WAI-ARIA tablist and tabpanel switcher primitive.

    Renders a ``<dds-tabs class="dds-tabs">`` Light DOM custom element containing
    a ``<div role="tablist" class="l-cluster">`` with ``<button role="tab">``
    triggers and associated ``<div role="tabpanel">`` regions.

    Tab items may be passed as dictionaries or objects with ``id`` and ``label``
    plus optional ``icon``, ``badge``, and ``content`` attributes. Callers can
    provide panel content inline via each tab item's ``content`` key, or pass
    custom ``<div role="tabpanel" data-tab-panel="...">`` markup inside the
    component's block body.

    Example usage::

        {% dds__tabs tabs=tab_items active_tab="overview" aria_label="Component views" %}
        {% enddds__tabs %}

        {% dds__tabs tabs=tab_headers active_tab="preview" %}
            <div role="tabpanel" id="dds-panel-preview" data-tab-panel="preview" aria-labelledby="dds-tab-preview">
                Custom preview content
            </div>
        {% enddds__tabs %}
    """

    template_name = "dj_design_system/components/elements/tabs/tabs.html"
    _template_name = template_name

    tabs = ListParam(
        description="List of tab items (dicts with 'id', 'label', and optional 'icon', 'badge', 'content').",
        default=[],
        required=False,
    )
    active_tab = StrParam(
        description="ID of the initially active tab; defaults to the first tab.",
        default="",
        required=False,
    )
    aria_label = StrParam(
        description="Accessible label for the tablist.",
        default=DEFAULT_ARIA_LABEL,
        required=False,
    )

    class Meta:
        positional_args = ["tabs"]

    class Media:
        css = "dj_design_system/components/elements/tabs/tabs.css"
        js = "dj_design_system/components/elements/tabs/tabs.js"

    @staticmethod
    def _extract_raw_tab(raw_item: Any) -> dict[str, Any]:
        """Extract raw string fields from a dict or object tab item.

        Args:
            raw_item: Dictionary or object defining ``id``, ``label``, and
                optional ``icon``, ``badge``, and ``content``.

        Returns:
            Dictionary with string-normalized ``id``, ``label``, ``icon``,
            ``badge``, and ``content`` values.
        """
        if isinstance(raw_item, dict):
            raw_id = raw_item.get("id")
            raw_label = raw_item.get("label")
            raw_icon = raw_item.get("icon")
            raw_badge = raw_item.get("badge")
            raw_content = raw_item.get("content")
        else:
            raw_id = getattr(raw_item, "id", None)
            raw_label = getattr(raw_item, "label", None)
            raw_icon = getattr(raw_item, "icon", None)
            raw_badge = getattr(raw_item, "badge", None)
            raw_content = getattr(raw_item, "content", None)

        tab_id = str(raw_id) if raw_id is not None else ""
        label = str(raw_label) if raw_label is not None else ""
        icon = str(raw_icon) if raw_icon is not None else ""
        badge = str(raw_badge) if raw_badge is not None else ""
        content = (
            raw_content
            if isinstance(raw_content, str)
            else (str(raw_content) if raw_content is not None else "")
        )

        return {
            "id": tab_id,
            "label": label,
            "icon": icon,
            "badge": badge,
            "content": content,
        }

    @classmethod
    def _build_normalized_tab(
        cls,
        extracted: dict[str, Any],
        *,
        resolved_active: str,
    ) -> dict[str, Any]:
        """Build a complete normalized tab dictionary for template rendering.

        Args:
            extracted: Raw extracted tab fields from ``_extract_raw_tab``.
            resolved_active: The resolved active tab ID.

        Returns:
            Normalized tab dictionary with DOM IDs, ARIA state, and content flags.
        """
        tab_id = extracted["id"]
        icon = extracted["icon"]
        badge = extracted["badge"]
        content = extracted["content"]
        is_active = bool(tab_id == resolved_active)

        return {
            "id": tab_id,
            "label": extracted["label"],
            "icon": icon,
            "has_icon": bool(icon),
            "badge": badge,
            "has_badge": bool(badge),
            "content": content,
            "has_content": bool(content),
            "tab_dom_id": f"{TAB_DOM_ID_PREFIX}{tab_id}",
            "panel_dom_id": f"{PANEL_DOM_ID_PREFIX}{tab_id}",
            "is_active": is_active,
            "aria_selected": "true" if is_active else "false",
            "tabindex": "0" if is_active else "-1",
        }

    def get_context(self) -> dict[str, Any]:
        """Compute normalized tabs, active tab state, and panel flags.

        Returns:
            Dictionary containing ``normalized_tabs``, ``resolved_active``,
            ``aria_label``, ``has_inline_panels``, and ``has_slot_content``.
        """
        context = super().get_context()
        raw_tabs = list(self.tabs) if self.tabs else []
        extracted_tabs = [self._extract_raw_tab(raw_item=item) for item in raw_tabs]
        tab_ids = [item["id"] for item in extracted_tabs]

        if self.active_tab and self.active_tab in tab_ids:
            resolved_active = str(self.active_tab)
        elif extracted_tabs:
            resolved_active = extracted_tabs[0]["id"]
        else:
            resolved_active = ""

        normalized_tabs = [
            self._build_normalized_tab(
                extracted=item,
                resolved_active=resolved_active,
            )
            for item in extracted_tabs
        ]
        slot_content = context.get("content")
        resolved_slot_content = (
            slot_content
            if isinstance(slot_content, str)
            else (str(slot_content) if slot_content is not None else "")
        )

        context["aria_label"] = self.aria_label or DEFAULT_ARIA_LABEL
        context["resolved_active"] = resolved_active
        context["normalized_tabs"] = normalized_tabs
        context["has_inline_panels"] = any(
            item["has_content"] for item in normalized_tabs
        )
        context["content"] = resolved_slot_content
        context["has_slot_content"] = bool(resolved_slot_content.strip())
        return context
