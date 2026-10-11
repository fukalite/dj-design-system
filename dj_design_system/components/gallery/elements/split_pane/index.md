# Split Pane (`dds__split_pane`)

The `dds__split_pane` element component renders a resizable dual-pane container (`<dds-split-pane class="dds-split-pane">`) separated by an accessible WAI-ARIA `role="separator"` handle (`[data-split-resizer]`). It supports horizontal (side-by-side) and vertical (stacked) orientations, clamped percentage ratios (`10`–`90`), and unopinionated slotted pane content.

## When to Use

- Dividing a view into resizable dual panes (e.g. documentation alongside an interactive preview).
- Providing pointer-drag and keyboard-accessible pane resizing with automatic ratio clamping.
- Composing distinct custom layouts, toolbars, or surface tokens independently within each pane slot.

## Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `orientation` | `str` | `"horizontal"` | Split orientation (`"horizontal"` for side-by-side or `"vertical"` for stacked). |
| `initial_ratio` | `int` | `50` | Initial primary pane percentage (clamped between `min_ratio` and `max_ratio`). |
| `min_ratio` | `int` | `20` | Minimum primary pane percentage (clamped to `10`–`90`). |
| `max_ratio` | `int` | `80` | Maximum primary pane percentage (clamped to `min_ratio`–`90`). |
| `resizer_label` | `str` | `"Resize panes"` | Accessible `aria-label` on the `[data-split-resizer]` separator handle. |

## Slots

| Slot | Required | Description |
| :--- | :--- | :--- |
| `primary` | `False` | Primary (leading/top) pane content inside `[data-split-pane="primary"]` (falls back to block `content` when instantiated in Python). |
| `secondary` | `False` | Secondary (trailing/bottom) pane content inside `[data-split-pane="secondary"]`. |

## Client-Side Custom Element (`<dds-split-pane>`)

- **Pointer Resizing:** Dragging `[data-split-resizer]` updates `--_split-pane-ratio` and `aria-valuenow` within `[data-min-ratio, data-max-ratio]` and sets `data-dragging="true"` while active.
- **Keyboard Resizing:** Pressing arrow keys (`ArrowLeft`/`ArrowRight` in horizontal mode, `ArrowUp`/`ArrowDown` in vertical mode), `Home` (minimum ratio), or `End` (maximum ratio) on `[data-split-resizer]` adjusts the split ratio and dispatches a bubbling `dds:split-resize` `CustomEvent` (`detail: { ratio, orientation }`).

## Template Usage

```django
{% load design_components %}

{% dds__split_pane orientation="horizontal" initial_ratio=65 %}
  {% slot "primary" %}
    <p>Primary preview pane content.</p>
  {% endslot %}
  {% slot "secondary" %}
    <p>Secondary controls pane content.</p>
  {% endslot %}
{% enddds__split_pane %}
```
