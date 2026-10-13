# Index Template

- **Template Path**: `dj_design_system/templates/dj_design_system/gallery/panes/index.html`
- **Surface**: `data-surface="docs"`
- **Parent Layout**: Included inside `gallery/index.html` when visiting the root gallery URL (`/`).

The Index template renders the default welcome screen when visitors enter the gallery root. It displays the design system title, introductory browsing guidance, the total component count, and a warning notice if served from an offline static build.

```canvas
<div style="border: 2px dashed var(--dds-control-accent-color); background: var(--dds-state-hover-bg-color); border-radius: var(--dds-radius-md); padding: var(--dds-space-md);">
  <div style="font-family: var(--dds-text-code-font); font-size: 11px; font-weight: 700; color: var(--dds-control-accent-color); text-transform: uppercase; margin-bottom: 8px;">
    &lt;l-stack&gt;
  </div>

  <l-stack style="--space: 12px;">
    <!-- Welcome Prose Solid Block -->
    <div style="border: 1px solid var(--dds-control-border-color); background: var(--dds-surface-bg-color); border-radius: var(--dds-control-border-radius); padding: 14px; box-shadow: 0 1px 2px rgba(0,0,0,0.1);">
      <h2 style="margin: 0 0 6px 0; font-size: 16px; color: var(--dds-text-prominent-color);">{{ design_system_name }}</h2>
      <p style="margin: 0 0 8px 0; font-size: 12px; color: var(--dds-text-muted-color);">
        Browse components using the sidebar navigation.
      </p>
      <span style="display: inline-block; background: var(--dds-status-info-bg-color); color: var(--dds-status-info-text-color); border: 1px solid var(--dds-status-info-border-color); padding: 3px 8px; border-radius: var(--dds-control-border-radius); font-size: 11px; font-weight: 600;">
        {{ total_components_label }}
      </span>
    </div>

    <!-- Static Notice Solid Block -->
    <div style="background: var(--dds-status-warning-bg-color); border-left: 4px solid var(--dds-status-warning-border-color); padding: 10px 14px; border-radius: var(--dds-control-border-radius);">
      <strong style="color: var(--dds-status-warning-text-color); font-size: 11px;">dds__notice (Static snapshot)</strong>
      <p style="margin: 2px 0 0 0; font-size: 11px; color: var(--dds-status-warning-text-color);">
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
