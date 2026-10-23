# Semantic Tokens & Naming Scheme

This document details the Three-Tier Design Token System, explains the naming grammar, breaks down each semantic domain, and provides live rendered visual demonstrations.

---

## 1. The Three-Tier Token Hierarchy

The design system enforces a strict 3-tier token hierarchy that decouples raw colour values from semantic intent and component styling:

```text
Tier 1: Primitives (:root)
  └── Private raw literals (--_dds-blue-600, --_dds-space-md)
        │ (mapped directly in tokens.css)
        ▼
Tier 2: Semantic Tokens (:root)
  └── Public theming API (--dds-status-info-text-color, --dds-surface-bg-color)
        │ (contextually remapped by [data-surface='...'])
        ▼
Tier 3: Component-Scoped Tokens (.dds-component)
  └── Component-local variables (--_badge-bg-color, --_button-border-radius)
```

### Tier 1: Literal Primitives (Private, `:root` only)
- **Format:** `--_dds-<palette-or-scale>-<step>` (leading `_` denotes internal private).
- **Rule:** Defined exclusively on `:root` inside `tokens.css`. Never referenced outside `tokens.css`.
- **Examples:** `--_dds-blue-600: #4263eb;`, `--_dds-space-md: 0.75rem;`, `--_dds-radius-md: 6px;`.

### Tier 2: Semantic Tokens (Public Theming API)
- **Format:** `--dds-<domain>-<role>-<property>` or `--dds-<domain>-<property>`.
- **Rule:** Defined on `:root` (and inverted for dark mode). Represents meaningful design intent. All components and surface selectors reference Tier 2 tokens.
- **Examples:** `--dds-status-info-bg-color`, `--dds-surface-border-color`, `--dds-control-accent-color`.

### Tier 3: Component-Scoped Tokens (Private, Component Root)
- **Format:** `--_<component>-<property>` (leading `_` denotes component-local privacy).
- **Rule:** Declared at the top of a component's `<name>.css` on the root selector (`.dds-<name>` or `dds-<name>`). Every Tier 3 token maps directly from a Tier 2 token.
- **Example:**
  ```css
  .dds-badge {
    --_badge-bg-color: var(--dds-surface-bg-color);
    --_badge-text-color: var(--dds-text-default-color);
    --_badge-border-radius: var(--dds-surface-border-radius);
    
    background-color: var(--_badge-bg-color);
    color: var(--_badge-text-color);
    border-radius: var(--_badge-border-radius);
  }
  ```

---

## 2. Token Naming Grammar

Semantic tokens follow an outcome-oriented, predictable grammar:

$$\text{--dds-} \underbrace{\text{<domain>}}_{\text{Context}} \text{-} \underbrace{\text{<role>}}_{\text{Intent}} \text{-} \underbrace{\text{<property>}}_{\text{CSS Attribute}} \text{-} \underbrace{\text{<variant>}}_{\text{Modifier (optional)}}$$

- **`<domain>`**: High-level semantic territory (`surface`, `layer`, `text`, `space`, `state`, `control`, `status`, `font`, `layout`).
- **`<role>`**: Specific semantic function or level (`info`, `success`, `hover`, `active`, `sidebar`, `topbar`).
- **`<property>`**: Physical CSS attribute affected (`bg-color`, `border-color`, `border-radius`, `shadow-shape`, `z-index`, `font-size`).
- **`<variant>`**: Optional modifier (`default`, `compact`, `tight`, `section`).

---

## 3. Semantic Domains & Visual Demonstrations

### Domain 1: Status & Feedback Tokens (`--dds-status-*`)

Status tokens provide uniform styling for system alerts, feedback banners, and badges across four semantic levels: `info`, `success`, `warning`, and `error`. Each status defines matching text, background, border, and shadow tokens.

