# Folder Listing (`dds__folder_listing`)

A domain gallery component that renders the index overview for a navigation folder node when no custom `index.md` overrides the page.

## When to Use

- Displaying child folders, components, documentation pages, and variants inside a gallery directory view.
- Providing an empty-state fallback when a registered directory has no visible child entries.
- Surfacing a contextual authoring hint (`show_debug_hint=True`) in debug mode to explain how to replace the generated listing with a custom `index.md` file.

## Parameters

- **`title` (`str`, optional, default `""`, positional):** Folder heading title rendered inside `<h1 data-folder-title>` when non-empty.
- **`items` (`list`, optional, default `None`, positional):** Child `NavNode` instances or item dictionaries (`label`, `url`, `node_type`/`type`, `icon`, `children`, `has_children`, `is_component`, `is_document`, `is_variant`) to render as cards.
- **`empty_message` (`str`, optional, default `"This folder is empty."`):** Fallback message rendered inside `<p data-folder-empty>` when `items` is empty.
- **`show_debug_hint` (`bool`, optional, default `False`):** When `True`, renders an informational `dds__notice` callout explaining how to add an `index.md` file.

## Behaviour & Accessibility

- Renders `<section class="dds-folder-listing" data-surface="docs">` wrapping an Every Layout `<l-stack>`.
- Normalises all item fields in `get_context()`, resolving semantic icons (`folder`, `component`, `doc`, `code`), `dds__badge` labels and variants, and singular/plural child counts (`"1 item"` vs `"N items"`) without template filters.
- Uses `<ul class="l-grid" data-folder-grid>` for responsive auto-fit card layout and `<l-cluster>` inside each `<a data-folder-card>` link.

## Example Usage

```django
{% load design_components %}

{% dds__folder_listing "Elements" items %}
{% dds__folder_listing title=node.label items=node.children show_debug_hint=debug %}
```
