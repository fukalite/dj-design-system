## Client-Side Behaviour (`<dds-sandbox-toolbar>`)

The `{% dds__sandbox_toolbar %}` component renders an accessible toolbar for controlling the sandbox preview canvas.

- **Viewport Resizing**: Dispatches `dds:canvas-resize` custom events with preset widths (Mobile: 375px, Tablet: 768px, Desktop: 100%, Responsive: dynamic).
- **Background Toggling**: Updates active canvas background preset between light, dark, and transparent checkerboard.
- **Ruler & Inspection**: Toggles CSS bounding box overlays, ruler guides, and RTL text direction in the canvas stage.
