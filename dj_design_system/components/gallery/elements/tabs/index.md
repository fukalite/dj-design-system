# Tabs (`dds__tabs`)

An accessible WAI-ARIA tablist and tabpanel switcher primitive enhanced in place by the `<dds-tabs>` Light DOM custom element.

## When to Use

- Switching between related views within the same context (such as Preview, Source Code, and Documentation panes).
- Grouping parallel content sections without full page navigation.
- Composing tab triggers with optional leading icons (`dds__icon`) and metadata pills (`dds__badge`).

## Parameters

- **`tabs` (`list`, optional, positional):** List of tab items (dictionaries or objects with `id`, `label`, and optional `icon`, `badge`, and `content`).
- **`active_tab` (`str`, optional, default `""`):** ID of the initially active tab. If omitted or not found in `tabs`, defaults to the first tab's `id`.
- **`aria_label` (`str`, optional, default `"Tabs"`):** Accessible label applied to the `<div role="tablist">` container.
- **`id_prefix` (`str`, optional, default `"dds"`):** DOM ID prefix for tab triggers (`<id_prefix>-tab-<id>`) and panels (`<id_prefix>-panel-<id>`).

## Behaviour & Accessibility

- Renders `<dds-tabs class="dds-tabs" data-active-tab="...">` containing `<div role="tablist" class="l-cluster">`.
- Each trigger renders as `<button type="button" role="tab" id="<id_prefix>-tab-<id>" data-tab-trigger="<id>" aria-selected="..." aria-controls="<id_prefix>-panel-<id>" tabindex="...">`.
- Inline `content` values render as `<div role="tabpanel" id="<id_prefix>-panel-<id>" data-tab-panel="<id>" aria-labelledby="<id_prefix>-tab-<id>">`, with `hidden` set on inactive panels. Callers may also supply custom `<div role="tabpanel" data-tab-panel="...">` blocks inside `{% dds__tabs %}...{% enddds__tabs %}`.
- `<dds-tabs>` handles click activation and keyboard navigation (`ArrowRight`, `ArrowLeft`, `Home`, `End`), updating roving `tabindex`, `aria-selected`, `panel.hidden`, `data-active-tab`, and dispatching a bubbling `dds:tab-change` `CustomEvent` with `detail: { tabId }`.

## Example Usage

```django
{% load design_components %}

{% dds__tabs tabs=tab_items active_tab="overview" aria_label="Component views" %}
{% enddds__tabs %}

{% dds__tabs tabs=tab_headers active_tab="preview" %}
  <div role="tabpanel" id="dds-panel-preview" data-tab-panel="preview" aria-labelledby="dds-tab-preview">
    Custom slotted panel content
  </div>
{% enddds__tabs %}
```
