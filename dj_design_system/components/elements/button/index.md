# Button (`dds__button`)

The `dds__button` primitive renders an interactive `<button class="dds-button">` control or a polymorphic `<a class="dds-button">` link when `href` is provided and `disabled` is `False`.

## When to Use

- Triggering actions, form submissions, toolbar toggles (`pressed`), and declarative parent Web Component hooks (`action`).
- Navigating to internal or external URLs with button styling (`href` and `target`).
- Rendering compact icon-only controls (`icon_only=True`) with mandatory `aria-label` accessibility.

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
