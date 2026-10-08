"""Built-in interactive search box domain component for the dds gallery."""

import json
import typing

from django.utils import safestring

from dj_design_system import components, parameters


DEFAULT_PLACEHOLDER = "Search components and docs..."
DEFAULT_ARIA_LABEL = "Search components and documentation"
DEFAULT_INDEX_ID = "gallery-search-index"
DEFAULT_INPUT_ID = "gallery-search-input"
DEFAULT_RESULTS_ID = "gallery-search-results"
DEFAULT_SHORTCUT_HINT = "/"
INDEX_ENTRY_KEYS: tuple[str, ...] = (
    "label",
    "url",
    "type",
    "breadcrumb",
    "content",
)


class SearchBox(components.TagComponent):
    """Client-side instant search input and dropdown results backed by ``<dds-search-box>``.

    Renders a ``<dds-search-box class="dds-search-box">`` Light DOM custom
    element containing a combobox search field (leading search icon,
    ``<input type="search" role="combobox">``, and optional keyboard shortcut
    hint badge), a floating ``<div data-search-results data-surface="popout"
    role="listbox">`` container, and an embedded ``<script type="application/json"
    data-search-index>`` JSON payload so the custom element can read its index
    entirely within its own DOM subtree.

    Args:
        placeholder: Search input placeholder text.
        aria_label: Accessible label for the combobox search input.
        search_index: Optional list of search index entry dicts or objects with
            ``label``, ``url``, ``type``, ``breadcrumb``, and ``content`` fields.
        index_id: DOM id of the JSON script element containing the search index.
        input_id: DOM id for the search input element.
        results_id: DOM id for the listbox results container.
        shortcut_hint: Keyboard shortcut hint badge label (pass ``""`` to hide).

    Example usage::

        {% dds__search_box search_index=search_index %}
        {% dds__search_box "Filter components..." shortcut_hint="⌘K" %}
    """

    template_name = "dj_design_system/components/domain/search_box/search_box.html"
    _template_name = template_name

    placeholder = parameters.StrParam(
        description="Search input placeholder text.",
        default=DEFAULT_PLACEHOLDER,
        required=False,
    )
    aria_label = parameters.StrParam(
        description="Accessible label for the search input.",
        default=DEFAULT_ARIA_LABEL,
        required=False,
    )
    search_index = parameters.ListParam(
        description="Optional list of search index entry dicts.",
        default=None,
        required=False,
    )
    index_id = parameters.StrParam(
        description="DOM id of the JSON script element containing the search index.",
        default=DEFAULT_INDEX_ID,
        required=False,
    )
    input_id = parameters.StrParam(
        description="DOM id for the search input element.",
        default=DEFAULT_INPUT_ID,
        required=False,
    )
    results_id = parameters.StrParam(
        description="DOM id for the listbox results container.",
        default=DEFAULT_RESULTS_ID,
        required=False,
    )
    shortcut_hint = parameters.StrParam(
        description="Keyboard shortcut hint badge label.",
        default=DEFAULT_SHORTCUT_HINT,
        required=False,
    )

    class Meta:
        positional_args = ["placeholder"]

    class Media:
        css = "dj_design_system/components/domain/search_box/search_box.css"
        js = "dj_design_system/components/domain/search_box/search_box.js"

    def get_context(self) -> dict[str, typing.Any]:
        """Build the normalized template context and serialized search index JSON.

        Returns:
            Dictionary containing resolved input/results/index DOM ids,
            combobox labels, ``has_shortcut``, ``normalized_index``, and
            ``search_index_json``.
        """
        context = super().get_context()
        raw_index = list(self.search_index) if self.search_index else []
        normalized_index: list[dict[str, str]] = []

        for raw_entry in raw_index:
            if isinstance(raw_entry, dict):
                raw_label = raw_entry.get("label")
                if raw_label is None:
                    raw_label = raw_entry.get("name", "")
                raw_url = raw_entry.get("url")
                if raw_url is None:
                    raw_url = raw_entry.get("href", "")
                raw_type = raw_entry.get("type", "")
                raw_breadcrumb = raw_entry.get("breadcrumb", "")
                raw_content = raw_entry.get("content", "")
            else:
                raw_label = getattr(raw_entry, "label", None)
                if raw_label is None:
                    raw_label = getattr(raw_entry, "name", str(raw_entry))
                raw_url = getattr(raw_entry, "url", None)
                if raw_url is None:
                    raw_url = getattr(raw_entry, "href", "")
                raw_type = getattr(raw_entry, "type", "")
                raw_breadcrumb = getattr(raw_entry, "breadcrumb", "")
                raw_content = getattr(raw_entry, "content", "")

            normalized_index.append(
                {
                    "label": str(raw_label) if raw_label is not None else "",
                    "url": str(raw_url) if raw_url is not None else "",
                    "type": str(raw_type) if raw_type is not None else "",
                    "breadcrumb": (
                        str(raw_breadcrumb) if raw_breadcrumb is not None else ""
                    ),
                    "content": str(raw_content) if raw_content is not None else "",
                }
            )

        serialized_index = json.dumps(obj=normalized_index).replace("</", "<\\/")
        search_index_json = safestring.SafeString(serialized_index)
        shortcut_hint = str(self.shortcut_hint) if self.shortcut_hint else ""

        context["placeholder"] = (
            str(self.placeholder) if self.placeholder else DEFAULT_PLACEHOLDER
        )
        context["aria_label"] = (
            str(self.aria_label) if self.aria_label else DEFAULT_ARIA_LABEL
        )
        context["index_id"] = str(self.index_id) if self.index_id else DEFAULT_INDEX_ID
        context["input_id"] = str(self.input_id) if self.input_id else DEFAULT_INPUT_ID
        context["results_id"] = (
            str(self.results_id) if self.results_id else DEFAULT_RESULTS_ID
        )
        context["shortcut_hint"] = shortcut_hint
        context["has_shortcut"] = bool(shortcut_hint)
        context["search_index"] = normalized_index
        context["normalized_index"] = normalized_index
        context["search_index_json"] = search_index_json
        return context
