# Sandbox Canvas Area

- **Template Path**: `dj_design_system/components/gallery/composites/canvas_widget/canvas_widget.html`
- **Surface**: `data-surface="stage"` (preview viewport) & `data-surface="code"` (inspectors)
- **Parent Layout**: Positioned as the central preview stage inside `panes/sandbox.html`.

The Sandbox Canvas area hosts the sandboxed iframe stage for rendering components in complete style isolation. It features automatic height synchronization via `postMessage` alongside switchable drawer tabs to inspect the Django template invocation syntax and rendered HTML output.

```canvas
<div style="border: 2px dashed #4338ca; background: rgba(67, 56, 202, 0.04); border-radius: 8px; padding: 14px;">
  <div style="font-family: monospace; font-size: 11px; font-weight: 700; color: #3730a3; text-transform: uppercase; margin-bottom: 8px;">
    &lt;dds-canvas-widget&gt;
  </div>

  <div style="border: 2px dashed #6366f1; background: #ffffff; border-radius: 6px; padding: 12px;">
    <!-- Mode Toggles -->
    <div style="border: 1px dashed #94a3b8; background: #f8fafc; border-radius: 4px; padding: 8px; margin-bottom: 10px;">
      <div style="font-family: monospace; font-size: 10px; font-weight: 700; color: #475569; margin-bottom: 6px;">
        &lt;l-cluster&gt;
      </div>
      <l-cluster style="gap: 6px;">
        <span style="background: #4338ca; color: #ffffff; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;">[👁 Preview Active]</span>
        <span style="background: #e2e8f0; color: #475569; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;">[Template Source]</span>
        <span style="background: #e2e8f0; color: #475569; padding: 4px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;">[Output HTML]</span>
      </l-cluster>
    </div>

    <!-- Isolated Stage Viewport -->
    <div style="background: #1e1b4b; color: #e0e7ff; padding: 24px 16px; border-radius: 6px; text-align: center; border: 1px solid #4338ca;">
      <div style="font-weight: 700; font-size: 12px; color: #a5b4fc;">
        data-surface="stage"
      </div>
      <div style="font-size: 11px; color: #c7d2fe; margin-top: 4px;">
        &lt;iframe data-canvas-iframe src="/gallery/canvas/..."&gt;
      </div>
    </div>
  </div>
</div>
```

### Overriding

Include the canvas widget directly or customize its initial viewport mode and background:

```django
{% dds__canvas_widget canvas_id="sandbox" iframe_src=canvas_iframe_url source_code=source_html rendered_html=rendered_output_html background=active_bg_value title="Component preview" %}
```
