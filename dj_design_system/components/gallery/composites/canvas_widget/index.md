## Custom Element Behaviour (`<dds-canvas-widget>`)

- **Mode Toggling:** Clicking any `[data-canvas-mode]` button updates `data-mode`, toggles `aria-pressed` on the mode buttons, toggles `hidden` on `[data-canvas-stage]`, `[data-canvas-panel='code']`, and `[data-canvas-panel='html']`, and dispatches a bubbling `dds:canvas-mode-change` `CustomEvent` with `detail: { canvasId, mode }`.
- **Iframe Auto-Resize:** Listens for `window` `message` events with `{ type: 'canvas-resize', id?, height }` matching `data-canvas-id` or the iframe's `contentWindow`, clamps `height` to `Math.max(24, Number(data.height))`, updates `iframe.style.height` and `--_canvas-widget-iframe-height`, and dispatches `dds:canvas-resize` with `detail: { canvasId, height }`.
- **Public Methods:** `setViewport(viewport)`, `setBackground(background)`, and `setZoom(zoom)` update the corresponding `data-*` attributes and `--_canvas-widget-viewport-width`.
