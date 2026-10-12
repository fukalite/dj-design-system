# Documentation Usage Area

- **Template Path**: `dj_design_system/templates/dj_design_system/gallery/panes/docs/usage.html`
- **Surface**: `data-surface="docs"` (with preview stages in `data-surface="stage"`)
- **Parent Layout**: Positioned as the usage section inside `panes/docs.html`.

The Documentation Usage area provides live code signatures and interactive preview iframes demonstrating how to invoke the component in Django templates. It renders minimal examples with required parameters, maximal examples showcasing all available options, and namespaced import snippets.

```canvas
<div style="border: 2px dashed #0284c7; background: rgba(2, 132, 199, 0.04); border-radius: 8px; padding: 14px;">
  <div style="font-family: monospace; font-size: 11px; font-weight: 700; color: #0369a1; text-transform: uppercase; margin-bottom: 8px;">
    &lt;l-stack&gt;
  </div>

  <l-stack style="--space: 14px;">
    <!-- Minimal Usage Block -->
    <div style="border: 1px dashed #0284c7; background: #ffffff; border-radius: 6px; padding: 12px;">
      <h3 style="margin: 0 0 6px 0; font-size: 13px; color: #0f172a;">Minimal Example</h3>
      <div style="background: #0f172a; color: #94a3b8; padding: 14px; border-radius: 4px; text-align: center; font-size: 11px; margin-bottom: 8px;">
        data-surface="stage" (Preview Stage Iframe)
      </div>
      <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 8px 10px; border-radius: 4px; font-family: monospace; font-size: 11px; color: #334155;">
        {% verbatim %}{% dds__button label="Submit" %}{% endverbatim %}
      </div>
    </div>

    <!-- Maximal Usage Block -->
    <div style="border: 1px dashed #0369a1; background: #ffffff; border-radius: 6px; padding: 12px;">
      <h3 style="margin: 0 0 6px 0; font-size: 13px; color: #0f172a;">Maximal Example</h3>
      <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 8px 10px; border-radius: 4px; font-family: monospace; font-size: 11px; color: #334155;">
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
