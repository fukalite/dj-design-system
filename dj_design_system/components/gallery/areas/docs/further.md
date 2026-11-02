---
order: 4
---
# Documentation Further Area

- **Template Path**: `dj_design_system/templates/dj_design_system/gallery/panes/docs/further.html`
- **Surface**: `data-surface="docs"`
- **Parent Layout**: Included inside `panes/docs.html` when a co-located `index.md` exists.

The Documentation Further area renders extended markdown documentation and live embedded canvas wireframes discovered from a component's co-located `index.md` file. It injects rendered HTML into a typography prose container to preserve readable styling.

```canvas
<div style="border: 2px dashed var(--dds-control-accent-color); background: var(--dds-state-hover-bg-color); border-radius: var(--dds-radius-md); padding: var(--dds-space-md);">
  <div style="font-family: var(--dds-text-code-font); font-size: 11px; font-weight: 700; color: var(--dds-control-accent-color); text-transform: uppercase; margin-bottom: 8px;">
    &lt;div class="dds-prose" data-surface="docs"&gt;
  </div>

  <div style="background: var(--dds-surface-bg-color); border: 1px solid var(--dds-control-border-color); border-radius: var(--dds-control-border-radius); padding: 14px; box-shadow: 0 1px 2px rgba(0,0,0,0.1);">
    <h3 style="margin: 0 0 6px 0; font-size: 14px; color: var(--dds-text-prominent-color);">Extended Documentation</h3>
    <p style="margin: 0 0 10px 0; font-size: 11px; color: var(--dds-text-muted-color);">
      Rendered HTML extracted from co-located index.md files.
    </p>

    <!-- Embedded Canvas Demonstration -->
    <div style="border: 1px dashed var(--dds-status-info-border-color); background: var(--dds-status-info-bg-color); border-radius: var(--dds-control-border-radius); padding: 10px; text-align: center;">
      <span style="font-family: var(--dds-text-code-font); font-size: 10px; color: var(--dds-status-info-text-color); font-weight: 700;">
        Embedded Live Canvas Block (```canvas)
      </span>
    </div>
  </div>
</div>
```

### Overriding

Create `templates/dj_design_system/gallery/panes/docs/further.html` to add custom documentation footers or discussion widgets:

```django
{% extends "dj_design_system/gallery/panes/docs/further.html" %}
```
