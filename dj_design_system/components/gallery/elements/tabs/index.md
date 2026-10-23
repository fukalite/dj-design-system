# Tabs (`dds__tabs`)

An accessible WAI-ARIA tablist and tabpanel switcher primitive enhanced in place by the `<dds-tabs>` Light DOM custom element.

## When to Use

- Switching between related views within the same context (such as Preview, Source Code, and Documentation panes).
- Grouping parallel content sections without full page navigation.
- Rendering standalone view switchers (such as Docs vs. Sandbox headers) via `variant="switcher"`.
- Composing tab triggers with optional leading icons (`dds__icon`) and metadata pills (`dds__badge`).

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

## Parameters

| Parameter | Type | Default | Description |
|:---|:---|:---|:---|
| `tabs` | `list` | `None` | Sequence of `TabItem` instances, dictionaries, or objects with `id` and `label` (positional). |
| `active_tab` | `str` | `""` | ID of the initially active tab. Defaults to the first tab's `id`. |
| `variant` | `str` | `"default"` | Visual variant (`"default"` for standard tabs, `"switcher"` for uppercase overline switcher). |
| `aria_label` | `str` | `"Tabs"` | Accessible label applied to the `<div role="tablist">` container. |
| `id_prefix` | `str` | `"dds"` | DOM ID prefix for tab triggers (`<id_prefix>-tab-<id>`) and panels (`<id_prefix>-panel-<id>`). |

## Behaviour & Accessibility

- Renders `<dds-tabs class="dds-tabs" data-variant="..." data-active-tab="...">` containing `<div role="tablist" class="l-cluster">`.
- Each trigger renders as `<button type="button" role="tab" id="<id_prefix>-tab-<id>" data-tab-trigger="<id>" aria-selected="..." tabindex="...">`.
- When an inline panel or slotted panel exists, `aria-controls="<id_prefix>-panel-<id>"` is bound to the trigger. When used as a panel-less view switcher, dangling `aria-controls` references are omitted.
- Inline `content` values render as `<div role="tabpanel" id="<id_prefix>-panel-<id>" data-tab-panel="<id>" aria-labelledby="<id_prefix>-tab-<id>">`, with `hidden` set on inactive panels.
- Custom rich panels can be supplied inside the block body.
- `<dds-tabs>` handles click activation and keyboard navigation (`ArrowRight`, `ArrowLeft`, `Home`, `End`), updating roving `tabindex`, `aria-selected`, `panel.hidden`, `data-active-tab`, and dispatching a bubbling `dds:tab-change` `CustomEvent` with `detail: { tabId }`. Nested tab instances are strictly isolated from parent event handling.

## Example Usage

```django
{% load design_components %}

{# Standard tab switcher with inline panels #}
{% dds__tabs tabs active_tab="overview" aria_label="Component views" %}{% enddds__tabs %}

{# Standalone view switcher without panels #}
{% dds__tabs tabs=view_modes active_tab="docs" variant="switcher" aria_label="Documentation and Sandbox view switcher" %}{% enddds__tabs %}

{# Custom slotted panels #}
{% dds__tabs tabs=tab_headers active_tab="preview" %}
  <div role="tabpanel" id="dds-panel-preview" data-tab-panel="preview" aria-labelledby="dds-tab-preview">
    Custom slotted preview content
  </div>
  <div role="tabpanel" id="dds-panel-code" data-tab-panel="code" aria-labelledby="dds-tab-code" hidden>
    <pre><code>Custom code content</code></pre>
  </div>
{% enddds__tabs %}
```
