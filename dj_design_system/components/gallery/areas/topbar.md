# Topbar Area

- **Template Path**: `dj_design_system/templates/dj_design_system/gallery/areas/topbar.html`
- **Surface**: `data-surface="topbar"`
- **Parent Layout**: Injected into `{% block topbar %}` inside `gallery/base.html`.

The Topbar area renders the persistent horizontal chrome anchored across the top of the gallery viewport. It coordinates global brand links, hierarchical breadcrumb trails, universal quick search, and consumer theme selectors, with an extension block for custom navigation actions.

```canvas
<div style="border: 2px dashed #0284c7; background: rgba(2, 132, 199, 0.04); border-radius: 8px; padding: 14px;">
  <div style="font-family: monospace; font-size: 11px; font-weight: 700; color: #0369a1; text-transform: uppercase; margin-bottom: 8px;">
    &lt;header class="dds-topbar" data-surface="topbar"&gt;
  </div>

  <div style="border: 2px dashed #0369a1; background: #ffffff; border-radius: 6px; padding: 10px;">
    <div style="font-family: monospace; font-size: 10px; font-weight: 700; color: #0284c7; margin-bottom: 6px;">
      &lt;l-cluster&gt;
    </div>

    <l-cluster style="justify-content: space-between; align-items: center; width: 100%;">
      <!-- Leading Cluster -->
      <div style="border: 1px dashed #64748b; background: rgba(100, 116, 139, 0.05); border-radius: 4px; padding: 6px;">
        <div style="font-family: monospace; font-size: 9px; color: #475569; margin-bottom: 4px;">
          &lt;l-cluster&gt;
        </div>
        <l-cluster style="--space: 8px;" align="center">
          <div style="background: #1e293b; color: white; padding: 6px 10px; border-radius: 4px; font-size: 11px; font-weight: 600;">
            dds__button (Drawer Toggle)
          </div>
          <div style="background: #4338ca; color: white; padding: 6px 12px; border-radius: 4px; font-size: 12px; font-weight: 700;">
            Brand Link
          </div>
          <div style="background: #334155; color: white; padding: 6px 10px; border-radius: 4px; font-size: 11px;">
            dds__breadcrumb (Navigation Trail)
          </div>
        </l-cluster>
      </div>

      <!-- Actions Cluster -->
      <div style="border: 1px dashed #6366f1; background: rgba(99, 102, 241, 0.05); border-radius: 4px; padding: 6px;">
        <div style="font-family: monospace; font-size: 9px; color: #4338ca; margin-bottom: 4px;">
          &lt;l-cluster&gt;
        </div>
        <l-cluster style="--space: 8px;" align="center">
          <div style="background: #4f46e5; color: white; padding: 6px 12px; border-radius: 4px; font-size: 11px; font-weight: 600;">
            dds__search_box (Universal Search)
          </div>
          <div style="background: #6366f1; color: white; padding: 6px 10px; border-radius: 4px; font-size: 11px; font-weight: 600;">
            dds__theme_select (Theme Selector)
          </div>
          <div style="background: #1e293b; color: white; padding: 6px 10px; border-radius: 4px; font-size: 11px; font-weight: 600;">
            dds__button (Theme Toggle)
          </div>
          <div style="background: #059669; color: white; padding: 6px 10px; border-radius: 4px; font-size: 11px; font-weight: 600;">
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
