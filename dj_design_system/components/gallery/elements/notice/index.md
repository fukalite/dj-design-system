## Accessibility

- `info` and `success` variants render with `role="note"`.
- `warning` and `error` variants automatically upgrade to `role="alert"` so assistive technologies announce urgent messages.
- Use `role="note"` to override static or passive warnings that should not act as interrupting live regions.
- The leading status icon is decorative (`aria-hidden="true"`) because the notice heading and prose convey the message semantics.
