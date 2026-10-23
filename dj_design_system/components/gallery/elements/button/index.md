All primary action colours and visual emphasis states are showcased side by side below.

```canvas
<l-cluster gap="var(--dds-space-sm)" align="center">
  {% dds__button label="Default Button" %}
  {% dds__button label="Primary Action" variant="primary" %}
  {% dds__button label="Ghost Action" variant="ghost" %}
  {% dds__button label="Danger Action" variant="danger" %}
</l-cluster>
```

## Accessibility

- Native `<button>` elements automatically inherit keyboard activation via `Enter` and `Space`.
- When rendered as a link (`href` provided), the component emits an `<a>` element with appropriate `rel` and `target` attributes.
- Icon-only buttons require an accessible `label` to ensure screen readers announce the action properly.
