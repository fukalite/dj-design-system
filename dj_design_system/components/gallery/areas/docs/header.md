# Documentation Header Area

- **Template Path**: `dj_design_system/templates/dj_design_system/gallery/panes/docs/header.html`
- **Surface**: `data-surface="docs"` (with preview stage in `data-surface="stage"`)
- **Parent Layout**: Positioned as the top block inside `panes/docs.html`.

The Documentation Header area renders the leading block of the documentation pane. For standard components, it displays the docstring prose description; for variants, it renders a badge header, isolated preview stage, and quick link to open the preview in the sandbox.

```canvas
<div style="border: 2px dashed var(--dds-control-accent-color); background: var(--dds-state-hover-bg-color); border-radius: var(--dds-radius-md); padding: var(--dds-space-md);">
  <div style="font-family: var(--dds-text-code-font); font-size: 11px; font-weight: 700; color: var(--dds-control-accent-color); text-transform: uppercase; margin-bottom: 8px;">
    &lt;l-stack&gt;
  </div>

  <l-stack style="--space: 14px;">
    <!-- Standard Description Block -->
    <div style="border: 1px dashed var(--dds-control-border-color); background: var(--dds-surface-bg-color); border-radius: var(--dds-control-border-radius); padding: 12px;">
      <div style="font-size: 10px; font-weight: 700; color: var(--dds-control-accent-color); margin-bottom: 6px;">Standard Component View</div>
      <h3 style="margin: 0 0 6px 0; font-size: 14px; color: var(--dds-text-prominent-color);">Description</h3>
      <p style="margin: 0; font-size: 11px; color: var(--dds-text-muted-color);">
        Formatted component docstrings extracted automatically from Python classes.
      </p>
    </div>

    <!-- Variant Header & Preview Stage -->
    <div style="border: 1px dashed var(--dds-control-accent-color); background: var(--dds-surface-bg-color); border-radius: var(--dds-control-border-radius); padding: 12px;">
      <div style="font-size: 10px; font-weight: 700; color: var(--dds-control-accent-color); margin-bottom: 6px;">Variant Inspection View</div>
      <l-cluster style="justify-content: space-between; align-items: center; margin-bottom: 10px;">
        <span style="background: var(--dds-status-info-bg-color); color: var(--dds-status-info-text-color); border: 1px solid var(--dds-status-info-border-color); padding: 2px 8px; border-radius: var(--dds-control-border-radius); font-size: 11px; font-weight: 600;">Variant: Primary Action</span>
        <span style="background: var(--dds-state-hover-bg-color); color: var(--dds-text-default-color); border: 1px solid var(--dds-control-border-color); padding: 4px 10px; border-radius: var(--dds-control-border-radius); font-size: 11px; font-weight: 600;">Open in Sandbox →</span>
      </l-cluster>
      <div style="background: var(--dds-surface-stage-bg-color); color: var(--dds-text-muted-color); border: 1px dashed var(--dds-surface-stage-border-color); padding: 16px; border-radius: var(--dds-control-border-radius); text-align: center; font-size: 11px;">
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
