Standard and compact table densities are showcased stacked below.

```canvas
<l-stack gap="var(--dds-space-lg)">
  {% dds__table caption="Standard density" %}
    {% slot head %}
      <tr><th scope="col">Name</th><th scope="col">Role</th></tr>
    {% endslot %}
    {% slot body %}
      <tr><td>Ada Lovelace</td><td>Computing Pioneer</td></tr>
      <tr><td>Alan Turing</td><td>Mathematician</td></tr>
    {% endslot %}
  {% enddds__table %}

  {% dds__table caption="Compact density" density="compact" %}
    {% slot head %}
      <tr><th scope="col">Token</th><th scope="col">Value</th></tr>
    {% endslot %}
    {% slot body %}
      <tr><td>--dds-space-xs</td><td>0.25rem</td></tr>
      <tr><td>--dds-space-sm</td><td>0.5rem</td></tr>
    {% endslot %}
  {% enddds__table %}
</l-stack>
```

## Accessibility

- The responsive outer container enforces `overflow-x: auto`, `tabindex="0"`, and `role="region"` with an `aria-label` matching the caption (or falling back to `"Data table"`). This guarantees keyboard-only users can scroll wide tables horizontally.

