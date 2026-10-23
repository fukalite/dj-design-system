# Toolbar (`dds__toolbar`)

The `dds__toolbar` domain component renders the top gallery header bar (`<header class="dds-toolbar" data-surface="topbar">`). It uses Every Layout `<l-cluster>` primitives to align leading navigation controls (mobile drawer toggle, brand link, and breadcrumb trail) alongside trailing utility actions (instant search box, theme selector, and custom action slots).

## When to Use

- Rendering the primary topbar in `dds__gallery_shell` or standalone documentation pages.
- Composing `dds__button`, `dds__breadcrumb`, `dds__search_box`, and `dds__theme_select` into a single elevated `topbar` surface with optional `leading` and `actions` slots.

## Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `brand_name` | `str` | `"Design System"` | Design system brand title displayed in the `[data-toolbar-brand]` link. |
| `brand_url` | `str` | `"/"` | URL for the brand link. |
| `breadcrumbs` | `list` | `None` | Breadcrumb trail items delegated to `{% dds__breadcrumb %}` when the `leading` slot is omitted. |
| `themes` | `list` | `None` | Available themes delegated to `{% dds__theme_select %}` when non-empty. |
| `active_theme` | `str` | `"light"` | Active theme identifier passed to `{% dds__theme_select %}`. |
| `search_index` | `list` | `None` | Search index entries delegated to `{% dds__search_box %}`. |
| `show_search` | `bool` | `True` | Whether to render `{% dds__search_box %}` in the trailing actions cluster. |
| `show_menu_toggle` | `bool` | `True` | Whether to render the mobile navigation drawer toggle button (`action="toggle-drawer"`). |

## Slots

| Slot | Required | Description |
| :--- | :--- | :--- |
| `leading` | `False` | Optional custom leading/breadcrumb markup inside `[data-toolbar-breadcrumb]` (overrides `breadcrumbs`). |
| `actions` | `False` | Optional extra toolbar action controls appended inside `[data-toolbar-actions]`. |

## Template Usage

```django
{% load design_components %}

{% dds__toolbar brand_name="Design System" breadcrumbs=breadcrumbs themes=themes active_theme=active_theme search_index=search_index %}{% enddds__toolbar %}

{% dds__toolbar brand_name="Component Docs" show_search=False %}
  {% slot "leading" %}
    <span>v2.0</span>
  {% endslot %}
  {% slot "actions" %}
    {% dds__button "GitHub" variant="ghost" size="sm" href="https://example.com" %}
  {% endslot %}
{% enddds__toolbar %}
```
