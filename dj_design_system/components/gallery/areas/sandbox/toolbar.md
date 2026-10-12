# Sandbox Toolbar Area

- **Template Path**: `dj_design_system/components/gallery/composites/sandbox_toolbar/sandbox_toolbar.html`
- **Surface**: `data-surface="sandbox"`
- **Parent Layout**: Positioned as the top control bar inside `panes/sandbox.html`.

The Sandbox Toolbar area provides workbench controls for testing component responsiveness, color schemes, and accessibility states. It hosts popout selectors for variants, canvas backgrounds, viewport presets, and zoom scaling, alongside quick toggles for rulers and RTL mirroring.

```canvas
<div style="border: 2px dashed #4f46e5; background: rgba(79, 70, 229, 0.04); border-radius: 8px; padding: 14px;">
  <div style="font-family: monospace; font-size: 11px; font-weight: 700; color: #4338ca; text-transform: uppercase; margin-bottom: 8px;">
    &lt;dds-sandbox-toolbar&gt;
  </div>

  <div style="border: 2px dashed #6366f1; background: #ffffff; border-radius: 6px; padding: 12px;">
    <div style="font-family: monospace; font-size: 10px; font-weight: 700; color: #4f46e5; margin-bottom: 8px;">
      &lt;l-cluster&gt;
    </div>

    <l-cluster style="gap: 8px; align-items: center;">
      <div style="background: #4f46e5; color: #ffffff; padding: 6px 12px; border-radius: 4px; font-size: 11px; font-weight: 600;">
        Variant: Default Presets ▾
      </div>
      <div style="background: #4f46e5; color: #ffffff; padding: 6px 12px; border-radius: 4px; font-size: 11px; font-weight: 600;">
        Background: Checkerboard ▾
      </div>
      <div style="background: #4f46e5; color: #ffffff; padding: 6px 12px; border-radius: 4px; font-size: 11px; font-weight: 600;">
        Viewport: 100% Fluid ▾
      </div>
      <div style="background: #4f46e5; color: #ffffff; padding: 6px 12px; border-radius: 4px; font-size: 11px; font-weight: 600;">
        Zoom: 100% ▾
      </div>
      <div style="background: #e0e7ff; color: #3730a3; padding: 6px 10px; border-radius: 4px; font-size: 11px; font-weight: 600;">
        [Ruler] [RTL] [Reset] [Open Tab]
      </div>
    </l-cluster>
  </div>
</div>
```

### Overriding

Consume or customize the toolbar by passing variant lists and canvas URLs to the built-in composite component:

```django
{% dds__sandbox_toolbar variants=gallery_variants active_variant=active_variant component_url=component_base_url backgrounds=canvas_backgrounds active_background=active_bg_value canvas_url=canvas_iframe_url reset_url=sandbox_reset_url %}
```
