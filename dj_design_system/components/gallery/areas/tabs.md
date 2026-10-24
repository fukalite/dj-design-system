---
order: 3
---
# Tabs Area

- **Template Path**: `dj_design_system/templates/dj_design_system/gallery/areas/tabs.html`
- **Stylesheet**: `dj_design_system/static/dj_design_system/areas/tabs.css`
- **Root Selector**: `[data-component-tabs]`
- **Surface**: Inherits `data-surface="docs"` from the main viewport shell.
- **Parent Layout**: Positioned directly above component panes in `gallery/component.html`.

The Tabs area renders the view switcher pinned above component documentation and workbenches. It coordinates with the horizontal split pane to toggle between the **Documentation** pane and the **Sandbox** pane, preserving the selected view across page navigations.

### Styling Responsibilities & Encapsulation

- **File**: `areas/tabs.css` encapsulated within `@layer blocks`.
- **Tab Navigation Bar**: Controls the container border-bottom divider, background tint, and horizontal alignment across viewport sizes.
- **State Indicators**: Formats active tab state via an accent-coloured bottom boundary line (`border-bottom: 2px solid var(--dds-control-accent-color)`), subtle hover feedback, and clear focus outlines for keyboard navigation.
- **Boundary Cleanliness**: Scoped strictly to `[data-component-tabs]` and avoids leaking styles into descendant tab controls or sibling panes.

```canvas
<div style="border: 2px dashed var(--dds-control-accent-color); background: var(--dds-state-hover-bg-color); border-radius: var(--dds-radius-md); padding: var(--dds-space-md);">
  <div style="font-family: var(--dds-text-code-font); font-size: 11px; font-weight: 700; color: var(--dds-control-accent-color); text-transform: uppercase; margin-bottom: 8px;">
    &lt;nav class="dds-tabs"&gt;
  </div>

  <div style="border: 1px solid var(--dds-control-border-color); background: var(--dds-surface-bg-color); border-radius: var(--dds-control-border-radius); padding: 12px;">
    <div style="font-family: var(--dds-text-code-font); font-size: 10px; font-weight: 700; color: var(--dds-control-accent-color); margin-bottom: 8px;">
      &lt;l-cluster&gt;
    </div>

    <l-cluster style="gap: 8px; align-items: center;">
      <!-- Active Docs Tab -->
      <div style="background: var(--dds-control-accent-color); color: var(--dds-text-on-accent-color, #ffffff); padding: 6px 14px; border-radius: var(--dds-control-border-radius); font-size: 12px; font-weight: 600;">
        Docs (Active)
      </div>

      <!-- Inactive Sandbox Tab -->
      <div style="background: var(--dds-control-bg-color); color: var(--dds-text-muted-color); padding: 6px 14px; border-radius: var(--dds-control-border-radius); font-size: 12px; font-weight: 600; border: 1px solid var(--dds-control-border-color);">
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
