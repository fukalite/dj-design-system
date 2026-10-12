# Documentation Parameters Area

- **Template Path**: `dj_design_system/templates/dj_design_system/gallery/panes/docs/params.html`
- **Surface**: `data-surface="docs"`
- **Parent Layout**: Positioned as the parameters section inside `panes/docs.html`.

The Documentation Parameters area provides tabular reference specifications for all component parameters and declared template slots. It documents parameter names, accepted types, requirement status, default values, and docstring descriptions using the compact table component.

```canvas
<div style="border: 2px dashed #0284c7; background: rgba(2, 132, 199, 0.04); border-radius: 8px; padding: 14px;">
  <div style="font-family: monospace; font-size: 11px; font-weight: 700; color: #0369a1; text-transform: uppercase; margin-bottom: 8px;">
    &lt;l-stack&gt;
  </div>

  <l-stack style="--space: 12px;">
    <!-- Parameters Table Solid Block -->
    <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 6px; padding: 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
      <h3 style="margin: 0 0 8px 0; font-size: 13px; color: #0f172a;">Parameters Table (dds__table)</h3>
      <div style="font-size: 11px; color: #475569;">
        Columns: Name | Type Badge | Required | Default | Description
      </div>
    </div>

    <!-- Slots Table Solid Block -->
    <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 6px; padding: 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
      <h3 style="margin: 0 0 8px 0; font-size: 13px; color: #0f172a;">Slots Table (dds__table)</h3>
      <div style="font-size: 11px; color: #475569;">
        Columns: Slot Name | Default Content Flag | Description
      </div>
    </div>
  </l-stack>
</div>
```

### Overriding

Create `templates/dj_design_system/gallery/panes/docs/params.html` to inject extra columns or custom documentation badges:

```django
{% extends "dj_design_system/gallery/panes/docs/params.html" %}
```
