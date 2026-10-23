# Table (`dds__table`)

A responsive, accessible table primitive for structured tabular data.

## When to Use

- Displaying structured datasets, parameter specifications, or comparison matrices.
- Use `density="default"` for general documentation tables.
- Use `density="compact"` for dense parameter or metadata listings.

## Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `caption` | `str` | `""` | Optional accessible table caption. |
| `density` | `str` | `"default"` | Row padding density (`"default"` or `"compact"`). |

## Slots

| Slot | Required | Description |
| :--- | :--- | :--- |
| `head` | `False` | Table header rows (`<tr>` containing `<th>` cells), rendered inside `<thead>`. |
| `body` | `True` | Table body rows (`<tr>` containing `<td>` or `<th>` cells), rendered inside `<tbody>`. |
| `foot` | `False` | Optional table footer rows (`<tr>` containing `<td>` or `<th>` cells), rendered inside `<tfoot>`. |

## Accessibility

- The responsive outer container enforces `overflow-x: auto`, `tabindex="0"`, and `role="region"` with an `aria-label` matching the caption (or falling back to `"Data table"`). This guarantees keyboard-only users can scroll wide tables horizontally.

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
