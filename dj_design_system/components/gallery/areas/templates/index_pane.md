# Index Template

- **Template Path**: `dj_design_system/templates/dj_design_system/gallery/panes/index.html`
- **Surface**: `data-surface="docs"`
- **Parent Layout**: Included inside `gallery/index.html` when visiting the root gallery URL (`/`).

The Index template renders the default welcome screen when visitors enter the gallery root. It displays the design system title, introductory browsing guidance, the total component count, and a warning notice if served from an offline static build.

```canvas
<div style="border: 2px dashed #0284c7; background: rgba(2, 132, 199, 0.04); border-radius: 8px; padding: 14px;">
  <div style="font-family: monospace; font-size: 11px; font-weight: 700; color: #0369a1; text-transform: uppercase; margin-bottom: 8px;">
    &lt;l-stack&gt;
  </div>

  <l-stack style="--space: 12px;">
    <!-- Welcome Prose Solid Block -->
    <div style="border: 1px solid #cbd5e1; background: #ffffff; border-radius: 6px; padding: 14px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
      <h2 style="margin: 0 0 6px 0; font-size: 16px; color: #0f172a;">{{ design_system_name }}</h2>
      <p style="margin: 0 0 8px 0; font-size: 12px; color: #475569;">
        Browse components using the sidebar navigation.
      </p>
      <span style="display: inline-block; background: #e0e7ff; color: #3730a3; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;">
        {{ total_components_label }}
      </span>
    </div>

    <!-- Static Notice Solid Block -->
    <div style="background: #fffbeb; border-left: 4px solid #f59e0b; padding: 10px 14px; border-radius: 4px;">
      <strong style="color: #b45309; font-size: 11px;">dds__notice (Static snapshot)</strong>
      <p style="margin: 2px 0 0 0; font-size: 11px; color: #92400e;">
        Interactive sandbox controls require a running Django server.
      </p>
    </div>
  </l-stack>
</div>
```

### Overriding

Create `templates/dj_design_system/gallery/panes/index.html` to render a custom branded landing page:

```django
{% load design_components %}
<l-stack style="--space: var(--dds-space-xl);">
    <div class="dds-prose" data-surface="docs">
        <h1>My Company Design System</h1>
        <p>Production component library for our web applications.</p>
    </div>
</l-stack>
```