```canvas
<l-stack style="--space: var(--dds-space-md);">
  <l-box style="--space: var(--dds-space-md); background-color: var(--dds-status-info-bg-color); border-color: var(--dds-status-info-border-color); color: var(--dds-status-info-text-color); border-radius: var(--dds-status-info-border-radius);">
    <l-cluster style="--space: var(--dds-space-sm);" align="center">
      {% dds__icon name="info" size="md" %}
      <l-stack style="--space: var(--dds-space-3xs);">
        <strong>Information Notice (<code>--dds-status-info-*</code>)</strong>
        <span style="font-size: var(--dds-text-caption-size);">Used for passive updates, guidance, and non-blocking notifications.</span>
      </l-stack>
    </l-cluster>
  </l-box>

  <l-box style="--space: var(--dds-space-md); background-color: var(--dds-status-success-bg-color); border-color: var(--dds-status-success-border-color); color: var(--dds-status-success-text-color); border-radius: var(--dds-status-success-border-radius);">
    <l-cluster style="--space: var(--dds-space-sm);" align="center">
      {% dds__icon name="check" size="md" %}
      <l-stack style="--space: var(--dds-space-3xs);">
        <strong>Success Confirmation (<code>--dds-status-success-*</code>)</strong>
        <span style="font-size: var(--dds-text-caption-size);">Confirms positive actions, saved states, and successful operations.</span>
      </l-stack>
    </l-cluster>
  </l-box>

  <l-box style="--space: var(--dds-space-md); background-color: var(--dds-status-warning-bg-color); border-color: var(--dds-status-warning-border-color); color: var(--dds-status-warning-text-color); border-radius: var(--dds-status-warning-border-radius);">
    <l-cluster style="--space: var(--dds-space-sm);" align="center">
      {% dds__icon name="warning" size="md" %}
      <l-stack style="--space: var(--dds-space-3xs);">
        <strong>Warning Alert (<code>--dds-status-warning-*</code>)</strong>
        <span style="font-size: var(--dds-text-caption-size);">Indicates caution, deprecation, or non-fatal boundary conditions.</span>
      </l-stack>
    </l-cluster>
  </l-box>

  <l-box style="--space: var(--dds-space-md); background-color: var(--dds-status-error-bg-color); border-color: var(--dds-status-error-border-color); color: var(--dds-status-error-text-color); border-radius: var(--dds-status-error-border-radius);">
    <l-cluster style="--space: var(--dds-space-sm);" align="center">
      {% dds__icon name="error" size="md" %}
      <l-stack style="--space: var(--dds-space-3xs);">
        <strong>Critical Error (<code>--dds-status-error-*</code>)</strong>
        <span style="font-size: var(--dds-text-caption-size);">Highlights validation errors, failed requests, and destructive actions.</span>
      </l-stack>
    </l-cluster>
  </l-box>
</l-stack>
```

---

### Domain 2: Interactive States (`--dds-state-*`)

State tokens govern user interaction feedback: `interactive` (resting), `hover`, `focus`, `active` (pressed), `selected`, and `disabled`.

```canvas
<l-grid style="--min: 150px; --space: var(--dds-space-md);">
  <l-box style="--space: var(--dds-space-md); background-color: var(--dds-state-interactive-bg-color); border-color: var(--dds-state-interactive-border-color); color: var(--dds-state-interactive-text-color); text-align: center;">
    <l-stack style="--space: var(--dds-space-xs);" align="center">
      {% dds__icon name="component" size="md" %}
      <strong>Interactive</strong>
      <code style="font-size: var(--dds-text-caption-size);">Resting state</code>
    </l-stack>
  </l-box>

  <l-box style="--space: var(--dds-space-md); background-color: var(--dds-state-hover-bg-color); border-color: var(--dds-state-hover-border-color); color: var(--dds-state-hover-text-color); text-align: center;">
    <l-stack style="--space: var(--dds-space-xs);" align="center">
      {% dds__icon name="component" size="md" %}
      <strong>Hover</strong>
      <code style="font-size: var(--dds-text-caption-size);">Pointer focus</code>
    </l-stack>
  </l-box>

  <l-box style="--space: var(--dds-space-md); background-color: var(--dds-state-selected-bg-color); border-color: var(--dds-state-selected-border-color); color: var(--dds-state-selected-text-color); text-align: center;">
    <l-stack style="--space: var(--dds-space-xs);" align="center">
      {% dds__icon name="check" size="md" %}
      <strong>Selected</strong>
      <code style="font-size: var(--dds-text-caption-size);">Active selection</code>
    </l-stack>
  </l-box>

  <l-box style="--space: var(--dds-space-md); background-color: var(--dds-state-active-bg-color); border-color: var(--dds-state-active-border-color); color: var(--dds-state-active-text-color); text-align: center;">
    <l-stack style="--space: var(--dds-space-xs);" align="center">
      {% dds__icon name="component-variants" size="md" %}
      <strong>Active</strong>
      <code style="font-size: var(--dds-text-caption-size);">Pressed mouse</code>
    </l-stack>
  </l-box>

  <l-box style="--space: var(--dds-space-md); background-color: var(--dds-state-disabled-bg-color); border-color: var(--dds-state-disabled-border-color); color: var(--dds-state-disabled-text-color); opacity: var(--dds-state-disabled-opacity); text-align: center;">
    <l-stack style="--space: var(--dds-space-xs);" align="center">
      {% dds__icon name="close" size="md" %}
      <strong>Disabled</strong>
      <code style="font-size: var(--dds-text-caption-size);">Inactive / locked</code>
    </l-stack>
  </l-box>
</l-grid>
```

