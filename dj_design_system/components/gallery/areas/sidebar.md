---
order: 2
---
# Sidebar Area

- **Template Path**: `dj_design_system/templates/dj_design_system/gallery/areas/sidebar.html`
- **Stylesheet**: `dj_design_system/static/dj_design_system/areas/sidebar.css`
- **Root Selector**: `.dds-sidebar`
- **Surface**: `data-surface="sidebar"`
- **Parent Layout**: Injected into `{% block sidebar %}` inside `gallery/base.html` within `<div data-shell-sidebar>`.

The Sidebar area hosts the primary navigation drawer for browsing categories, components, and documentation. Setting `data-surface="sidebar"` applies an inverted dark theme to focus visual attention on content, automatically preserves scroll position across navigations, and anchors the gallery theme switcher in its footer.

### Styling Responsibilities & Encapsulation

- **File**: `areas/sidebar.css` encapsulated within `@layer blocks`.
- **Vertical Flex Layout**: Organises the sidebar into a three-tier vertical flex column: sticky brand header, scrollable body hosting `dds__nav_tree` (`overflow-y: auto`, `flex: 1`), and pinned bottom footer.
- **Surface Inversion**: Inherits token delegation from `[data-surface="sidebar"]`, rendering an inverted dark surface in light mode while automatically adapting when the entire page enters dark theme.
- **Drawer Encapsulation**: Enforces right border dividers and mobile drawer bounds without styling the internal nodes of `dds__nav_tree` directly.

```canvas
<div style="border: 2px dashed var(--dds-control-accent-color); background: var(--dds-state-hover-bg-color); border-radius: var(--dds-radius-md); padding: var(--dds-space-md); max-width: 320px;">
  <div style="font-family: var(--dds-text-code-font); font-size: 11px; font-weight: 700; color: var(--dds-control-accent-color); text-transform: uppercase; margin-bottom: 8px;">
    &lt;aside class="dds-sidebar" data-surface="sidebar"&gt;
  </div>

  <div data-surface="sidebar" style="border: 1px solid var(--dds-control-border-color); background: var(--dds-surface-bg-color); border-radius: var(--dds-control-border-radius); padding: 12px; color: var(--dds-text-default-color);">
    <div style="font-family: var(--dds-text-code-font); font-size: 10px; font-weight: 700; color: var(--dds-control-accent-color); margin-bottom: 8px;">
      &lt;l-stack&gt;
    </div>

    <l-stack style="--space: 10px;">
      <!-- Header -->
      <div style="background: var(--dds-control-bg-color); border: 1px solid var(--dds-control-border-color); padding: 8px 10px; border-radius: var(--dds-control-border-radius); font-size: 11px; font-weight: 700; color: var(--dds-text-prominent-color);">
        Header: Brand Logo &amp; Title
      </div>

      <!-- Body / Tree -->
      <div style="background: var(--dds-control-bg-color); padding: 24px 10px; border-radius: var(--dds-control-border-radius); border: 1px dashed var(--dds-control-border-color);">
        <div style="font-size: 11px; font-weight: 600; color: var(--dds-control-accent-color);">
          dds__nav_tree
        </div>
        <div style="font-size: 10px; color: var(--dds-text-muted-color); margin-top: 4px;">
          Scrollable navigation tree with state retention
        </div>
      </div>

      <!-- Footer -->
      <div style="background: var(--dds-control-bg-color); border: 1px solid var(--dds-control-border-color); padding: 8px 10px; border-radius: var(--dds-control-border-radius); font-size: 11px; color: var(--dds-text-muted-color);">
        Footer: Theme Switcher Toggle
      </div>
    </l-stack>
  </div>
</div>
```

### Overriding

Create `templates/dj_design_system/gallery/areas/sidebar.html` to inject additional branding or custom footer links:

```django
{% extends "dj_design_system/gallery/areas/sidebar.html" %}

{% block sidebar_footer %}
    <div class="sidebar-custom-footer">
        <a href="/status/">System Status</a>
    </div>
{% endblock %}
```
