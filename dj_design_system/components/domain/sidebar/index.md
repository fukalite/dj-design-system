# Sidebar (`dds__sidebar`)

A gallery sidebar landmark domain component (`<aside class="dds-sidebar" data-surface="sidebar">`) that composes the brand header (or custom `header` slot), optional instant search (`{% dds__search_box %}`), scrollable navigation tree (`{% dds__nav_tree %}`), and an optional `footer` slot.

## When to Use

- Rendering the primary left-hand navigation landmark inside the gallery shell.
- Customising the gallery sidebar brand header or footer while retaining standard search and navigation tree behaviour.

## Parameters

- **`brand_name` (`str`, optional, default `"Design System"`):** Design system title shown in the sidebar header when no `header` slot is provided.
- **`brand_url` (`str`, optional, default `"/"`):** URL for the sidebar brand link.
- **`nodes` (`list`, optional, default `None`):** Navigation tree nodes passed to `{% dds__nav_tree %}`.
- **`active_path` (`str`, optional, default `""`):** Current active gallery route path passed to `{% dds__nav_tree %}`.
- **`active_variant` (`str`, optional, default `""`):** Optional active variant slug or `Variant` instance passed to `{% dds__nav_tree %}`.
- **`search_index` (`list`, optional, default `None`):** Optional search index entries passed to `{% dds__search_box %}` when `show_search=True`.
- **`show_search` (`bool`, optional, default `False`):** Whether to render `<div data-sidebar-search>{% dds__search_box %}</div>` inside the sidebar.
- **`aria_label` (`str`, optional, default `"Gallery sidebar"`):** Accessible label applied to the `<aside class="dds-sidebar">` landmark.

## Slots

- **`header` (optional):** Custom markup rendered inside `<div data-sidebar-header>` in place of the default `<a data-sidebar-brand>` link.
- **`footer` (optional):** Custom markup rendered inside `<div data-sidebar-footer>` at the bottom of the sidebar.

## Example Usage

```django
{% load design_components %}

{% dds__sidebar brand_name="Design System" brand_url="/gallery/" nodes=nav_tree active_path=active_path show_search=True search_index=search_index %}
  {% slot "footer" %}
    <span>v1.0.0</span>
  {% endslot %}
{% enddds__sidebar %}
```
