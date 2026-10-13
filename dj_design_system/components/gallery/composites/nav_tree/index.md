## Behaviour & Accessibility

- Renders `<dds-nav-tree class="dds-nav-tree">` wrapping `<nav class="dds-nav-tree-nav" aria-label="{{ aria_label }}">`.
- Expandable folders render `<div data-nav-folder data-state="open|closed" data-folder-id="...">` containing a navigable `<a>` link and a sibling `<button type="button" data-nav-toggle aria-expanded="true|false" aria-controls="dds-nav-children-...">`.
- Active links receive `aria-current="page"` and `data-active="true"`. Variant links also receive `data-variant-link="true"`.
