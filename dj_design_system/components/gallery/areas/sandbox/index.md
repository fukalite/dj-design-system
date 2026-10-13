# Sandbox Area

- **Template Path**: `dj_design_system/templates/dj_design_system/gallery/panes/sandbox.html`
- **Stylesheet**: `dj_design_system/static/dj_design_system/panes/sandbox.css`
- **Root Selector**: `[data-sandbox-pane]`
- **Surface**: `data-surface="sandbox"`
- **Parent Layout**: Injected into the `#pane-sandbox` secondary slot in `gallery/component.html`.

The Sandbox area coordinates the interactive workbench for testing components in isolation. It assembles the toolbar controls, the isolated iframe canvas, and the live parameter mutation drawer into a unified vertical layout.

### Styling Responsibilities & Encapsulation

- **File**: `panes/sandbox.css` encapsulated within `@layer blocks`.
- **Workbench Layout**: Scoped to `[data-sandbox-pane]`. Organises the vertical flex stack hosting `dds__sandbox_toolbar`, `dds__canvas_widget`, and `dds__sandbox_params`.
- **Scrolling & Viewport**: Enforces independent vertical scrolling (`overflow-y: auto`) within the workbench pane while preserving the pinned sandbox toolbar at the top.
- **Component Boundary**: Layout controls the outer box rhythm; internal stage rendering, iframe measurements, and HTMX input fields remain fully encapsulated within their respective component stylesheets.

```canvas
<div style="border: 2px dashed var(--dds-control-accent-color); background: var(--dds-state-hover-bg-color); border-radius: var(--dds-radius-md); padding: var(--dds-space-md);">
  <div style="font-family: var(--dds-text-code-font); font-size: 11px; font-weight: 700; color: var(--dds-control-accent-color); text-transform: uppercase; margin-bottom: 8px;">
    Sandbox Area Container
  </div>

  <div style="border: 1px solid var(--dds-control-border-color); background: var(--dds-surface-bg-color); border-radius: var(--dds-control-border-radius); padding: 14px;">
    <div style="font-family: var(--dds-text-code-font); font-size: 10px; font-weight: 700; color: var(--dds-control-accent-color); margin-bottom: 8px;">
      &lt;l-stack&gt;
    </div>

    <l-stack style="--space: 12px;">
      <!-- Sandbox Toolbar Sub-Area -->
      <div style="background: var(--dds-control-bg-color); border: 1px solid var(--dds-control-border-color); color: var(--dds-text-prominent-color); padding: 12px 16px; border-radius: var(--dds-control-border-radius); box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
        <div style="font-weight: 700; font-size: 13px;">Sub-Area: Toolbar (dds__sandbox_toolbar)</div>
        <div style="font-size: 11px; color: var(--dds-text-muted-color); margin-top: 4px;">
          Variant presets, canvas background switcher, viewport resizing, zoom, and test toggles
        </div>
      </div>

      <!-- Canvas Widget Sub-Area -->
      <div style="background: var(--dds-surface-stage-bg-color); border: 1px dashed var(--dds-surface-stage-border-color); color: var(--dds-text-prominent-color); padding: 20px 16px; border-radius: var(--dds-control-border-radius); box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
        <div style="font-weight: 700; font-size: 13px;">Sub-Area: Canvas (dds__canvas_widget)</div>
        <div style="font-size: 11px; color: var(--dds-text-muted-color); margin-top: 4px;">
          Isolated preview stage iframe (canvas/iframe.html) and template source code inspectors
        </div>
      </div>

      <!-- Sandbox Parameters Drawer Sub-Area -->
      <div style="background: var(--dds-control-bg-color); border: 1px solid var(--dds-control-border-color); color: var(--dds-text-prominent-color); padding: 12px 16px; border-radius: var(--dds-control-border-radius); box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
        <div style="font-weight: 700; font-size: 13px;">Sub-Area: Parameters Drawer (dds__sandbox_params)</div>
        <div style="font-size: 11px; color: var(--dds-text-muted-color); margin-top: 4px;">
          Live HTMX form inputs driving instantaneous parameter mutations
        </div>
      </div>
    </l-stack>
  </div>
</div>
```

### Overriding

Create `templates/dj_design_system/gallery/panes/sandbox.html` in your consuming project to customise workbench arrangement or inject audit overlays:

```django
{% load design_components %}
<l-stack data-sandbox-stack>
    {% dds__sandbox_toolbar variants=gallery_variants active_variant=active_variant component_url=component_base_url backgrounds=canvas_backgrounds active_background=active_bg_value canvas_url=canvas_iframe_url reset_url=sandbox_reset_url %}
    {% dds__canvas_widget canvas_id="sandbox" iframe_src=canvas_iframe_url source_code=source_html rendered_html=rendered_output_html background=active_bg_value title="Component preview" %}
    {% dds__sandbox_params param_rows=param_rows action_url=request.path active_theme=sandbox_active_theme active_variant=active_variant hx_target="[data-gallery-sandbox-body]" %}
</l-stack>
```