---

### Domain 3: Surface & Elevation Layers (`--dds-layer-*` & `--dds-surface-*`)

The elevation scale defines 5 Z-index planes and associated surface styling:

| Layer | Z-Index Token | Typical UI Surface |
| :--- | :--- | :--- |
| **`sunken`** | `--dds-layer-sunken-z-index: 0` | `stage` (recessed canvas), `code` (code panels) |
| **`base`** | `--dds-layer-base-z-index: 1` | `docs` (main documentation), `sandbox` (workbench) |
| **`raised`** | `--dds-layer-raised-z-index: 10` | `topbar` (header bar), `sidebar` (navigation drawer) |
| **`floating`** | `--dds-layer-floating-z-index: 20` | `popout` (menus, dropdowns, tooltips, flyouts) |
| **`overlay`** | `--dds-layer-overlay-z-index: 30` | `overlay` (modal backdrops, dialogs, fullscreen scrim) |

```canvas
<l-cluster style="--space: var(--dds-space-lg);" align="center" justify="center">
  <l-box style="--space: var(--dds-space-md); background-color: var(--dds-surface-bg-color); border-color: var(--dds-surface-border-color); border-radius: var(--dds-surface-border-radius); box-shadow: var(--_dds-shadow-shape-sm) var(--dds-surface-shadow-color); min-width: 140px; text-align: center;">
    <strong>Base (1)</strong>
    <p style="font-size: var(--dds-text-caption-size); color: var(--dds-text-muted-color); margin: var(--dds-space-3xs) 0 0 0;">Subtle Shadow</p>
  </l-box>

  <l-box style="--space: var(--dds-space-md); background-color: var(--dds-surface-bg-color); border-color: var(--dds-surface-border-color); border-radius: var(--dds-surface-border-radius); box-shadow: var(--_dds-shadow-shape-md) var(--dds-surface-shadow-color); min-width: 140px; text-align: center;">
    <strong>Raised (10)</strong>
    <p style="font-size: var(--dds-text-caption-size); color: var(--dds-text-muted-color); margin: var(--dds-space-3xs) 0 0 0;">Medium Shadow</p>
  </l-box>

  <l-box style="--space: var(--dds-space-md); background-color: var(--dds-surface-bg-color); border-color: var(--dds-surface-border-color); border-radius: var(--dds-surface-border-radius); box-shadow: var(--_dds-shadow-shape-lg) var(--dds-surface-shadow-color); min-width: 140px; text-align: center;">
    <strong>Floating (20)</strong>
    <p style="font-size: var(--dds-text-caption-size); color: var(--dds-text-muted-color); margin: var(--dds-space-3xs) 0 0 0;">High Elevation</p>
  </l-box>
</l-cluster>
```

---

### Domain 4: Control Tokens (`--dds-control-*`)

Control tokens standardize interactive inputs, text fields, checkboxes, and select menus:

- `--dds-control-bg-color`: Form input background.
- `--dds-control-border-color`: Input boundary outline.
- `--dds-control-border-radius`: Standard control curvature.
- `--dds-control-accent-color`: Focused accent highlight.

```canvas
<l-stack style="--space: var(--dds-space-md);">
  <l-cluster style="--space: var(--dds-space-md);" align="center">
    <input type="text" placeholder="Standard text input" style="background-color: var(--dds-control-bg-color); border: var(--dds-control-border-width) var(--dds-control-border-style) var(--dds-control-border-color); border-radius: var(--dds-control-border-radius); padding: var(--dds-space-xs) var(--dds-space-sm); font-size: var(--dds-text-body-size); color: var(--dds-text-default-color);" />
    {% dds__button label="Submit Action" variant="primary" %}
    {% dds__button label="Cancel" variant="ghost" %}
  </l-cluster>
</l-stack>
```
