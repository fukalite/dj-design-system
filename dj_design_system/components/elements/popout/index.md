# Popout (`dds__popout`)

The `dds__popout` block component renders a `<dds-popout class="dds-popout">` Light DOM custom element pairing an accessible trigger button (`[data-popout-trigger]`) with a floating menu (`[data-popout-menu]` on `data-surface="popout"`).

## When to Use

- Dropdown selectors (e.g. theme switcher, viewport width presets) containing `{% dds__popout_option %}` items.
- Compact overflow menus or breadcrumb flyout navigation menus.
- Custom trigger buttons supplied via the optional `{% slot "trigger" %}` slot.

## Parameters & Slots

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `label` | `str` | `""` | Trigger button label (positional argument 1). |
| `icon` | `str` | `""` | Optional leading trigger icon name from `ICON_NAMES`. |
| `icon_only` | `bool` | `False` | Renders an icon-only trigger button with `aria-label`. |
| `align` | `str` | `"start"` | Horizontal menu alignment (`"start"` or `"end"`). |
| `open` | `bool` | `False` | Whether the floating menu is initially open. |
| `menu_label` | `str` | `""` | Accessible `aria-label` for the menu; falls back to `label`. |

| Slot | Required | Description |
| :--- | :--- | :--- |
| `trigger` | `False` | Optional custom trigger markup; when omitted, renders a default trigger button. |

## Client-Side Behaviour (`<dds-popout>`)

- Clicking `[data-popout-trigger]` toggles `data-state` (`"open"` / `"closed"`), `aria-expanded`, and `menu.hidden`.
- Pressing `Escape` or clicking outside `<dds-popout>` closes the menu.
- Clicking an enabled `[data-popout-option]` updates `aria-checked`, dispatches a bubbling `dds:popout-select` `CustomEvent` with `detail: { value }`, and closes the menu.

## Template Usage

```django
{% load design_components %}

{% dds__popout "Theme" icon="sun" align="end" menu_label="Choose theme" %}
  {% dds__popout_option "Light" value="light" icon="sun" selected=True %}
  {% dds__popout_option "Dark" value="dark" icon="moon" %}
{% enddds__popout %}
```
