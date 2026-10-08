# Params Form (`dds__params_form`)

A domain gallery component that renders the interactive parameter editing form inside the component sandbox drawer.

## When to Use

- Rendering editable form controls for a component's declared parameters and slots inside the live sandbox pane.
- Triggering debounced HTMX sandbox updates while preserving active gallery state (`_iss`, `_dds_theme`, and `_dds_variant`).
- Displaying a clear empty-state message when a component has no configurable parameters.

## Parameters

- **`param_rows` (`list`, optional, default `None`, positional):** Parameter row dictionaries or objects containing `name`, `spec`, and `field` entries.
- **`action_url` (`str`, optional, default `""`):** Form GET `action` and `hx-get` URL.
- **`active_theme` (`str`, optional, default `""`):** Active theme identifier preserved as a hidden `_dds_theme` input when non-empty.
- **`active_variant` (`str`, optional, default `""`):** Active variant name (or `Variant` instance) preserved as a hidden `_dds_variant` input when non-empty.
- **`hx_target` (`str`, optional, default `"closest [data-gallery-sandbox-body]"`):** HTMX target selector for live sandbox swaps.
- **`empty_message` (`str`, optional, default `"This component has no configurable parameters."`):** Fallback message rendered inside `<p data-params-empty>` when `param_rows` is empty.

## Behaviour & Accessibility

- Renders `<dds-params-form class="dds-params-form" data-surface="sandbox">`.
- Normalises parameter rows in `get_context()` without using Django template filters (`|default`, `|safe`, etc.).
- Wraps fields in an Every Layout `<l-stack data-params-fields>` and delegates each field's label, required indicator, helper description, error alert, and control slot to `{% dds__form_field %}`.

## Example Usage

```django
{% load design_components %}

{% dds__params_form param_rows action_url=request.path active_theme=active_theme active_variant=active_variant %}
```
