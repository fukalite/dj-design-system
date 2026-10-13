# Sandbox Canvas Area

- **Template Path**: `dj_design_system/components/gallery/composites/canvas_widget/canvas_widget.html`
- **Surface**: `data-surface="stage"` (preview viewport) & `data-surface="code"` (inspectors)
- **Parent Layout**: Positioned as the central preview stage inside `panes/sandbox.html`.

The Sandbox Canvas area hosts the sandboxed iframe stage for rendering components in complete style isolation. It features automatic height synchronization via `postMessage` alongside switchable drawer tabs to inspect the Django template invocation syntax and rendered HTML output.

```canvas
<div style="border: 2px dashed var(--dds-control-accent-color); background: var(--dds-state-hover-bg-color); border-radius: var(--dds-radius-md); padding: var(--dds-space-md);">
  <div style="font-family: var(--dds-text-code-font); font-size: 11px; font-weight: 700; color: var(--dds-control-accent-color); text-transform: uppercase; margin-bottom: 8px;">
    &lt;dds-canvas-widget&gt;
  </div>

  <div style="border: 1px solid var(--dds-control-border-color); background: var(--dds-surface-bg-color); border-radius: var(--dds-control-border-radius); padding: 12px;">
    <!-- Mode Toggles -->
    <div style="border: 1px dashed var(--dds-control-border-color); background: var(--dds-state-hover-bg-color); border-radius: var(--dds-control-border-radius); padding: 8px; margin-bottom: 10px;">
      <div style="font-family: var(--dds-text-code-font); font-size: 10px; font-weight: 700; color: var(--dds-text-muted-color); margin-bottom: 6px;">
        &lt;l-cluster&gt;
      </div>
      <l-cluster style="gap: 6px;">
        <span style="background: var(--dds-control-accent-color); color: var(--dds-text-on-accent-color, #ffffff); padding: 4px 8px; border-radius: var(--dds-control-border-radius); font-size: 11px; font-weight: 600;">[👁 Preview Active]</span>
        <span style="background: var(--dds-control-bg-color); border: 1px solid var(--dds-control-border-color); color: var(--dds-text-default-color); padding: 4px 8px; border-radius: var(--dds-control-border-radius); font-size: 11px; font-weight: 600;">[Template Source]</span>
        <span style="background: var(--dds-control-bg-color); border: 1px solid var(--dds-control-border-color); color: var(--dds-text-default-color); padding: 4px 8px; border-radius: var(--dds-control-border-radius); font-size: 11px; font-weight: 600;">[Output HTML]</span>
      </l-cluster>
    </div>

    <!-- Isolated Stage Viewport -->
    <div style="background: var(--dds-surface-stage-bg-color); color: var(--dds-text-muted-color); padding: 24px 16px; border-radius: var(--dds-control-border-radius); text-align: center; border: 1px dashed var(--dds-surface-stage-border-color);">
      <div style="font-weight: 700; font-size: 12px; color: var(--dds-text-prominent-color);">
        data-surface="stage"
      </div>
      <div style="font-family: var(--dds-text-code-font); font-size: 11px; color: var(--dds-text-muted-color); margin-top: 4px;">
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
