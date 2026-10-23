The ``dds__tooltip`` component is an accessible, lightweight floating label that describes an interactive element on hover and keyboard focus.

## Placements

```canvas
<l-cluster gap="var(--dds-space-2xl)" justify="center">
  {% dds__tooltip text="Top tooltip" placement="top" %}
    <button type="button" class="dds-button" data-variant="neutral" data-size="sm">
      <span>Top</span>
    </button>
  {% enddds__tooltip %}

  {% dds__tooltip text="Bottom tooltip" placement="bottom" %}
    <button type="button" class="dds-button" data-variant="neutral" data-size="sm">
      <span>Bottom</span>
    </button>
  {% enddds__tooltip %}

  {% dds__tooltip text="Left tooltip" placement="left" %}
    <button type="button" class="dds-button" data-variant="neutral" data-size="sm">
      <span>Left</span>
    </button>
  {% enddds__tooltip %}

  {% dds__tooltip text="Right tooltip" placement="right" %}
    <button type="button" class="dds-button" data-variant="neutral" data-size="sm">
      <span>Right</span>
    </button>
  {% enddds__tooltip %}

  {% dds__tooltip text="End aligned tooltip" placement="bottom" align="end" %}
    <button type="button" class="dds-button" data-variant="neutral" data-size="sm">
      <span>End Aligned</span>
    </button>
  {% enddds__tooltip %}
</l-cluster>
```

## Client-Side Behaviour (`<dds-tooltip>`)

- **Hover & Focus Triggering**: Moving pointer over `<dds-tooltip>` or focusing the child trigger element reveals the tooltip bubble.
- **WCAG 2.1 SC 1.4.13 Compliance**:
  - *Dismissible*: Pressing `Escape` immediately dismisses the tooltip without changing focus.
  - *Hoverable*: The pointer can safely traverse between the trigger and the bubble without closing the bubble.
  - *Persistent*: Tooltip remains visible until the pointer leaves, focus moves away, or `Escape` is pressed.
- **ARIA Wiring**: Automatically injects a generated or explicit ID into the bubble and links the interactive trigger via `aria-describedby`.
- **Open Menu Suppression**: If the trigger element opens a menu or popout (`[data-state="open"]` or `aria-expanded="true"`), the tooltip is automatically concealed.

## Rich Content Slot

```django
{% dds__tooltip placement="bottom" %}
  <button type="button" class="dds-button" data-variant="neutral" data-size="sm">
    <span>Rich Hint</span>
  </button>
  {% slot "tip" %}
    <span>Open <strong>canvas view</strong> in a new browser tab</span>
  {% endslot %}
{% enddds__tooltip %}
```
