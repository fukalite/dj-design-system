# Button (`dds__button`)

The `dds__button` primitive renders an interactive `<button class="dds-button">` control or a polymorphic `<a class="dds-button">` link when `href` is provided and `disabled` is `False`.

## When to Use

- Triggering actions, form submissions, toolbar toggles (`pressed`), and declarative parent Web Component hooks (`action`).
- Navigating to internal or external URLs with button styling (`href` and `target`).
- Rendering compact icon-only controls (`icon_only=True`) with mandatory `aria-label` accessibility.

## Parameters

| Parameter | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `label` | `str` | No | `""` | Button text label (or accessible `aria-label` when `icon_only=True`). Positional argument 1. |
| `variant` | `str` | No | `"default"` | Visual style: `"default"`, `"primary"`, `"ghost"`, `"danger"`. |
| `size` | `str` | No | `"md"` | Size step: `"sm"`, `"md"`, `"lg"`. |
| `icon` | `str` | No | `""` | Optional leading or standalone icon name from built-in gallery icon set. |
| `icon_trailing` | `str` | No | `""` | Optional trailing icon name from built-in gallery icon set. |
| `icon_only` | `bool` | No | `False` | Render only the icon and use `label` as accessible `aria-label`. |
| `href` | `str` | No | `""` | Optional URL; renders an `<a>` element when provided and not disabled. |
| `target` | `str` | No | `""` | Optional link target attribute (e.g. `"_blank"`). |
| `button_type` | `str` | No | `"button"` | HTML button type attribute: `"button"`, `"submit"`, `"reset"`. |
| `name` | `str` | No | `""` | Form submission name attribute. |
| `value` | `str` | No | `""` | Form submission value attribute. |
| `disabled` | `bool` | No | `False` | Whether interaction is disabled. |
| `pressed` | `bool` | No | `None` | Optional toggle state for `aria-pressed` (`"true"`/`"false"`). |
| `action` | `str` | No | `""` | Optional `data-action` hook for parent Web Component event delegation. |

## Variants & Sizes

| Variant | Purpose |
| :--- | :--- |
| `default` | Standard bordered control surface button. |
| `primary` | High-emphasis action button using selected state tokens. |
| `ghost` | Low-emphasis borderless button for toolbars and dense UI headers. |
| `danger` | Destructive or reset action button using error status tokens. |

| Size | Icon Size |
| :--- | :--- |
| `sm` | `sm` |
| `md` | `md` (default) |
| `lg` | `md` |

## Template Usage

```django
{% load design_components %}

{% dds__button "Save changes" variant="primary" %}
{% dds__button "Copy" variant="ghost" size="sm" icon="copy" action="copy" %}
{% dds__button "Close drawer" variant="ghost" icon="close" icon_only=True %}
{% dds__button "Open standalone" href="/canvas/" target="_blank" icon_trailing="external-link" %}
```
