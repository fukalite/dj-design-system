# Theme Select (`dds__theme_select`)

The `dds__theme_select` domain component renders an accessible theme selector control inside a `<dds-theme-select>` Light DOM custom element. It displays a contextual `sun` or `moon` icon alongside a native `<select data-theme-select>` dropdown for switching gallery or canvas themes.

## When to Use

- Allowing users to switch the active gallery shell theme in the topbar (`dds__toolbar`) or preview theme in the sandbox toolbar.
- Presenting a list of `Theme` dataclass objects, `{ "value", "label" }` dictionaries, or theme identifier strings with automatic icon resolution (`moon` when `"dark"` is in the theme identifier, `sun` otherwise).

## Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `themes` | `list` | `None` | Available theme objects, dicts with `'value'` and `'label'`, or plain string identifiers (positional argument 0). |
| `active_theme` | `str` | `"light"` | Currently active theme identifier; falls back to the first available theme if not matched. |
| `label` | `str` | `"Global Theme"` | Accessible `aria-label` and `title` for the `<select>` control. |
| `select_id` | `str` | `"gallery-global-theme-select"` | DOM `id` attribute for the `<select>` element. |

## Client-Side Behaviour (`<dds-theme-select>`)

- Queries `[data-theme-select]` strictly within its own Light DOM subtree.
- Updates `data-active-theme` on `<dds-theme-select>`, persists the selected theme, and dispatches a bubbling `dds:theme-change` `CustomEvent` when the selection changes.

## Template Usage

```django
{% load design_components %}

{% dds__theme_select themes %}

{% dds__theme_select themes=gallery_themes active_theme="dark" label="Global Theme" %}
```
