---
order: 1
---
# Documentation Area

- **Template Path**: `dj_design_system/templates/dj_design_system/gallery/panes/docs.html`
- **Stylesheets**: `dj_design_system/static/dj_design_system/panes/docs.css` & `panes/prose.css`
- **Root Selectors**: `[data-docs-pane]` and `.dds-prose`
- **Surface**: `data-surface="docs"`
- **Parent Layout**: Injected into the `#pane-docs` primary slot in `gallery/component.html`.

The Documentation area coordinates the complete reference view for a component or variant. It structures the page into four specialized sub-areas assembled sequentially within an `<l-stack>` layout.

### Styling Responsibilities & Encapsulation

- **Files**: `panes/docs.css` and `panes/prose.css` encapsulated within `@layer blocks`.
- **Docs Pane Layout (`panes/docs.css`)**: Scoped to `[data-docs-pane]`. Manages variant preview stages, live usage demonstration frames, section dividers (`[data-docs-divider]`), and parameter/slot table containers.
- **Prose Typography (`panes/prose.css`)**: Scoped to `.dds-prose`. Enforces fluid type rhythm, proportional headings, inline code tags, code block styling, bullet lists, and blockquotes for co-located markdown prose.
- **Component Isolation**: Does not override component styles; parameter tables, icon buttons, and badges inside the documentation pane maintain complete internal encapsulation.

```canvas
<div style="border: 2px dashed var(--dds-control-accent-color); background: var(--dds-state-hover-bg-color); border-radius: var(--dds-radius-md); padding: var(--dds-space-md);">
  <div style="font-family: var(--dds-text-code-font); font-size: 11px; font-weight: 700; color: var(--dds-control-accent-color); text-transform: uppercase; margin-bottom: 8px;">
    Documentation Area Container
  </div>

  <div style="border: 1px solid var(--dds-control-border-color); background: var(--dds-surface-bg-color); border-radius: var(--dds-control-border-radius); padding: 14px;">
    <div style="font-family: var(--dds-text-code-font); font-size: 10px; font-weight: 700; color: var(--dds-control-accent-color); margin-bottom: 8px;">
      &lt;l-stack&gt;
    </div>

    <l-stack style="--space: 12px;">
      <!-- Header Sub-Area Block -->
      <div style="background: var(--dds-status-info-bg-color); border: 1px solid var(--dds-status-info-border-color); color: var(--dds-status-info-text-color); padding: 12px 16px; border-radius: var(--dds-control-border-radius); box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
        <div style="font-weight: 700; font-size: 13px;">Sub-Area: Header (gallery/panes/docs/header.html)</div>
        <div style="font-size: 11px; opacity: 0.9; margin-top: 4px;">
          Component Title, Badges, and Docstring Prose (or Variant Preview Stage)
        </div>
      </div>

      <div style="border-top: 1px dashed var(--dds-control-border-color); margin: 4px 0; font-family: var(--dds-text-code-font); font-size: 9px; color: var(--dds-text-muted-color); text-align: center;">
        &lt;hr&gt;
      </div>

      <!-- Usage Sub-Area Block -->
      <div style="background: var(--dds-surface-stage-bg-color); border: 1px solid var(--dds-surface-stage-border-color); color: var(--dds-text-prominent-color); padding: 12px 16px; border-radius: var(--dds-control-border-radius); box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
        <div style="font-weight: 700; font-size: 13px;">Sub-Area: Usage (gallery/panes/docs/usage.html)</div>
        <div style="font-size: 11px; color: var(--dds-text-muted-color); margin-top: 4px;">
          Minimal, Maximal, and Namespaced Code Snippets &amp; Live Canvas Previews
        </div>
      </div>

      <div style="border-top: 1px dashed var(--dds-control-border-color); margin: 4px 0; font-family: var(--dds-text-code-font); font-size: 9px; color: var(--dds-text-muted-color); text-align: center;">
        &lt;hr&gt;
      </div>

      <!-- Params Sub-Area Block -->
      <div style="background: var(--dds-surface-bg-color); border: 1px solid var(--dds-control-border-color); color: var(--dds-text-prominent-color); padding: 12px 16px; border-radius: var(--dds-control-border-radius); box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
        <div style="font-weight: 700; font-size: 13px;">Sub-Area: Parameters (gallery/panes/docs/params.html)</div>
        <div style="font-size: 11px; color: var(--dds-text-muted-color); margin-top: 4px;">
          Tabular Specifications for Component Parameters and Declared Slots
        </div>
      </div>

      <div style="border-top: 1px dashed var(--dds-control-border-color); margin: 4px 0; font-family: var(--dds-text-code-font); font-size: 9px; color: var(--dds-text-muted-color); text-align: center;">
        &lt;hr&gt;
      </div>

      <!-- Further Sub-Area Block -->
      <div style="background: var(--dds-state-hover-bg-color); border: 1px solid var(--dds-control-border-color); color: var(--dds-text-prominent-color); padding: 12px 16px; border-radius: var(--dds-control-border-radius); box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
        <div style="font-weight: 700; font-size: 13px;">Sub-Area: Further Documentation (gallery/panes/docs/further.html)</div>
        <div style="font-size: 11px; color: var(--dds-text-muted-color); margin-top: 4px;">
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
