## Client-Side Custom Element (`<dds-split-pane>`)

The `{% dds__split_pane %}` component renders an accessible resizable split-view container supporting `primary` and `secondary` pane slots.

- **Parameters:** `orientation` (`horizontal` / `vertical`), `initial_ratio`, `min_ratio`, `max_ratio`, and `resizer_label`.

- **Pointer Resizing:** Dragging `[data-split-resizer]` updates `--_split-pane-ratio` and `aria-valuenow` within `[data-min-ratio, data-max-ratio]` and sets `data-dragging="true"` while active.
- **Keyboard Resizing:** Pressing arrow keys (`ArrowLeft`/`ArrowRight` in horizontal mode, `ArrowUp`/`ArrowDown` in vertical mode), `Home` (minimum ratio), or `End` (maximum ratio) on `[data-split-resizer]` adjusts the split ratio and dispatches a bubbling `dds:split-resize` `CustomEvent` (`detail: { ratio, orientation }`).
