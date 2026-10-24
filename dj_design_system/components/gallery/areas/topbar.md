---
order: 1
---
# Topbar Area

- **Template Path**: `dj_design_system/templates/dj_design_system/gallery/areas/topbar.html`
- **Stylesheet**: `dj_design_system/static/dj_design_system/areas/topbar.css`
- **Root Selector**: `.dds-toolbar`
- **Surface**: `data-surface="topbar"`
- **Parent Layout**: Injected into `{% block topbar %}` inside `gallery/base.html`.

The Topbar area renders the persistent horizontal chrome anchored across the top of the gallery viewport. It coordinates global brand links, hierarchical breadcrumb trails, universal quick search, and consumer theme selectors, with an extension block for custom navigation actions.

### Styling Responsibilities & Encapsulation

- **File**: `areas/topbar.css` encapsulated within `@layer blocks`.
- **Layout & Positioning**: Governs sticky positioning at the top of the viewport (`position: sticky`, `top: 0`, `z-index: var(--dds-layer-raised-z-index)`), bottom border divider, and elevation shadow.
- **Controls & Clusters**: Enforces responsive alignment for the leading drawer button and brand heading, constrains the universal search combobox input width, and aligns consumer theme controls.
- **Zero Outer Margins**: The toolbar container has zero external margins and delegates all interior distribution to `<l-cluster>`. Child components (`dds__search_box`, `dds__button`, etc.) remain fully encapsulated.

```canvas
<div style="border: 2px dashed var(--dds-control-accent-color); background: var(--dds-state-hover-bg-color); border-radius: var(--dds-radius-md); padding: var(--dds-space-md);">
  <div style="font-family: var(--dds-text-code-font); font-size: 11px; font-weight: 700; color: var(--dds-control-accent-color); text-transform: uppercase; margin-bottom: 8px;">
    &lt;header class="dds-topbar" data-surface="topbar"&gt;
  </div>

  <div data-surface="topbar" style="border: 1px solid var(--dds-control-border-color); background: var(--dds-surface-bg-color); border-radius: var(--dds-control-border-radius); padding: 10px; color: var(--dds-text-default-color);">
    <div style="font-family: var(--dds-text-code-font); font-size: 10px; font-weight: 700; color: var(--dds-control-accent-color); margin-bottom: 6px;">
      &lt;l-cluster&gt;
    </div>

    <l-cluster style="justify-content: space-between; align-items: center; width: 100%;">
      <!-- Leading Cluster -->
      <div style="border: 1px dashed var(--dds-control-border-color); background: var(--dds-state-hover-bg-color); border-radius: var(--dds-control-border-radius); padding: 6px;">
        <div style="font-family: var(--dds-text-code-font); font-size: 9px; color: var(--dds-text-muted-color); margin-bottom: 4px;">
          &lt;l-cluster&gt;
        </div>
        <l-cluster style="--space: 8px;" align="center">
          <div style="background: var(--dds-control-bg-color); border: 1px solid var(--dds-control-border-color); color: var(--dds-text-default-color); padding: 6px 10px; border-radius: var(--dds-control-border-radius); font-size: 11px; font-weight: 600;">
            dds__button (Drawer Toggle)
          </div>
          <div style="background: var(--dds-control-accent-color); color: var(--dds-text-on-accent-color, #ffffff); padding: 6px 12px; border-radius: var(--dds-control-border-radius); font-size: 12px; font-weight: 700;">
            Brand Link
          </div>
          <div style="background: var(--dds-control-bg-color); border: 1px solid var(--dds-control-border-color); color: var(--dds-text-muted-color); padding: 6px 10px; border-radius: var(--dds-control-border-radius); font-size: 11px;">
            dds__breadcrumb (Navigation Trail)
          </div>
        </l-cluster>
      </div>

      <!-- Actions Cluster -->
      <div style="border: 1px dashed var(--dds-control-border-color); background: var(--dds-state-hover-bg-color); border-radius: var(--dds-control-border-radius); padding: 6px;">
        <div style="font-family: var(--dds-text-code-font); font-size: 9px; color: var(--dds-text-muted-color); margin-bottom: 4px;">
          &lt;l-cluster&gt;
        </div>
        <l-cluster style="--space: 8px;" align="center">
          <div style="background: var(--dds-control-bg-color); border: 1px solid var(--dds-control-border-color); color: var(--dds-text-default-color); padding: 6px 12px; border-radius: var(--dds-control-border-radius); font-size: 11px; font-weight: 600;">
            dds__search_box (Universal Search)
          </div>
          <div style="background: var(--dds-control-bg-color); border: 1px solid var(--dds-control-border-color); color: var(--dds-text-default-color); padding: 6px 10px; border-radius: var(--dds-control-border-radius); font-size: 11px; font-weight: 600;">
            dds__theme_select (Theme Selector)
          </div>
          <div style="background: var(--dds-control-bg-color); border: 1px solid var(--dds-control-border-color); color: var(--dds-text-default-color); padding: 6px 10px; border-radius: var(--dds-control-border-radius); font-size: 11px; font-weight: 600;">
            dds__button (Theme Toggle)
          </div>
          <div style="background: var(--dds-status-success-bg-color); border: 1px solid var(--dds-status-success-border-color); color: var(--dds-status-success-text-color); padding: 6px 10px; border-radius: var(--dds-control-border-radius); font-size: 11px; font-weight: 600;">
            [Custom Actions Block]
          </div>
        </l-cluster>
      </div>
    </l-cluster>
  </div>
</div>
```

### Overriding

Create `templates/dj_design_system/gallery/areas/topbar.html` to inject custom toolbar actions:

```django
{% extends "dj_design_system/gallery/areas/topbar.html" %}

{% block toolbar_actions %}
    <a href="https://example.com/docs" class="dds-button" data-variant="ghost" data-size="sm">
        API Reference
    </a>
{% endblock %}
```
