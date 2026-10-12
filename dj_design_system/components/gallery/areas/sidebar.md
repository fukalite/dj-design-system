# Sidebar Area

- **Template Path**: `dj_design_system/templates/dj_design_system/gallery/areas/sidebar.html`
- **Surface**: `data-surface="sidebar"`
- **Parent Layout**: Injected into `{% block sidebar %}` inside `gallery/base.html` within `<div data-shell-sidebar>`.

The Sidebar area hosts the primary navigation drawer for browsing categories, components, and documentation. Setting `data-surface="sidebar"` applies an inverted dark theme to focus visual attention on content, automatically preserves scroll position across navigations, and anchors the gallery theme switcher in its footer.

```canvas
<div style="border: 2px dashed #0284c7; background: rgba(2, 132, 199, 0.04); border-radius: 8px; padding: 14px; max-width: 320px;">
  <div style="font-family: monospace; font-size: 11px; font-weight: 700; color: #0369a1; text-transform: uppercase; margin-bottom: 8px;">
    &lt;aside class="dds-sidebar" data-surface="sidebar"&gt;
  </div>

  <div style="border: 2px dashed #0369a1; background: #0f172a; border-radius: 6px; padding: 12px; color: #ffffff;">
    <div style="font-family: monospace; font-size: 10px; font-weight: 700; color: #38bdf8; margin-bottom: 8px;">
      &lt;l-stack&gt;
    </div>

    <l-stack style="--space: 10px;">
      <!-- Header -->
      <div style="background: #1e293b; padding: 8px 10px; border-radius: 4px; font-size: 11px; font-weight: 700; color: #f8fafc;">
        Header: Brand Logo &amp; Title
      </div>

      <!-- Body / Tree -->
      <div style="background: #1e293b; padding: 24px 10px; border-radius: 4px; border: 1px dashed #334155;">
        <div style="font-size: 11px; font-weight: 600; color: #38bdf8;">
          dds__nav_tree
        </div>
        <div style="font-size: 10px; color: #94a3b8; margin-top: 4px;">
          Scrollable navigation tree with state retention
        </div>
      </div>

      <!-- Footer -->
      <div style="background: #1e293b; padding: 8px 10px; border-radius: 4px; font-size: 11px; color: #cbd5e1;">
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
