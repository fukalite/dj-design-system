## Behaviour & Accessibility

- Renders `<dds-nav-tree class="dds-nav-tree">` wrapping
  `<nav class="dds-nav-tree-nav" aria-label="{{ aria_label }}">`, and exports
  the `NavTreeNode` dataclass alongside `NavTree`.
- Expandable app groups and folders render
  `<div data-nav-group data-state="open|closed" data-group-id="...">` and
  `<div data-nav-folder data-state="open|closed" data-folder-id="...">`
  containing a navigable `<a>` link and a sibling
  `<button type="button" data-nav-toggle aria-expanded="true|false"`
  `aria-controls="dds-nav-children-...">`.
  `<dds-nav-tree>` exposes `applyExpandedState(stateMap)` (keeping ancestors of
  an active child expanded) and emits `dds:nav-tree-ready` on connect plus
  `dds:nav-toggle` on toggle, while `PaneManager` persists state in
  `localStorage` (`dds-nav-expanded-state`).
- Active links receive `aria-current="page"` and `data-active="true"`.
  Variant links also receive `data-variant-link="true"`.
