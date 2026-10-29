# Typography & Spacing System

This document specifies the typography and spacing foundations of the design system, outlining their token hierarchies, purpose mappings, and live visual specimens.

---

## 1. Typography Architecture

Typography in the design system is decoupled into **font purposes**, **semantic text roles**, and **contrast prominence levels**.

### Font Purposes (`--dds-font-*`)

The design system declares three purpose-driven font stacks in `@layer tokens`:

- **`--dds-font-ui`**: Modern system sans-serif stack (`-apple-system, blinkmacsystemfont, 'segoe ui', roboto, 'helvetica neue', arial, sans-serif`) optimized for user interfaces, buttons, toolbars, and navigation trees.
- **`--dds-font-prose`**: Editorial sans-serif stack tuned for documentation reading and long-form articles.
- **`--dds-font-technical`**: Monospace stack (`sfmono-regular, menlo, monaco, consolas, 'liberation mono', monospace`) for code snippets, token definitions, parameters, and keyboard shortcuts.

### Typographic Text Roles (`--dds-text-<role>-*`)

Every text role defines five coordinated properties: `font`, `size`, `line-height`, `weight`, and `letter-spacing`:

| Role | Token Example | Size (Rem / Px) | Weight | Line Height |
| :--- | :--- | :--- | :--- | :--- |
| **`title`** | `--dds-text-title-size` | `1.75rem` (28px) | `700` (Bold) | `1.25` (Tight) |
| **`heading`** | `--dds-text-heading-size` | `1.375rem` (22px) | `600` (Semibold) | `1.375` (Snug) |
| **`subheading`** | `--dds-text-subheading-size` | `1.125rem` (18px) | `600` (Semibold) | `1.375` (Snug) |
| **`body`** | `--dds-text-body-size` | `1.0rem` (16px) | `400` (Regular) | `1.5` (Normal) |
| **`prose`** | `--dds-text-prose-size` | `1.0rem` (16px) | `400` (Regular) | `1.65` (Relaxed) |
| **`control`** | `--dds-text-control-size` | `0.875rem` (14px) | `500` (Medium) | `1.375` (Snug) |
| **`caption`** | `--dds-text-caption-size` | `0.8125rem` (13px) | `400` (Regular) | `1.375` (Snug) |
| **`overline`** | `--dds-text-overline-size` | `0.75rem` (12px) | `600` (Semibold) | `1.25` (Tight, `0.08em` tracking) |
| **`code`** | `--dds-text-code-size` | `0.8125rem` (13px) | `400` (Mono) | `1.375` (Snug) |

### Contrast Prominence Levels

- `--dds-text-prominent-color`: High-contrast headers, active labels, and emphasis.
- `--dds-text-default-color`: Standard body copy, readable against surface backgrounds.
- `--dds-text-muted-color`: Secondary metadata, timestamps, and subtle hints.

### Rendered Typography Specimen

