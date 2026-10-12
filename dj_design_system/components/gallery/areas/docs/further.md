# Documentation Further Area

- **Template Path**: `dj_design_system/templates/dj_design_system/gallery/panes/docs/further.html`
- **Surface**: `data-surface="docs"`
- **Parent Layout**: Included inside `panes/docs.html` when a co-located `index.md` exists.

The Documentation Further area renders extended markdown documentation and live embedded canvas wireframes discovered from a component's co-located `index.md` file. It injects rendered HTML into a typography prose container to preserve readable styling.

```canvas
<div style="border: 2px dashed #0284c7; background: rgba(2, 132, 199, 0.04); border-radius: 8px; padding: 14px;">
  <div style="font-family: monospace; font-size: 11px; font-weight: 700; color: #0369a1; text-transform: uppercase; margin-bottom: 8px;">
    &lt;div class="dds-prose" data-surface="docs"&gt;
  </div>

  <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 6px; padding: 14px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
    <h3 style="margin: 0 0 6px 0; font-size: 14px; color: #0f172a;">Extended Documentation</h3>
    <p style="margin: 0 0 10px 0; font-size: 11px; color: #475569;">
      Rendered HTML extracted from co-located index.md files.
    </p>

    <!-- Embedded Canvas Demonstration -->
    <div style="border: 1px dashed #6366f1; background: #faf5ff; border-radius: 4px; padding: 10px; text-align: center;">
      <span style="font-family: monospace; font-size: 10px; color: #6d28d9; font-weight: 700;">
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
