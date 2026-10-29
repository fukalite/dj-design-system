# Documentation Usage Area

- **Template Path**: `dj_design_system/templates/dj_design_system/gallery/panes/docs/usage.html`
- **Surface**: `data-surface="docs"` (with preview stages in `data-surface="stage"`)
- **Parent Layout**: Positioned as the usage section inside `panes/docs.html`.

The Documentation Usage area provides live code signatures and interactive preview iframes demonstrating how to invoke the component in Django templates. It renders minimal examples with required parameters, maximal examples showcasing all available options, and namespaced import snippets.

```canvas
<div style="border: 2px dashed var(--dds-control-accent-color); background: var(--dds-state-hover-bg-color); border-radius: var(--dds-radius-md); padding: var(--dds-space-md);">
  <div style="font-family: var(--dds-text-code-font); font-size: 11px; font-weight: 700; color: var(--dds-control-accent-color); text-transform: uppercase; margin-bottom: 8px;">
    &lt;l-stack&gt;
  </div>

  <l-stack style="--space: 14px;">
    <!-- Minimal Usage Block -->
    <div style="border: 1px dashed var(--dds-control-border-color); background: var(--dds-surface-bg-color); border-radius: var(--dds-control-border-radius); padding: 12px;">
      <h3 style="margin: 0 0 6px 0; font-size: 13px; color: var(--dds-text-prominent-color);">Minimal Example</h3>
      <div style="background: var(--dds-surface-stage-bg-color); color: var(--dds-text-muted-color); border: 1px dashed var(--dds-surface-stage-border-color); padding: 14px; border-radius: var(--dds-control-border-radius); text-align: center; font-size: 11px; margin-bottom: 8px;">
        data-surface="stage" (Preview Stage Iframe)
      </div>
      <div style="background: var(--dds-surface-code-bg-color); border: 1px solid var(--dds-surface-code-border-color); padding: 8px 10px; border-radius: var(--dds-control-border-radius); font-family: var(--dds-text-code-font); font-size: 11px; color: var(--dds-surface-code-text-default-color);">
        {% verbatim %}{% dds__button label="Submit" %}{% endverbatim %}
      </div>
    </div>

    <!-- Maximal Usage Block -->
    <div style="border: 1px dashed var(--dds-control-border-color); background: var(--dds-surface-bg-color); border-radius: var(--dds-control-border-radius); padding: 12px;">
      <h3 style="margin: 0 0 6px 0; font-size: 13px; color: var(--dds-text-prominent-color);">Maximal Example</h3>
      <div style="background: var(--dds-surface-code-bg-color); border: 1px solid var(--dds-surface-code-border-color); padding: 8px 10px; border-radius: var(--dds-control-border-radius); font-family: var(--dds-text-code-font); font-size: 11px; color: var(--dds-surface-code-text-default-color);">
        {% verbatim %}{% dds__button label="Delete" variant="danger" icon="trash" size="lg" %}{% endverbatim %}
      </div>
    </div>
  </l-stack>
</div>
```

### Overriding

Create `templates/dj_design_system/gallery/panes/docs/usage.html` to add custom code tabs or framework integration examples:

```django
{% extends "dj_design_system/gallery/panes/docs/usage.html" %}
```
