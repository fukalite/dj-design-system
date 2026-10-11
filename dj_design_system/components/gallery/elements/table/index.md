# Table (`dds__table`)

A responsive, accessible table primitive for structured tabular data.

## When to Use

- Displaying structured datasets, parameter specifications, or comparison matrices.
- Use `density="default"` for general documentation tables.
- Use `density="compact"` for dense parameter or metadata listings.

## Slots

- **`head` (optional):** Table header rows (`<tr>` containing `<th>` cells), rendered inside `<thead>`.
- **`body` (required):** Table body rows (`<tr>` containing `<td>` cells), rendered inside `<tbody>`.

## Example Usage

```django
{% load design_components %}

{% dds__table caption="Component parameters" density="compact" %}
  {% slot "head" %}
    <tr>
      <th scope="col">Name</th>
      <th scope="col">Type</th>
    </tr>
  {% endslot %}
  {% slot "body" %}
    <tr>
      <td>caption</td>
      <td>str</td>
    </tr>
  {% endslot %}
{% enddds__table %}
```
