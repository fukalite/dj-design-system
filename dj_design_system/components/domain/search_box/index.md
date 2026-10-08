# Search Box (`dds__search_box`)

The `dds__search_box` domain component renders a `<dds-search-box class="dds-search-box">` Light DOM custom element providing client-side instant search across gallery components, folders, and documentation pages.

## When to Use

- In the gallery topbar (`dds__toolbar`) or sidebar header to provide instant keyboard-accessible search across the component and documentation catalogue.
- Anywhere a self-contained combobox search widget with an embedded JSON search index is needed.

## Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `placeholder` | `str` | `"Search components and docs..."` | Search input placeholder text (positional argument 1). |
| `aria_label` | `str` | `"Search components and documentation"` | Accessible label for the combobox search input. |
| `search_index` | `list` | `None` | Optional list of search index entry dicts (`label`, `url`, `type`, `breadcrumb`, `content`). |
| `index_id` | `str` | `"gallery-search-index"` | DOM `id` of the embedded JSON `<script>` element. |
| `input_id` | `str` | `"gallery-search-input"` | DOM `id` for the `<input type="search">` element. |
| `results_id` | `str` | `"gallery-search-results"` | DOM `id` for the floating `role="listbox"` results container. |
| `shortcut_hint` | `str` | `"/"` | Keyboard shortcut hint badge label; pass `""` to omit the `<kbd>` badge. |

## Client-Side Behaviour (`<dds-search-box>`)

- Reads the JSON search index from its internal `<script data-search-index>` element without querying outside its subtree.
- Pressing `/` (outside editable fields) focuses `[data-search-input]`.
- Typing filters the index and populates `[data-search-results]`, setting `data-state="open"` and `aria-expanded="true"`.
- Arrow keys navigate result options, `Enter` activates the selected option (dispatching `dds:search-select`), and `Escape` or outside click closes the results popover.

## Template Usage

```django
{% load design_components %}

{% dds__search_box search_index=search_index %}
{% dds__search_box "Filter components..." shortcut_hint="" %}
```
