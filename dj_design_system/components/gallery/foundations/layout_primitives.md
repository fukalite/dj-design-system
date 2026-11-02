---
order: 3
---
# Layout Primitives (Every Layout)

This document details the 11 intrinsic **Every Layout** composition primitives in `@layer composition`. These primitives govern all layout, flow, and spatial rhythm across the gallery and components.

---

## 1. The Every Layout Philosophy

Modern component libraries frequently suffer from two common anti-patterns:
1. **Margin Leakage**: Components declaring external margins (`margin-bottom: 1rem`), making them brittle and context-dependent.
2. **Brittle Media Queries**: Layouts hardcoding fixed viewport breakpoints (`@media (min-width: 768px)`), ignoring the actual width of the component's container.

The design system resolves both issues using **Every Layout**:
- **Zero Component Margins**: All component roots enforce `margin: 0`. A component never dictates the space around itself; it adapts to fill whatever space its parent provides.
- **Intrinsic Web Design**: Layouts adapt dynamically to the content and the container's inline size using CSS Flexbox, Grid, `clamp()`, and `calc()`.
- **Cascade Layer**: Defined in `@layer composition` between `global` and `blocks`, ensuring layout styles can be refined by component themes without specificity wars.

---

## 2. The 11 Layout Primitives

Primitives can be written as custom elements (`<l-*>`) or semantic HTML tags with matching utility classes (`.l-*`):

| Primitive | Tag / Class | Primary Control Variables | Purpose |
| :--- | :--- | :--- | :--- |
| **Stack** | `<l-stack>` / `.l-stack` | `--space` (default: `--dds-space-gap-default`) | Vertical flow rhythm with automatic margin collapse |
| **Cluster** | `<l-cluster>` / `.l-cluster` | `--space`, `--align`, `--justify` | Wrapping horizontal items (toolbars, tags, badges) |
| **Sidebar** | `<l-sidebar>` / `.l-sidebar` | `--side-width`, `--content-min`, `--space` | Intrinsic sidebar with flexible main content split |
| **Switcher** | `<l-switcher>` / `.l-switcher` | `--measure`, `--space` | Container-responsive row-to-column switching |
| **Box** | `<l-box>` / `.l-box` | `--space` | Padded, bordered surface container |
| **Center** | `<l-center>` / `.l-center` | `--measure`, `--space` | Horizontally centered prose container (max `65ch`) |
| **Cover** | `<l-cover>` / `.l-cover` | `--min-height`, `--space` | Vertically centered hero or empty-state layout |
| **Frame** | `<l-frame>` / `.l-frame` | `--n`, `--d` (aspect ratio `n/d`) | Cropped aspect-ratio container for media |
| **Grid** | `<l-grid>` / `.l-grid` | `--min`, `--space` | Auto-fit responsive card grid without media queries |
| **Reel** | `<l-reel>` / `.l-reel` | `--space`, `--item-width` | Horizontal scrolling track for overflow items |
| **Imposter** | `<l-imposter>` / `.l-imposter`| `--margin`, `[data-fixed]` | Perfectly centered overlay or modal dialog |

---

## 3. Core Primitives in Action

### Stack (`<l-stack>`)

The Stack primitive injects consistent vertical rhythm between sibling elements without applying top margins to the first child or bottom margins to the last child:

```canvas
<l-box style="--space: var(--dds-space-md); max-width: 400px;">
  <l-stack style="--space: var(--dds-space-sm);">
    <h3 style="margin: 0; font-size: var(--dds-text-heading-size); color: var(--dds-text-prominent-color);">Stack Layout</h3>
    <p style="margin: 0; font-size: var(--dds-text-body-size); color: var(--dds-text-default-color);">
      Direct children automatically receive consistent spacing via <code style="font-size: var(--dds-text-code-size);">--space</code>.
    </p>
    <l-cluster style="--space: var(--dds-space-xs);">
      {% dds__badge variant="info" label="Item 1" %}
      {% dds__badge variant="success" label="Item 2" %}
      {% dds__badge variant="warning" label="Item 3" %}
    </l-cluster>
  </l-stack>
</l-box>
```

---

### Cluster (`<l-cluster>`)

The Cluster primitive groups elements horizontally, wrapping them onto new lines as needed while maintaining vertical and horizontal alignment:

```canvas
<l-cluster style="--space: var(--dds-space-sm);" align="center">
  {% dds__button label="Primary Action" variant="primary" %}
  {% dds__button label="Secondary Action" variant="ghost" %}
  {% dds__button label="Danger" variant="danger" %}
  <span style="font-size: var(--dds-text-caption-size); color: var(--dds-text-muted-color);">Automatically wraps on narrow viewports</span>
</l-cluster>
```

---

### Grid (`<l-grid>`)

The Grid primitive creates an auto-fit card grid using CSS `repeat(auto-fit, minmax(min(var(--min), 100%), 1fr))`. Cards automatically flow into fewer columns as the container narrows without any media queries:

```canvas
<l-grid style="--min: 160px; --space: var(--dds-space-md);">
  <l-box style="--space: var(--dds-space-sm);">
    <strong style="font-size: var(--dds-text-body-size);">Card A</strong>
    <p style="font-size: var(--dds-text-caption-size); color: var(--dds-text-muted-color); margin: var(--dds-space-3xs) 0 0 0;">Auto-fitting column</p>
  </l-box>
  <l-box style="--space: var(--dds-space-sm);">
    <strong style="font-size: var(--dds-text-body-size);">Card B</strong>
    <p style="font-size: var(--dds-text-caption-size); color: var(--dds-text-muted-color); margin: var(--dds-space-3xs) 0 0 0;">Auto-fitting column</p>
  </l-box>
  <l-box style="--space: var(--dds-space-sm);">
    <strong style="font-size: var(--dds-text-body-size);">Card C</strong>
    <p style="font-size: var(--dds-text-caption-size); color: var(--dds-text-muted-color); margin: var(--dds-space-3xs) 0 0 0;">Auto-fitting column</p>
  </l-box>
  <l-box style="--space: var(--dds-space-sm);">
    <strong style="font-size: var(--dds-text-body-size);">Card D</strong>
    <p style="font-size: var(--dds-text-caption-size); color: var(--dds-text-muted-color); margin: var(--dds-space-3xs) 0 0 0;">Auto-fitting column</p>
  </l-box>
</l-grid>
```

---

### Sidebar (`<l-sidebar>`)

The Sidebar primitive places a fixed-basis sidebar alongside a flexible main content container. When the container width shrinks below the sum of `--side-width` and `--content-min`, the elements cleanly stack into a single column:

```canvas
<l-sidebar style="--side-width: 140px; --content-min: 50%; --space: var(--dds-space-md);">
  <l-box style="--space: var(--dds-space-sm); background-color: var(--dds-state-hover-bg-color);">
    <strong>Sidebar</strong>
    <p style="font-size: var(--dds-text-caption-size); margin: var(--dds-space-3xs) 0 0 0;">Fixed Basis</p>
  </l-box>
  <l-box style="--space: var(--dds-space-sm);">
    <strong>Main Content Area</strong>
    <p style="font-size: var(--dds-text-caption-size); margin: var(--dds-space-3xs) 0 0 0;">Expands to fill available width, or stacks when compressed.</p>
  </l-box>
</l-sidebar>
```
