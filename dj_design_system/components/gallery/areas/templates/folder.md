# Folder Template

- **Template Path**: `dj_design_system/templates/dj_design_system/gallery/panes/folder.html`
- **Surface**: `data-surface="docs"`
- **Parent Layout**: Included inside `gallery/folder.html` when browsing a directory that lacks an `index.md`.

The Folder template renders an auto-fitting responsive card grid representing child categories, components, and documents. When `DEBUG` mode is active, it includes a guidance notice prompting developers how to replace the grid with an `index.md` file.

```canvas
<div style="border: 2px dashed #0284c7; background: rgba(2, 132, 199, 0.04); border-radius: 8px; padding: 14px;">
  <div style="font-family: monospace; font-size: 11px; font-weight: 700; color: #0369a1; text-transform: uppercase; margin-bottom: 8px;">
    &lt;l-grid&gt;
  </div>

  <l-grid style="--min: 180px; --space: 10px;">
    <!-- Component Card Solid Block -->
    <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 6px; padding: 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
      <l-cluster style="justify-content: space-between; align-items: center;">
        <span style="font-weight: 600; font-size: 12px; color: #0f172a;">dds__icon + Button</span>
        <span style="background: #e2e8f0; color: #334155; font-size: 9px; padding: 2px 6px; border-radius: 4px;">dds__badge</span>
      </l-cluster>
      <div style="font-size: 10px; color: #64748b; margin-top: 6px;">3 variants</div>
    </div>

    <!-- Folder Card Solid Block -->
    <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 6px; padding: 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
      <l-cluster style="justify-content: space-between; align-items: center;">
        <span style="font-weight: 600; font-size: 12px; color: #0f172a;">dds__icon + Layouts</span>
        <span style="background: #e2e8f0; color: #334155; font-size: 9px; padding: 2px 6px; border-radius: 4px;">dds__badge</span>
      </l-cluster>
      <div style="font-size: 10px; color: #64748b; margin-top: 6px;">4 components</div>
    </div>

    <!-- Document Card Solid Block -->
    <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 6px; padding: 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
      <l-cluster style="justify-content: space-between; align-items: center;">
        <span style="font-weight: 600; font-size: 12px; color: #0f172a;">dds__icon + Guide</span>
        <span style="background: #e2e8f0; color: #334155; font-size: 9px; padding: 2px 6px; border-radius: 4px;">dds__badge</span>
      </l-cluster>
      <div style="font-size: 10px; color: #64748b; margin-top: 6px;">1 document</div>
    </div>
  </l-grid>
</div>
```

### Overriding

Create `templates/dj_design_system/gallery/panes/folder.html` to provide custom list layouts or category filtering:

```django
{% extends "dj_design_system/gallery/panes/folder.html" %}
```
