# Canvas Widget (`dds__canvas_widget`)

The `dds__canvas_widget` domain component renders a `<dds-canvas-widget class="dds-canvas-widget">` Light DOM custom element that hosts an isolated `<iframe>` component preview stage (`[data-canvas-stage]` on `data-surface="stage"`) alongside optional template source (`[data-canvas-panel="code"]`) and rendered HTML (`[data-canvas-panel="html"]`) drawers powered by `{% dds__code_block %}` on `data-surface="code"`.

## When to Use

- Embedding an isolated component preview `<iframe>` (via `iframe_src` or `iframe_srcdoc`) that automatically resizes in response to `window.postMessage` `{ type: 'canvas-resize', id, height }` payloads.
- Providing an interactive mode switcher (`Preview`, `Template`, `HTML`) above a component preview without duplicating code block chrome across views.
- Controlling stage background presets (`white`, `light`, `dark`), viewport width presets (`responsive` or pixel widths like `768`), and zoom levels (`100`, `125`, etc.).

## Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `canvas_id` | `str` | `"canvas"` | Unique identifier for the canvas instance and `postMessage` resize correlation. |
| `iframe_src` | `str` | `""` | URL for the isolated preview iframe (first positional argument). |
| `iframe_srcdoc` | `str` | `""` | Inline HTML document string for `srcdoc` preview embedding. |
| `source_code` | `str` | `""` | Raw or highlighted template source code snippet. |
| `rendered_html` | `str` | `""` | Raw or highlighted rendered HTML output snippet. |
| `mode` | `str` | `"preview"` | Initial active panel mode (`'preview'`, `'code'`, or `'html'`). |
| `viewport` | `str` | `"responsive"` | Initial viewport width preset (`'responsive'` or pixel width string such as `'768'`). |
| `background` | `str` | `"white"` | Initial canvas stage background preset (`'white'`, `'light'`, `'dark'`). |
| `zoom` | `str` | `"100"` | Initial zoom percentage string (e.g. `'100'`). |
| `sandbox_attrs` | `str` | `""` | Optional iframe `sandbox` attribute value. |
| `title` | `str` | `"Component preview"` | Accessible `title` attribute for the preview iframe. |
| `show_toggles` | `bool` | `True` | Whether to render the preview/code/html mode toggle bar when code snippets exist. |

## Custom Element Behaviour (`<dds-canvas-widget>`)

- **Mode Toggling:** Clicking any `[data-canvas-mode]` button updates `data-mode`, toggles `aria-pressed` on the mode buttons, toggles `hidden` on `[data-canvas-stage]`, `[data-canvas-panel='code']`, and `[data-canvas-panel='html']`, and dispatches a bubbling `dds:canvas-mode-change` `CustomEvent` with `detail: { canvasId, mode }`.
- **Iframe Auto-Resize:** Listens for `window` `message` events with `{ type: 'canvas-resize', id?, height }` matching `data-canvas-id` or the iframe's `contentWindow`, clamps `height` to `Math.max(24, Number(data.height))`, updates `iframe.style.height` and `--_canvas-widget-iframe-height`, and dispatches `dds:canvas-resize` with `detail: { canvasId, height }`.
- **Public Methods:** `setViewport(viewport)`, `setBackground(background)`, and `setZoom(zoom)` update the corresponding `data-*` attributes and `--_canvas-widget-viewport-width`.

## Template Usage

```django
{% load design_components %}

{% dds__canvas_widget "/gallery/canvas/?component=dds__button" canvas_id="button-preview" source_code="{% dds__button 'Save' %}" rendered_html="<button class='dds-button'>Save</button>" %}

{% dds__canvas_widget iframe_srcdoc="<button>Inline preview</button>" background="dark" viewport="768" zoom="125" show_toggles=False %}
```
