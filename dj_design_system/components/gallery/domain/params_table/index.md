# Params Table (`dds__params_table`)

A domain gallery component that renders structured documentation tables for a component's declared parameters and optional named slots.

## When to Use

- Displaying the read-only parameter specification table (`Name`, `Type`, `Requirement`, `Default`, `Choices`, `Description`) in a component's documentation view.
- Documenting named `BlockComponent` slots alongside component parameters.
- Providing a clear empty-state message when a component defines no parameters.

## Parameters

- **`params` (`list`, optional, default `None`, positional):** Component parameter 2-tuples `(name, spec)`, `param_rows` dicts containing `"name"` and `"spec"`, or normalized parameter dicts/objects.
- **`slots_list` (`list`, optional, default `None`):** Optional named slot 2-tuples `(name, slot)` or slot dicts to render in a secondary `Slots` table.
- **`title` (`str`, optional, default `"Parameters"`):** Section heading rendered inside `<h3 data-params-heading>` when non-empty.
- **`empty_message` (`str`, optional, default `"This component has no parameters."`):** Fallback message rendered inside `<p data-params-empty>` when `params` is empty.

## Behaviour & Accessibility

- Renders `<section class="dds-params-table">` wrapping an Every Layout `<l-stack>`.
- Normalises all parameter and slot rows in `get_context()` without using Django template filters (`|default`, `|yesno`, etc.).
- Composes `{% dds__table density="compact" %}` for horizontally scrollable tabular presentation and `{% dds__badge %}` (`code`, `error`, and `neutral` variants) for types, requirement pills, and parameter choices wrapped in `<l-cluster data-param-choices>`.

## Example Usage

```django
{% load design_components %}

{% dds__params_table params %}
{% dds__params_table params=param_rows slots_list=slots title="Parameters" %}
```
