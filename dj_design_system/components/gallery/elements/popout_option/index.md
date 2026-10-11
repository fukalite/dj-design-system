# Popout Option (`dds__popout_option`)

The `dds__popout_option` component renders an individual selectable option (`<button role="menuitemradio">`), action item (`<button role="menuitem">`), or navigation item (`<a role="menuitem">`) inside a `dds__popout` menu.

## When to Use

- Rendering selectable radio-style options (`selected=True`/`False`) inside a `{% dds__popout %}` menu.
- Rendering action items (`role="menuitem"`) inside an action or overflow menu.
- Rendering navigation links (`href="..."`) inside a breadcrumb flyout or navigation menu.
- Disabling unavailable options (`disabled=True`), which marks links as `aria-disabled="true"` or disables buttons.

## Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `label` | `str` | Required | Visible option text label (positional argument 1). |
| `value` | `str` | `""` | Option value payload; falls back to `label` when empty. |
| `role` | `str` | `""` | ARIA menu item role (`"menuitem"`, `"menuitemradio"`, or `"menuitemcheckbox"`). Defaults to `"menuitem"` for links and `"menuitemradio"` for buttons. |
| `icon` | `str` | `""` | Optional leading icon name. |
| `shortcut` | `str` | `""` | Optional keyboard shortcut hint (e.g. `"⌘K"`). |
| `selected` | `bool` | `False` | Sets `aria-checked="true"` when selected on checkable options. |
| `disabled` | `bool` | `False` | Disables the option (`aria-disabled="true"` on links, `disabled` on buttons). |
| `href` | `str` | `""` | Optional destination URL; renders an `<a>` element. |

## Template Usage

```django
{% load design_components %}

{% dds__popout "Theme" icon="sun" %}
  {% dds__popout_option "Light" value="light" icon="sun" selected=True %}
  {% dds__popout_option "Dark" value="dark" icon="moon" %}
  {% dds__popout_option "Docs" href="/docs/" icon="external-link" %}
{% enddds__popout %}
```
