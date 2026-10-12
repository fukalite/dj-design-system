# Documentation Header Area

- **Template Path**: `dj_design_system/templates/dj_design_system/gallery/panes/docs/header.html`
- **Surface**: `data-surface="docs"` (with preview stage in `data-surface="stage"`)
- **Parent Layout**: Positioned as the top block inside `panes/docs.html`.

The Documentation Header area renders the leading block of the documentation pane. For standard components, it displays the docstring prose description; for variants, it renders a badge header, isolated preview stage, and quick link to open the preview in the sandbox.

```canvas
<div style="border: 2px dashed #0284c7; background: rgba(2, 132, 199, 0.04); border-radius: 8px; padding: 14px;">
  <div style="font-family: monospace; font-size: 11px; font-weight: 700; color: #0369a1; text-transform: uppercase; margin-bottom: 8px;">
    &lt;l-stack&gt;
  </div>

  <l-stack style="--space: 14px;">
    <!-- Standard Description Block -->
    <div style="border: 1px dashed #0284c7; background: #ffffff; border-radius: 6px; padding: 12px;">
      <div style="font-size: 10px; font-weight: 700; color: #0284c7; margin-bottom: 6px;">Standard Component View</div>
      <h3 style="margin: 0 0 6px 0; font-size: 14px; color: #0f172a;">Description</h3>
      <p style="margin: 0; font-size: 11px; color: #475569;">
        Formatted component docstrings extracted automatically from Python classes.
      </p>
    </div>

    <!-- Variant Header & Preview Stage -->
    <div style="border: 1px dashed #6366f1; background: #ffffff; border-radius: 6px; padding: 12px;">
      <div style="font-size: 10px; font-weight: 700; color: #4338ca; margin-bottom: 6px;">Variant Inspection View</div>
      <l-cluster style="justify-content: space-between; align-items: center; margin-bottom: 10px;">
        <span style="background: #e0e7ff; color: #3730a3; padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;">Variant: Primary Action</span>
        <span style="background: #f1f5f9; color: #475569; padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: 600;">Open in Sandbox →</span>
      </l-cluster>
      <div style="background: #0f172a; color: #94a3b8; padding: 16px; border-radius: 4px; text-align: center; font-size: 11px;">
        data-surface="stage" (Live Variant Preview Iframe)
      </div>
    </div>
  </l-stack>
</div>
```

### Overriding

Create `templates/dj_design_system/gallery/panes/docs/header.html` to add custom headers or documentation metadata:

```django
{% extends "dj_design_system/gallery/panes/docs/header.html" %}
```
