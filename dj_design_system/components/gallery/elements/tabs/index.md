## Types

```python
from dj_design_system.components.gallery.elements.tabs import TabItem

item = TabItem(
    id="preview",
    label="Preview",
    icon="eye",
    badge="New",
    content="Panel body content",
)
```

## Behaviour & Accessibility

- Renders `{% dds__tabs %}` as `<dds-tabs class="dds-tabs" data-variant="..." data-active-tab="...">` with `tabs`, `active_tab`, and `aria_label` containing `<div role="tablist" class="l-cluster">`.
- Each trigger renders as `<button type="button" role="tab" id="<id_prefix>-tab-<id>" data-tab-trigger="<id>" aria-selected="..." tabindex="...">`.
- When an inline panel or slotted panel exists, `aria-controls="<id_prefix>-panel-<id>"` is bound to the trigger. When used as a panel-less view switcher, dangling `aria-controls` references are omitted.
- Inline `content` values render as `<div role="tabpanel" id="<id_prefix>-panel-<id>" data-tab-panel="<id>" aria-labelledby="<id_prefix>-tab-<id>">`, with `hidden` set on inactive panels.
- Custom rich panels can be supplied inside the block body.
- `<dds-tabs>` handles click activation and keyboard navigation (`ArrowRight`, `ArrowLeft`, `Home`, `End`), updating roving `tabindex`, `aria-selected`, `panel.hidden`, `data-active-tab`, and dispatching a bubbling `dds:tab-change` `CustomEvent` with `detail: { tabId }`. Nested tab instances are strictly isolated from parent event handling.
