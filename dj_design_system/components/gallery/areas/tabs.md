# Tabs Area

- **Template Path**: `dj_design_system/templates/dj_design_system/gallery/areas/tabs.html`
- **Surface**: Inherits `data-surface="docs"` from the main viewport shell.
- **Parent Layout**: Positioned directly above component panes in `gallery/component.html`.

The Tabs area renders the view switcher pinned above component documentation and workbenches. It coordinates with the horizontal split pane to toggle between the **Documentation** pane and the **Sandbox** pane, preserving the selected view across page navigations.

```canvas
<div style="border: 2px dashed #0284c7; background: rgba(2, 132, 199, 0.04); border-radius: 8px; padding: 14px;">
  <div style="font-family: monospace; font-size: 11px; font-weight: 700; color: #0369a1; text-transform: uppercase; margin-bottom: 8px;">
    &lt;nav class="dds-tabs"&gt;
  </div>

  <div style="border: 2px dashed #0369a1; background: #ffffff; border-radius: 6px; padding: 12px;">
    <div style="font-family: monospace; font-size: 10px; font-weight: 700; color: #0284c7; margin-bottom: 8px;">
      &lt;l-cluster&gt;
    </div>

    <l-cluster style="gap: 8px; align-items: center;">
      <!-- Active Docs Tab -->
      <div style="background: #0284c7; color: #ffffff; padding: 6px 14px; border-radius: 4px; font-size: 12px; font-weight: 600;">
        Docs (Active)
      </div>

      <!-- Inactive Sandbox Tab -->
      <div style="background: #f1f5f9; color: #475569; padding: 6px 14px; border-radius: 4px; font-size: 12px; font-weight: 600; border: 1px solid #cbd5e1;">
        Sandbox
      </div>
    </l-cluster>
  </div>
</div>
```

### Overriding

Create `templates/dj_design_system/gallery/areas/tabs.html` to add custom tabs or telemetry hooks:

```django
{% load design_components %}
{% dds__tabs variant="switcher" tabs=component_view_tabs active_tab=active_view_slug %}
```
