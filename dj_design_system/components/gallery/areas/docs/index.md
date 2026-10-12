# Documentation Area

- **Template Path**: `dj_design_system/templates/dj_design_system/gallery/panes/docs.html`
- **Surface**: `data-surface="docs"`
- **Parent Layout**: Injected into the `#pane-docs` primary slot in `gallery/component.html`.

The Documentation area coordinates the complete reference view for a component or variant. It structures the page into four specialized sub-areas assembled sequentially within an `<l-stack>` layout.

```canvas
<div style="border: 2px dashed #0284c7; background: rgba(2, 132, 199, 0.04); border-radius: 8px; padding: 14px;">
  <div style="font-family: monospace; font-size: 11px; font-weight: 700; color: #0369a1; text-transform: uppercase; margin-bottom: 8px;">
    Documentation Area Container
  </div>

  <div style="border: 2px dashed #0369a1; background: #ffffff; border-radius: 6px; padding: 14px;">
    <div style="font-family: monospace; font-size: 10px; font-weight: 700; color: #0284c7; margin-bottom: 8px;">
      &lt;l-stack&gt;
    </div>

    <l-stack style="--space: 12px;">
      <!-- Header Sub-Area Block -->
      <div style="background: #0284c7; color: #ffffff; padding: 12px 16px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
        <div style="font-weight: 700; font-size: 13px;">Sub-Area: Header (gallery/panes/docs/header.html)</div>
        <div style="font-size: 11px; opacity: 0.9; margin-top: 4px;">
          Component Title, Badges, and Docstring Prose (or Variant Preview Stage)
        </div>
      </div>

      <div style="border-top: 2px dashed #94a3b8; margin: 4px 0; font-family: monospace; font-size: 9px; color: #64748b; text-align: center;">
        &lt;hr&gt;
      </div>

      <!-- Usage Sub-Area Block -->
      <div style="background: #0369a1; color: #ffffff; padding: 12px 16px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
        <div style="font-weight: 700; font-size: 13px;">Sub-Area: Usage (gallery/panes/docs/usage.html)</div>
        <div style="font-size: 11px; opacity: 0.9; margin-top: 4px;">
          Minimal, Maximal, and Namespaced Code Snippets &amp; Live Canvas Previews
        </div>
      </div>

      <div style="border-top: 2px dashed #94a3b8; margin: 4px 0; font-family: monospace; font-size: 9px; color: #64748b; text-align: center;">
        &lt;hr&gt;
      </div>

      <!-- Params Sub-Area Block -->
      <div style="background: #075985; color: #ffffff; padding: 12px 16px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
        <div style="font-weight: 700; font-size: 13px;">Sub-Area: Parameters (gallery/panes/docs/params.html)</div>
        <div style="font-size: 11px; opacity: 0.9; margin-top: 4px;">
          Tabular Specifications for Component Parameters and Declared Slots
        </div>
      </div>

      <div style="border-top: 2px dashed #94a3b8; margin: 4px 0; font-family: monospace; font-size: 9px; color: #64748b; text-align: center;">
        &lt;hr&gt;
      </div>

      <!-- Further Sub-Area Block -->
      <div style="background: #0c4a6e; color: #ffffff; padding: 12px 16px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
        <div style="font-weight: 700; font-size: 13px;">Sub-Area: Further Documentation (gallery/panes/docs/further.html)</div>
        <div style="font-size: 11px; opacity: 0.9; margin-top: 4px;">
          Extended Markdown Prose Rendered from co-located index.md
        </div>
      </div>
    </l-stack>
  </div>
</div>
```

### Overriding

Create `templates/dj_design_system/gallery/panes/docs.html` in your consuming project to reorder sections or inject custom panels:

```django
<l-stack data-docs-stack>
    {% include "dj_design_system/gallery/panes/docs/header.html" %}
    <hr data-docs-divider>
    {% include "dj_design_system/gallery/panes/docs/usage.html" %}
    <hr data-docs-divider>
    {% include "dj_design_system/gallery/panes/docs/params.html" %}
</l-stack>
```
