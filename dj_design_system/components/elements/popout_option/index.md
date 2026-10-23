# Popout Option (`dds__popout_option`)

The `dds__popout_option` component renders an individual selectable option (`<button role="menuitemradio">`) or navigation item (`<a role="menuitem">`) inside a `dds__popout` menu.

## When to Use

- Rendering selectable radio-style options (`selected=True`/`False`) inside a `{% dds__popout %}` menu.
- Rendering navigation links (`href="..."`) inside a breadcrumb flyout or action menu.
- Disabling unavailable options (`disabled=True`), which automatically suppresses `href` link rendering.

## Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `label` | `str` | Required | Visible option text label (positional argument 1). |
| `value` | `str` | `""` | Option value payload; falls back to `label` when empty. |
| `icon` | `str` | `""` | Optional leading icon name from `ICON_NAMES`. |
| `selected` | `bool` | `False` | Sets `aria-checked="true"` when selected. |
| `disabled` | `bool` | `False` | Disables the option and forces `<button disabled>`. |
| `href` | `str` | `""` | Optional URL; renders `<a role="menuitem">` when not disabled. |

## Template Usage

```django
{% load design_components %}

{% dds__popout "Theme" icon="sun" %}
  {% dds__popout_option "Light" value="light" icon="sun" selected=True %}
  {% dds__popout_option "Dark" value="dark" icon="moon" %}
  {% dds__popout_option "Docs" href="/docs/" icon="external-link" %}
{% enddds__popout %}
```
