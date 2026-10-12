All status notice variants and alert modes are showcased stacked below.

```canvas
<l-stack gap="var(--dds-space-md)">
  {% dds__notice variant="info" title="Information" %}Component changes are reflected automatically in the preview canvas.{% enddds__notice %}
  {% dds__notice variant="success" title="Configuration Valid" %}All discovered components passed parameter and template validation.{% enddds__notice %}
  {% dds__notice variant="warning" title="Deprecated Parameter" %}Support for legacy CSS class parameters will be removed in a future release.{% enddds__notice %}
  {% dds__notice variant="error" title="Rendering Failed" %}Required slot content was omitted when invoking the block component.{% enddds__notice %}
</l-stack>
```

## Accessibility

- `info` and `success` variants render with `role="note"`.
- `warning` and `error` variants automatically upgrade to `role="alert"` so assistive technologies announce urgent messages.
- Use `role="note"` to override static or passive warnings that should not act as interrupting live regions.
- The leading status icon is decorative (`aria-hidden="true"`) because the notice heading and prose convey the message semantics.

