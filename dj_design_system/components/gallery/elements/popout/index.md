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
| `icon` | `str` | `""` | Optional leading trigger icon name. |
| `icon_only` | `bool` | `False` | Renders an icon-only trigger button with `aria-label`. |
| `align` | `str` | `"start"` | Horizontal menu alignment (`"start"` or `"end"`). |
| `open` | `bool` | `False` | Whether the floating menu is initially open. |
| `role` | `str` | `"menu"` | ARIA role for the floating pane (`"menu"`, `"dialog"`, `"region"`, or `"none"`). |
| `menu_label` | `str` | `""` | Accessible `aria-label` for the menu; falls back to `label`. |

| Slot | Required | Description |
| :--- | :--- | :--- |
| `trigger` | `False` | Optional custom trigger markup (e.g. `<dds__button data-popout-trigger>`); when omitted, renders a default `.dds-popout-trigger` button. Slotted triggers preserve their own styling completely. |
| `menu` | `False` | Optional floating menu content markup. |

## Client-Side Behaviour (`<dds-popout>`)

- Clicking `[data-popout-trigger]` toggles `data-state` (`"open"` / `"closed"`), `aria-expanded`, and `menu.hidden`.
- Pressing `Escape` or clicking outside `<dds-popout>` closes the menu and returns focus to the active trigger element.
- Clicking an enabled `[data-popout-option]` dispatches a bubbling `dds:popout-select` `CustomEvent` with `detail: { value }` and closes the menu.
- If the clicked option has `role="menuitemradio"`, radio group selection is updated. If `role="menuitemcheckbox"`, checked state toggles. Links and standard action `role="menuitem"` elements do not receive `aria-checked`.

## Template Usage

```django
{% load design_components %}

{% dds__popout "Theme" icon="sun" align="end" menu_label="Choose theme" %}
  {% slot "menu" %}
    {% dds__popout_option "Light" value="light" icon="sun" selected=True %}
    {% dds__popout_option "Dark" value="dark" icon="moon" %}
  {% endslot %}
{% enddds__popout %}
```
