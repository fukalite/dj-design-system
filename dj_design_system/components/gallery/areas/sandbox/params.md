# Sandbox Parameters Area

- **Template Path**: `dj_design_system/components/gallery/composites/sandbox_params/sandbox_params.html`
- **Surface**: `data-surface="sandbox"`
- **Parent Layout**: Positioned as the lower drawer inside `panes/sandbox.html`.

The Sandbox Parameters area generates dynamic form controls mapped to a component's declared parameters. Powered by HTMX, it dispatches asynchronous updates on every change or debounced keystroke, updating the isolated canvas stage instantly without reloading the page.

```canvas
<div style="border: 2px dashed #3730a3; background: rgba(55, 48, 163, 0.04); border-radius: 8px; padding: 14px;">
  <div style="font-family: monospace; font-size: 11px; font-weight: 700; color: #312e81; text-transform: uppercase; margin-bottom: 8px;">
    &lt;dds-sandbox-params&gt;
  </div>

  <div style="border: 2px dashed #4f46e5; background: #ffffff; border-radius: 6px; padding: 12px;">
    <div style="font-family: monospace; font-size: 10px; font-weight: 700; color: #4338ca; margin-bottom: 8px;">
      &lt;l-stack&gt;
    </div>

    <l-stack style="--space: 10px;">
      <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 4px; padding: 8px 12px;">
        <span style="font-size: 11px; font-weight: 600; color: #0f172a;">label: "Click me"</span>
        <div style="font-size: 10px; color: #64748b;">dds__form_field (String input)</div>
      </div>
      <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 4px; padding: 8px 12px;">
        <span style="font-size: 11px; font-weight: 600; color: #0f172a;">variant: "primary"</span>
        <div style="font-size: 10px; color: #64748b;">dds__form_field (Choice select dropdown)</div>
      </div>
      <div style="background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 4px; padding: 8px 12px;">
        <span style="font-size: 11px; font-weight: 600; color: #0f172a;">disabled: False</span>
        <div style="font-size: 10px; color: #64748b;">dds__form_field (Boolean checkbox switch)</div>
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
