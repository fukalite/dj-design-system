# Sandbox Toolbar (`dds__sandbox_toolbar`)

The `dds__sandbox_toolbar` domain component renders an accessible `<dds-sandbox-toolbar class="dds-sandbox-toolbar" data-surface="sandbox" role="toolbar">` Light DOM custom element control bar for interactive component sandboxes and canvas previews. It composes Every Layout `<l-cluster>`, `{% dds__popout %}`, `{% dds__popout_option %}`, and `{% dds__button %}` primitives, persists toolbar state to `sessionStorage` (`dds_toolbar_state`), and dispatches bubbling `dds:sandbox-bg`, `dds:sandbox-viewport`, `dds:sandbox-zoom`, `dds:sandbox-toggle`, and `dds:sandbox-reset` events.

## When to Use

- Providing interactive viewport width presets, canvas background switching, zoom controls, and variant preset selection above a sandbox preview stage.
- Exposing box model outline (`action="toggle-outline"`), measurement overlay (`action="toggle-measure"`), and RTL direction (`action="toggle-rtl"`) toggles alongside optional parameter reset and standalone canvas links.

## Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `variants` | `list` | `None` | Optional list of `Variant` instances or dicts with `'name'` and `'label'`. |
| `active_variant` | `str` | `""` | Currently active variant name or `Variant` instance. |
| `component_url` | `str` | `""` | Base component URL used to build variant switching links. |
| `backgrounds` | `list` | `None` | Available canvas background dicts or `(value, label)` pairs; defaults to White, Light, and Dark. |
| `active_background` | `str` | `"white"` | Currently active background identifier. |
| `viewports` | `list` | `None` | Optional viewport preset dicts or `(value, label)` pairs; defaults to Responsive through 2560px. |
| `active_viewport` | `str` | `"responsive"` | Currently active viewport preset value. |
| `zoom_levels` | `list` | `None` | Optional zoom percentage presets; defaults to `50` through `200`. |
| `active_zoom` | `str` | `"100"` | Currently active zoom level percentage. |
| `outline_active` | `bool` | `False` | Whether the box model outline toggle is initially pressed. |
| `measure_active` | `bool` | `False` | Whether the measurement overlay toggle is initially pressed. |
| `rtl_active` | `bool` | `False` | Whether the right-to-left direction toggle is initially pressed. |
| `canvas_url` | `str` | `""` | Optional standalone canvas URL rendered as a new-tab action link. |
| `reset_url` | `str` | `""` | Optional URL rendered as a parameter reset action control. |
| `aria_label` | `str` | `"Sandbox controls"` | Accessible `aria-label` for the `role="toolbar"` container. |

## Template Usage

```django
{% load design_components %}

{% dds__sandbox_toolbar %}

{% dds__sandbox_toolbar variants=variants active_variant="primary" component_url="/gallery/button/" active_background="dark" active_viewport="768" outline_active=True reset_url="/gallery/button/" canvas_url="/canvas/button/" %}
```