```canvas
<l-stack style="--space: var(--dds-space-lg);">
  <div>
    <span style="font-size: var(--dds-text-overline-size); font-weight: var(--_dds-font-weight-semibold); letter-spacing: var(--_dds-tracking-wider); text-transform: uppercase; color: var(--dds-text-muted-color);">Title (28px / 1.75rem)</span>
    <h1 style="font-size: var(--dds-text-title-size); line-height: var(--_dds-leading-tight); font-weight: var(--_dds-font-weight-bold); color: var(--dds-text-prominent-color); margin: 0;">
      Design Systems for Modern Django
    </h1>
  </div>

  <div>
    <span style="font-size: var(--dds-text-overline-size); font-weight: var(--_dds-font-weight-semibold); letter-spacing: var(--_dds-tracking-wider); text-transform: uppercase; color: var(--dds-text-muted-color);">Heading (22px / 1.375rem)</span>
    <h2 style="font-size: var(--dds-text-heading-size); line-height: var(--_dds-leading-snug); font-weight: var(--_dds-font-weight-semibold); color: var(--dds-text-prominent-color); margin: 0;">
      Component Boundaries and Encapsulation
    </h2>
  </div>

  <div>
    <span style="font-size: var(--dds-text-overline-size); font-weight: var(--_dds-font-weight-semibold); letter-spacing: var(--_dds-tracking-wider); text-transform: uppercase; color: var(--dds-text-muted-color);">Subheading (18px / 1.125rem)</span>
    <h3 style="font-size: var(--dds-text-subheading-size); line-height: var(--_dds-leading-snug); font-weight: var(--_dds-font-weight-semibold); color: var(--dds-text-prominent-color); margin: 0;">
      Zero Leakage with CUBE CSS Cascade Layers
    </h3>
  </div>

  <div>
    <span style="font-size: var(--dds-text-overline-size); font-weight: var(--_dds-font-weight-semibold); letter-spacing: var(--_dds-tracking-wider); text-transform: uppercase; color: var(--dds-text-muted-color);">Body (16px / 1rem) &amp; Code (13px)</span>
    <p style="font-size: var(--dds-text-body-size); line-height: var(--_dds-leading-normal); color: var(--dds-text-default-color); margin: 0;">
      Components must never set external margins on their root element. External spatial rhythm is the exclusive responsibility of Every Layout primitives like <code style="font-size: var(--dds-text-code-size); background-color: var(--dds-control-bg-color); border: 1px solid var(--dds-control-border-color); padding: 2px 4px; border-radius: 4px;">&lt;l-stack&gt;</code> and <code style="font-size: var(--dds-text-code-size); background-color: var(--dds-control-bg-color); border: 1px solid var(--dds-control-border-color); padding: 2px 4px; border-radius: 4px;">&lt;l-cluster&gt;</code>.
    </p>
  </div>

  <div>
    <span style="font-size: var(--dds-text-overline-size); font-weight: var(--_dds-font-weight-semibold); letter-spacing: var(--_dds-tracking-wider); text-transform: uppercase; color: var(--dds-text-muted-color);">Control (14px) &amp; Caption (13px)</span>
    <l-cluster style="--space: var(--dds-space-md);" align="center">
      {% dds__button label="Save Preference" variant="primary" size="sm" %}
      <span style="font-size: var(--dds-text-caption-size); color: var(--dds-text-muted-color);">Changes are automatically persisted to localStorage.</span>
    </l-cluster>
  </div>
</l-stack>
```

---

## 2. Spacing Architecture

Spacing is governed by an 8-point modular scale, complemented by semantic gap roles, inset presets, and layout constraints.

### The Modular Scale (`--dds-space-*`)

| Token | Value (Rem) | Pixel Value | Typical Application |
| :--- | :--- | :--- | :--- |
| **`--dds-space-3xs`** | `0.125rem` | 2px | Micro-hairline spacing, badge borders, outline offsets |
| **`--dds-space-2xs`** | `0.25rem` | 4px | Icon-to-text spacing, tight chips, tag padding |
| **`--dds-space-xs`** | `0.375rem` | 6px | Control internal padding, button compact gaps |
| **`--dds-space-sm`** | `0.5rem` | 8px | Standard control padding, compact insets |
| **`--dds-space-md`** | `0.75rem` | 12px | Default layout gap (`--dds-space-gap-default`) |
| **`--dds-space-lg`** | `1.0rem` | 16px | Default card inset (`--dds-space-inset-default`) |
| **`--dds-space-xl`** | `1.5rem` | 24px | Major group separation, card grid gutters |
| **`--dds-space-2xl`** | `2.0rem` | 32px | Section gap (`--dds-space-gap-section`), page margins |
| **`--dds-space-3xl`** | `3.0rem` | 48px | Hero containers, spacious layout dividers |

### Semantic Spacing Roles

- **Gaps (`--dds-space-gap-*`)**:
  - `tight` (`xs` / 6px): Clustered tags, breadcrumb items, segmented controls.
  - `default` (`md` / 12px): Standard form fields, sidebar links, toolbar items.
  - `section` (`2xl` / 32px): Major documentation sections and workbench panels.
