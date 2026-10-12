## Accessibility

- The responsive outer container enforces `overflow-x: auto`, `tabindex="0"`, and `role="region"` with an `aria-label` matching the caption (or falling back to `"Data table"`). This guarantees keyboard-only users can scroll wide tables horizontally.
