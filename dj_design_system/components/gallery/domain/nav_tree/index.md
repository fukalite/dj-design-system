# Navigation Tree (`dds__nav_tree`)

A recursive sidebar navigation tree domain component (`<dds-nav-tree>`) that renders app groups, collapsible folder hierarchies, component links, documentation links, and variant links with automatic active-route highlighting and ancestor folder expansion.

## When to Use

- Rendering the primary component and documentation navigation hierarchy inside the gallery sidebar.
- Displaying multi-level tree structures with independent folder navigation links and expand/collapse disclosure buttons.

## Parameters

- **`nodes` (`list`, optional, positional):** Top-level navigation nodes (`NavNode` dataclass instances, dictionaries, or duck-typed node objects). Normalised up to 4 levels deep (`depth` `0` through `3`) in `get_context()`.
- **`active_path` (`str`, optional, default `""`):** Current active gallery route path used to mark the matching item with `aria-current="page"` and expand ancestor folders on initial render.
- **`active_variant` (`str`, optional, default `""`):** Active variant slug or `Variant` instance used to match variant leaf nodes.
- **`aria_label` (`str`, optional, default `"Component navigation"`):** Accessible label applied to the `<nav class="dds-nav-tree-nav">` landmark.

## Behaviour & Accessibility

- Renders `<dds-nav-tree class="dds-nav-tree">` wrapping `<nav class="dds-nav-tree-nav" aria-label="{{ aria_label }}">`.
- Expandable folders render `<div data-nav-folder data-state="open|closed" data-folder-id="...">` containing a navigable `<a>` link and a sibling `<button type="button" data-nav-toggle aria-expanded="true|false" aria-controls="dds-nav-children-...">`.
- Active links receive `aria-current="page"` and `data-active="true"`. Variant links also receive `data-variant-link="true"`.

## Example Usage

```django
{% load design_components %}

{% dds__nav_tree nodes=nav_tree active_path=active_path active_variant=active_variant %}
{% dds__nav_tree nav_tree aria_label="Design system navigation" %}
```
