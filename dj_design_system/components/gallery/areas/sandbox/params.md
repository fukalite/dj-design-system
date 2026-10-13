# Sandbox Parameters Area

- **Template Path**: `dj_design_system/components/gallery/composites/sandbox_params/sandbox_params.html`
- **Surface**: `data-surface="sandbox"`
- **Parent Layout**: Positioned as the lower drawer inside `panes/sandbox.html`.

The Sandbox Parameters area generates dynamic form controls mapped to a component's declared parameters. Powered by HTMX, it dispatches asynchronous updates on every change or debounced keystroke, updating the isolated canvas stage instantly without reloading the page.

```canvas
<div style="border: 2px dashed var(--dds-control-accent-color); background: var(--dds-state-hover-bg-color); border-radius: var(--dds-radius-md); padding: var(--dds-space-md);">
  <div style="font-family: var(--dds-text-code-font); font-size: 11px; font-weight: 700; color: var(--dds-control-accent-color); text-transform: uppercase; margin-bottom: 8px;">
    &lt;dds-sandbox-params&gt;
  </div>

  <div style="border: 1px solid var(--dds-control-border-color); background: var(--dds-surface-bg-color); border-radius: var(--dds-control-border-radius); padding: 12px;">
    <div style="font-family: var(--dds-text-code-font); font-size: 10px; font-weight: 700; color: var(--dds-control-accent-color); margin-bottom: 8px;">
      &lt;l-stack&gt;
    </div>

    <l-stack style="--space: 10px;">
      <div style="background: var(--dds-control-bg-color); border: 1px solid var(--dds-control-border-color); border-radius: var(--dds-control-border-radius); padding: 8px 12px;">
        <span style="font-size: 11px; font-weight: 600; color: var(--dds-text-prominent-color);">label: "Click me"</span>
        <div style="font-size: 10px; color: var(--dds-text-muted-color);">dds__form_field (String input)</div>
      </div>
      <div style="background: var(--dds-control-bg-color); border: 1px solid var(--dds-control-border-color); border-radius: var(--dds-control-border-radius); padding: 8px 12px;">
        <span style="font-size: 11px; font-weight: 600; color: var(--dds-text-prominent-color);">variant: "primary"</span>
        <div style="font-size: 10px; color: var(--dds-text-muted-color);">dds__form_field (Choice select dropdown)</div>
      </div>
      <div style="background: var(--dds-control-bg-color); border: 1px solid var(--dds-control-border-color); border-radius: var(--dds-control-border-radius); padding: 8px 12px;">
        <span style="font-size: 11px; font-weight: 600; color: var(--dds-text-prominent-color);">disabled: False</span>
        <div style="font-size: 10px; color: var(--dds-text-muted-color);">dds__form_field (Boolean checkbox switch)</div>
      </div>
    </l-stack>
  </div>
</div>
```

### Overriding

Include the parameters drawer into any custom workbench view:

```django
{% dds__sandbox_params param_rows=param_rows action_url=request.path active_theme=sandbox_active_theme active_variant=active_variant hx_target="[data-gallery-sandbox-body]" %}
```
