# Areas & Token Delegation

This document explains how gallery area templates create contextual UI zones and how the **Three-Tier Token Delegation Cascade** allows components to adapt automatically across light, dark, and inverted surfaces without custom classes or variants.

---

## 1. Gallery Areas & Named Surfaces

The gallery UI is partitioned into distinct structural regions known as **Areas**. Each area declares a semantic `[data-surface='<name>']` attribute on its container element:

```html
<!-- Gallery Topbar Area -->
<header class="dds-topbar" data-surface="topbar"> ... </header>

<!-- Gallery Sidebar Area (Inverted Dark Theme) -->
<aside class="dds-sidebar" data-surface="sidebar"> ... </aside>

<!-- Documentation Pane Area -->
<section class="dds-docs-pane" data-surface="docs"> ... </section>

<!-- Interactive Sandbox Stage Area -->
<div class="dds-stage-area" data-surface="stage"> ... </div>
```

### Supported Named Surfaces

| Named Surface | Typical Elevation Layer | Visual Character |
| :--- | :--- | :--- |
| **`topbar`** | Raised (`10`) | Sticky header with subtle border and elevation shadow |
| **`sidebar`** | Raised (`10`) | Navigation drawer; **dark in light mode** for visual focus |
| **`docs`** | Base (`1`) | Crisp, high-readability documentation surface |
| **`sandbox`** | Base (`1`) | Interactive workbench surface for component tuning |
| **`stage`** | Sunken (`0`) | Recessed letterbox backdrop framing component previews |
| **`code`** | Sunken (`0`) | Syntax-highlighted code container; **dark in light mode** |
| **`popout`** | Floating (`20`) | Menus, dropdown options, and search result popovers |
| **`overlay`** | Overlay (`30`) | Modal dialogs, floating panels, and mobile drawer scrims |

---

## 2. The Token Delegation Cascade

Instead of hardcoding dark or light variants into components, the design system leverages **CSS custom property inheritance**:

```text
Tier 2 Defaults (:root)
  ├── Standard Area ([data-surface='docs'])
  │     └── Inherits :root defaults (Light Palette)
  │           └── Child Component (.dds-button, .dds-badge)
  │
  └── Inverted Area ([data-surface='sidebar'])
        └── Contextual Remapping:
              --dds-surface-bg-color: var(--dds-surface-sidebar-bg-color)
              --dds-text-default-color: var(--dds-surface-sidebar-text-default-color)
              └── Child Component (.dds-button, .dds-badge) renders dark palette automatically!
```

### Contextual Surface Remapping in `tokens.css`

Inside `tokens.css`, when a surface container declares `[data-surface='sidebar']`, it remaps the active Tier 2 tokens for its entire subtree:

```css
[data-surface='sidebar'] {
  /* Surface background & borders */
  --dds-surface-bg-color: var(--dds-surface-sidebar-bg-color);
  --dds-surface-border-color: var(--dds-surface-sidebar-border-color);

  /* Typography */
  --dds-text-default-color: var(--dds-surface-sidebar-text-default-color);
  --dds-text-muted-color: var(--dds-surface-sidebar-text-muted-color);
  --dds-text-prominent-color: var(--dds-surface-sidebar-text-prominent-color);

  /* Interactive States */
  --dds-state-interactive-text-color: var(--dds-surface-sidebar-state-interactive-text-color);
  --dds-state-hover-bg-color: var(--dds-surface-sidebar-state-hover-bg-color);
  --dds-state-hover-text-color: var(--dds-surface-sidebar-text-prominent-color);
  --dds-state-active-bg-color: var(--dds-surface-sidebar-state-active-bg-color);
  --dds-state-selected-bg-color: var(--dds-surface-sidebar-state-selected-bg-color);
}
```

---

## 3. Live Demonstration: Automatic Surface Adaptation

The example below demonstrates the power of token delegation. The exact same components (`dds__badge`, `dds__button`, standard text) are rendered inside a default `[data-surface='docs']` box and an inverted `[data-surface='sidebar']` box. **No modifier classes or CSS overrides are used on the components**:

```canvas
<l-grid style="--min: 240px; --space: var(--dds-space-lg);">
  <!-- Standard Docs Surface -->
  <div data-surface="docs" style="background-color: var(--dds-surface-bg-color); color: var(--dds-text-default-color); border: 1px solid var(--dds-surface-border-color); border-radius: var(--dds-surface-border-radius); padding: var(--dds-space-lg);">
    <l-stack style="--space: var(--dds-space-md);">
      <div>
        <strong style="color: var(--dds-text-prominent-color); font-size: var(--dds-text-heading-size);">Docs Surface</strong>
        <p style="color: var(--dds-text-muted-color); font-size: var(--dds-text-caption-size); margin: var(--dds-space-3xs) 0 0 0;">
          Standard high-contrast reading surface.
        </p>
      </div>
      <l-cluster style="--space: var(--dds-space-xs);">
        {% dds__badge variant="neutral" label="Neutral" %}
        {% dds__badge variant="info" label="Info" %}
        {% dds__badge variant="success" label="Success" %}
      </l-cluster>
      <div>
        {% dds__button label="Action Button" variant="primary" %}
      </div>
    </l-stack>
  </div>

  <!-- Inverted Sidebar Surface -->
  <div data-surface="sidebar" style="background-color: var(--dds-surface-bg-color); color: var(--dds-text-default-color); border: 1px solid var(--dds-surface-border-color); border-radius: var(--dds-surface-border-radius); padding: var(--dds-space-lg);">
    <l-stack style="--space: var(--dds-space-md);">
      <div>
        <strong style="color: var(--dds-text-prominent-color); font-size: var(--dds-text-heading-size);">Sidebar Surface</strong>
        <p style="color: var(--dds-text-muted-color); font-size: var(--dds-text-caption-size); margin: var(--dds-space-3xs) 0 0 0;">
          Inverted dark palette active even in light mode.
        </p>
      </div>
      <l-cluster style="--space: var(--dds-space-xs);">
        {% dds__badge variant="neutral" label="Neutral" %}
        {% dds__badge variant="info" label="Info" %}
        {% dds__badge variant="success" label="Success" %}
      </l-cluster>
      <div>
        {% dds__button label="Action Button" variant="primary" %}
      </div>
    </l-stack>
  </div>
</l-grid>
```