- **Insets (`--dds-space-inset-*`)**:
  - `compact` (`sm` / 8px): Table cells, dropdown menu items.
  - `default` (`lg` / 16px): Card surfaces, preview widgets, modal dialogs.
  - `page` (`2xl` / 32px): Outer documentation container margins.
- **Layout Constraints**:
  - `--dds-layout-prose-measure`: `65ch` (optimal line length for readable documentation prose).
  - `--dds-layout-sidebar-width`: `16.25rem` (260px standard navigation drawer width).

### Rendered Spacing Visualizer

```canvas
<l-stack style="--space: var(--dds-space-sm);">
  <l-cluster style="--space: var(--dds-space-sm);" align="center">
    <div style="width: 80px; font-size: var(--dds-text-caption-size); color: var(--dds-text-muted-color);">3xs (2px)</div>
    <div style="height: 20px; width: var(--dds-space-3xs); background-color: var(--dds-control-accent-color); border-radius: 2px;"></div>
  </l-cluster>

  <l-cluster style="--space: var(--dds-space-sm);" align="center">
    <div style="width: 80px; font-size: var(--dds-text-caption-size); color: var(--dds-text-muted-color);">2xs (4px)</div>
    <div style="height: 20px; width: var(--dds-space-2xs); background-color: var(--dds-control-accent-color); border-radius: 2px;"></div>
  </l-cluster>

  <l-cluster style="--space: var(--dds-space-sm);" align="center">
    <div style="width: 80px; font-size: var(--dds-text-caption-size); color: var(--dds-text-muted-color);">xs (6px)</div>
    <div style="height: 20px; width: var(--dds-space-xs); background-color: var(--dds-control-accent-color); border-radius: 2px;"></div>
  </l-cluster>

  <l-cluster style="--space: var(--dds-space-sm);" align="center">
    <div style="width: 80px; font-size: var(--dds-text-caption-size); color: var(--dds-text-muted-color);">sm (8px)</div>
    <div style="height: 20px; width: var(--dds-space-sm); background-color: var(--dds-control-accent-color); border-radius: 2px;"></div>
  </l-cluster>

  <l-cluster style="--space: var(--dds-space-sm);" align="center">
    <div style="width: 80px; font-size: var(--dds-text-caption-size); color: var(--dds-text-muted-color);">md (12px)</div>
    <div style="height: 20px; width: var(--dds-space-md); background-color: var(--dds-control-accent-color); border-radius: 2px;"></div>
  </l-cluster>

  <l-cluster style="--space: var(--dds-space-sm);" align="center">
    <div style="width: 80px; font-size: var(--dds-text-caption-size); color: var(--dds-text-muted-color);">lg (16px)</div>
    <div style="height: 20px; width: var(--dds-space-lg); background-color: var(--dds-control-accent-color); border-radius: 2px;"></div>
  </l-cluster>

  <l-cluster style="--space: var(--dds-space-sm);" align="center">
    <div style="width: 80px; font-size: var(--dds-text-caption-size); color: var(--dds-text-muted-color);">xl (24px)</div>
    <div style="height: 20px; width: var(--dds-space-xl); background-color: var(--dds-control-accent-color); border-radius: 2px;"></div>
  </l-cluster>

  <l-cluster style="--space: var(--dds-space-sm);" align="center">
    <div style="width: 80px; font-size: var(--dds-text-caption-size); color: var(--dds-text-muted-color);">2xl (32px)</div>
    <div style="height: 20px; width: var(--dds-space-2xl); background-color: var(--dds-control-accent-color); border-radius: 2px;"></div>
  </l-cluster>

  <l-cluster style="--space: var(--dds-space-sm);" align="center">
    <div style="width: 80px; font-size: var(--dds-text-caption-size); color: var(--dds-text-muted-color);">3xl (48px)</div>
    <div style="height: 20px; width: var(--dds-space-3xl); background-color: var(--dds-control-accent-color); border-radius: 2px;"></div>
  </l-cluster>
</l-stack>
```
