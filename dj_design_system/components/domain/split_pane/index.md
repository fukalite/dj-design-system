# Split Pane (`dds__split_pane`)

The `dds__split_pane` domain component renders a resizable dual-pane container (`<dds-split-pane class="dds-split-pane">`) separated by an accessible WAI-ARIA `role="separator"` handle (`[data-split-resizer]`). It supports horizontal (side-by-side) and vertical (stacked) orientations, clamped percentage ratios (`10`–`90`), optional pane header bars (`[data-split-pane-header]`), and surface token scopes (`data-surface`) on each pane.

## When to Use

- Dividing the interactive sandbox into a primary preview viewport and a secondary parameter/controls pane.
- Providing pointer-drag and keyboard-accessible pane resizing with automatic ratio clamping.
- Pairing distinct named surfaces (such as `docs`, `sandbox`, `stage`, or `code`) side-by-side or stacked.

## Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `orientation` | `str` | `"horizontal"` | Split orientation (`"horizontal"` for side-by-side or `"vertical"` for stacked). |
| `initial_ratio` | `int` | `50` | Initial primary pane percentage (clamped between `min_ratio` and `max_ratio`). |
| `min_ratio` | `int` | `20` | Minimum primary pane percentage (clamped to `10`–`90`). |
| `max_ratio` | `int` | `80` | Maximum primary pane percentage (clamped to `min_ratio`–`90`). |
| `primary_surface` | `str` | `"docs"` | Optional `data-surface` attribute for the primary pane (`""` omits the attribute). |
| `secondary_surface` | `str` | `"sandbox"` | Optional `data-surface` attribute for the secondary pane (`""` omits the attribute). |
| `primary_label` | `str` | `""` | Optional header label for the primary pane (`[data-split-pane-header]`). |
| `secondary_label` | `str` | `""` | Optional header label for the secondary pane (`[data-split-pane-header]`). |
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

{% dds__split_pane orientation="horizontal" initial_ratio=65 primary_label="Preview" secondary_label="Controls" %}
  {% slot "primary" %}
    <p>Primary preview pane content.</p>
  {% endslot %}
  {% slot "secondary" %}
    <p>Secondary controls pane content.</p>
  {% endslot %}
{% enddds__split_pane %}
```
