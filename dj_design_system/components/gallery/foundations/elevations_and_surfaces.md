# Elevations & Surfaces

This document details the depth architecture, stacking layers, shadow geometry, and contextual surface delegation system that govern spatial hierarchy across the design system.

---

## 1. Architectural Philosophy

The design system models spatial depth through two decoupled concepts:

1. **Elevations & Stacking Layers**: Stacking order (`z-index`) and lighting geometry (`box-shadow`) that establish physical distance from the canvas base.
2. **Contextual Surfaces (`[data-surface]`)**: Boundary containers that declare a semantic zone (such as `sidebar`, `code`, or `popout`) and dynamically remap semantic tokens for all descendant components.

```text
┌────────────────────────────────────────────────────────┐
│  Layer: Overlay (z: 30)   [data-surface="overlay"]     │
│  ├── Modal Scrims & Mobile Drawers                     │
│  └── Maximum elevation shadow (--_dds-shadow-shape-xl) │
└─────────────────────────┬──────────────────────────────┘
                          │
┌─────────────────────────▼──────────────────────────────┐
│  Layer: Floating (z: 20)  [data-surface="popout"]      │
│  ├── Dropdown Menus, Combobox Lists & Tooltips         │
│  └── High elevation shadow (--_dds-shadow-shape-lg)    │
└─────────────────────────┬──────────────────────────────┘
                          │
┌─────────────────────────▼──────────────────────────────┐
│  Layer: Raised (z: 10)    [data-surface="topbar|sidebar"]
│  ├── Sticky Headers, Workbenches & Navigation Drawers  │
│  └── Low elevation shadow (--_dds-shadow-shape-sm)     │
└─────────────────────────┬──────────────────────────────┘
                          │
┌─────────────────────────▼──────────────────────────────┐
│  Layer: Base (z: 1)       [data-surface="docs|sandbox"]│
│  ├── Main Document Flow, Reading Panes & Forms         │
│  └── Flush / Zero shadow (--_dds-shadow-shape-none)    │
└─────────────────────────┬──────────────────────────────┘
                          │
┌─────────────────────────▼──────────────────────────────┐
│  Layer: Sunken (z: -1)    [data-surface="stage|code"]  │
│  ├── Sandboxed Preview Viewports & Code Insets         │
│  └── Recessed borders & dashed containment             │
└────────────────────────────────────────────────────────┘
```

---

## 2. The 5 Layer Stacking Tiers

Stacking contexts in the design system are governed strictly by Tier 2 layer tokens. Arbitrary `z-index` integers are prohibited in stylesheets.

| Layer Tier | Token | Value | Primary Role |
| :--- | :--- | :--- | :--- |
| **Sunken** | `--dds-layer-sunken-z-index` | `-1` | Recessed backgrounds, sandboxed canvas iframes, embedded code viewports |
| **Base** | `--dds-layer-base-z-index` | `1` | Natural document flow, reading surfaces, primary page content |
| **Raised** | `--dds-layer-raised-z-index` | `10` | Sticky topbars, persistent sidebars, fixed navigation bars |
| **Floating** | `--dds-layer-floating-z-index` | `20` | Dropdown menus, popout option pickers, autocomplete flyouts |
| **Overlay** | `--dds-layer-overlay-z-index` | `30` | Modal dialog backdrops, fullscreen mobile drawer sheets |

---

## 3. Shadow Geometry & Lighting Model

Elevation depth is rendered via compound shadows split into two distinct Tier 2 design tokens:

$$\text{box-shadow:} \underbrace{\text{var(--dds-surface-*-shadow-shape)}}_{\text{Geometry \& Offset}} \quad \underbrace{\text{var(--dds-surface-*-shadow-color)}}_{\text{Alpha \& Colour}}$$

### Why Shape and Colour Are Decoupled
Decoupling the spatial shape from the colour enables light and dark themes to preserve identical optical physics whilst altering alpha tinting. In light mode, shadows utilise dark neutral alphas (`--_dds-alpha-dark-100` to `300`). In dark mode, shadows intensify or adopt tinted backdrops without altering elevation curves.

| Elevation Step | Shape Token | Geometry Offsets | Usage |
| :--- | :--- | :--- | :--- |
| **Inset** | `--_dds-shadow-shape-inset-sm` | `inset 0 2px 4px 0` | Sunken surfaces, embedded code blocks, input recesses |
| **Flush** | `--_dds-shadow-shape-none` | `0 0 0` | Flat document surfaces |
| **Low** | `--_dds-shadow-shape-sm` | `0 1px 2px 0` | Cards, buttons, resting sidebar borders, preview stage panes |
| **Medium** | `--_dds-shadow-shape-md` | `0 4px 12px -2px` | Hover elevations, active cards |
| **High** | `--_dds-shadow-shape-lg` | `0 4px 20px 0` | Popouts, floating toolbars, select menus |
| **Maximum** | `--_dds-shadow-shape-xl` | `0 20px 32px -8px` | Modal dialogs, drawer sheets, popovers |

---

## 4. Live Elevation & Shadow Visualisation

```canvas
<l-grid style="--min: 150px; --space: var(--dds-space-lg); padding: var(--dds-space-xl); background: var(--dds-surface-bg-color); border: 1px solid var(--dds-surface-border-color); border-radius: var(--dds-radius-lg);">
  <!-- Elevation 0: Sunken / Flush -->
  <l-box style="--space: var(--dds-space-md); background: var(--dds-surface-stage-bg-color); border: 1px dashed var(--dds-surface-stage-border-color); border-radius: var(--dds-radius-md);">
    <l-stack style="--space: var(--dds-space-2xs); text-align: center;">
      <strong style="font-size: var(--dds-text-body-size); color: var(--dds-text-prominent-color);">Sunken</strong>
      <span style="font-size: var(--dds-text-caption-size); color: var(--dds-text-muted-color);">z: -1 · Flush</span>
    </l-stack>
  </l-box>

  <!-- Elevation 1: Base -->
  <l-box style="--space: var(--dds-space-md); background: var(--dds-surface-docs-bg-color); border: 1px solid var(--dds-surface-docs-border-color); border-radius: var(--dds-radius-md); box-shadow: var(--_dds-shadow-shape-sm) var(--_dds-alpha-dark-100);">
    <l-stack style="--space: var(--dds-space-2xs); text-align: center;">
      <strong style="font-size: var(--dds-text-body-size); color: var(--dds-text-prominent-color);">Base</strong>
      <span style="font-size: var(--dds-text-caption-size); color: var(--dds-text-muted-color);">z: 1 · Low Shadow</span>
    </l-stack>
  </l-box>

  <!-- Elevation 2: Raised -->
  <l-box style="--space: var(--dds-space-md); background: var(--dds-surface-sidebar-bg-color); border: 1px solid var(--dds-surface-sidebar-border-color); border-radius: var(--dds-radius-md); box-shadow: var(--_dds-shadow-shape-md) var(--_dds-alpha-dark-100);">
    <l-stack style="--space: var(--dds-space-2xs); text-align: center;">
      <strong style="font-size: var(--dds-text-body-size); color: var(--dds-text-prominent-color);">Raised</strong>
      <span style="font-size: var(--dds-text-caption-size); color: var(--dds-text-muted-color);">z: 10 · Medium Shadow</span>
    </l-stack>
  </l-box>

  <!-- Elevation 3: Floating -->
  <l-box style="--space: var(--dds-space-md); background: var(--dds-surface-popout-bg-color); border: 1px solid var(--dds-surface-popout-border-color); border-radius: var(--dds-radius-lg); box-shadow: var(--_dds-shadow-shape-lg) var(--_dds-alpha-dark-300);">
    <l-stack style="--space: var(--dds-space-2xs); text-align: center;">
      <strong style="font-size: var(--dds-text-body-size); color: var(--dds-text-prominent-color);">Floating</strong>
      <span style="font-size: var(--dds-text-caption-size); color: var(--dds-text-muted-color);">z: 20 · High Shadow</span>
    </l-stack>
  </l-box>

  <!-- Elevation 4: Overlay -->
  <l-box style="--space: var(--dds-space-md); background: var(--dds-surface-popout-bg-color); border: 1px solid var(--dds-surface-border-color); border-radius: var(--dds-radius-lg); box-shadow: var(--_dds-shadow-shape-xl) var(--_dds-alpha-dark-300);">
    <l-stack style="--space: var(--dds-space-2xs); text-align: center;">
      <strong style="font-size: var(--dds-text-body-size); color: var(--dds-text-prominent-color);">Overlay</strong>
      <span style="font-size: var(--dds-text-caption-size); color: var(--dds-text-muted-color);">z: 30 · Max Shadow</span>
    </l-stack>
  </l-box>
</l-grid>
```

---

## 5. The 8 Semantic Surfaces (`[data-surface]`)

The gallery declares 8 primary surface roles. Declaring `data-surface="<role>"` on an element establishes an isolated visual context where background, borders, blurs, and interactive states are configured:

| Surface Name | `data-surface` | Stacking Tier | Default Appearance | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Docs** | `docs` | Base (`1`) | Neutral surface, no blur, flush | Clean reading canvas for markdown, guides, and specifications |
| **Stage** | `stage` | Sunken (`-1`) | Dashed border, medium outer shadow | Primary preview stage iframe canvas for live component rendering |
| **Code** | `code` | Sunken (`-1`) | Contrast surface, inset sunken shadow, monospace | Code blocks, inspector tabs, and template source viewers |
| **Sidebar** | `sidebar` | Raised (`10`) | Subtle tint, right border, remapped controls | Left navigation tree and quick filter search container |
| **Topbar** | `topbar` | Raised (`10`) | Frosted glass blur, border bottom | Sticky workbench header holding search, theme switcher, and branding |
| **Sandbox** | `sandbox` | Base (`1`) | Solid border, neutral surface | Parameters drawer and interactive property controls |
| **Popout** | `popout` | Floating (`20`) | Rounded `lg`, frosted blur, high shadow | Select dropdowns, context menus, tooltips, and flyout palettes |
| **Overlay** | `overlay` | Overlay (`30`) | Semi-transparent scrim, frosted blur | Modal backdrops and mobile navigation slide-in sheets |

---

## 6. How Contextual Surface Delegation Works

### The Invariant
Components in the design system **never** define variant styles for their parent containers (e.g. `.dds-button--in-sidebar` or `.dds-icon--in-code` are strictly forbidden).

Instead, child components bind their Tier 3 variables to generic Tier 2 tokens:

```css
/* Inside elements/button/button.css */
.dds-button {
  --_button-bg-color: var(--dds-control-bg-color);
  --_button-text-color: var(--dds-text-default-color);
  --_button-hover-bg: var(--dds-state-hover-bg-color);

  background-color: var(--_button-bg-color);
  color: var(--_button-text-color);
}
```

### The Delegation Cascade
When a parent container sets `[data-surface='sidebar']` or `[data-surface='code']`, rules in `tokens/semantic.css` (imported via `tokens.css`) locally reassign the Tier 2 tokens for that entire subtree:

```css
/* Inside tokens/semantic.css */
[data-surface='sidebar'] {
  --dds-control-bg-color: var(--dds-surface-sidebar-state-hover-bg-color);
  --dds-control-border-color: var(--dds-surface-sidebar-border-color);
  --dds-text-default-color: var(--dds-surface-sidebar-text-default-color);
  --dds-text-prominent-color: var(--dds-surface-sidebar-text-prominent-color);
  --dds-state-hover-bg-color: var(--dds-surface-sidebar-state-hover-bg-color);
}
```

As a result:
- Any button placed inside `[data-surface='sidebar']` automatically adopts the sidebar's interactive hover contrast and border tones.
- Any typography element placed inside `[data-surface='code']` inherits high-contrast syntax tokens without requiring custom classes.
- If the global theme flips between light and dark, surface rules re-evaluate without component-level modifications.

---

## 7. Live Surface Delegation Demonstration

```canvas
<l-grid style="--min: 240px; --space: var(--dds-space-md); padding: var(--dds-space-lg); background: var(--dds-surface-bg-color); border: 1px solid var(--dds-surface-border-color); border-radius: var(--dds-radius-lg);">
  <!-- Surface: Docs -->
  <div data-surface="docs" style="padding: var(--dds-space-md); border: 1px solid var(--dds-surface-border-color); border-radius: var(--dds-radius-md); background: var(--dds-surface-bg-color);">
    <l-stack style="--space: var(--dds-space-xs);">
      <span style="font-family: var(--dds-font-technical); font-size: var(--dds-text-caption-size); color: var(--dds-text-muted-color);">[data-surface="docs"]</span>
      <strong style="color: var(--dds-text-prominent-color);">Documentation Surface</strong>
      <p style="margin: 0; font-size: var(--dds-text-caption-size); color: var(--dds-text-default-color);">
        Primary reading typography and clean resting background.
      </p>
    </l-stack>
  </div>

  <!-- Surface: Sidebar -->
  <div data-surface="sidebar" style="padding: var(--dds-space-md); border: 1px solid var(--dds-surface-border-color); border-radius: var(--dds-radius-md); background: var(--dds-surface-bg-color);">
    <l-stack style="--space: var(--dds-space-xs);">
      <span style="font-family: var(--dds-font-technical); font-size: var(--dds-text-caption-size); color: var(--dds-text-muted-color);">[data-surface="sidebar"]</span>
      <strong style="color: var(--dds-text-prominent-color);">Sidebar Surface</strong>
      <p style="margin: 0; font-size: var(--dds-text-caption-size); color: var(--dds-text-default-color);">
        Tonal elevation with remapped interactive state highlights.
      </p>
    </l-stack>
  </div>

  <!-- Surface: Stage -->
  <div data-surface="stage" style="padding: var(--dds-space-md); border: 1px dashed var(--dds-surface-border-color); border-radius: var(--dds-radius-md); background: var(--dds-surface-bg-color); box-shadow: var(--dds-surface-shadow-shape) var(--dds-surface-shadow-color);">
    <l-stack style="--space: var(--dds-space-xs);">
      <span style="font-family: var(--dds-font-technical); font-size: var(--dds-text-caption-size); color: var(--dds-text-muted-color);">[data-surface="stage"]</span>
      <strong style="color: var(--dds-text-prominent-color);">Stage Surface</strong>
      <p style="margin: 0; font-size: var(--dds-text-caption-size); color: var(--dds-text-default-color);">
        Focal preview stage with subtle outer shadow lift and dashed perimeter.
      </p>
    </l-stack>
  </div>

  <!-- Surface: Code -->
  <div data-surface="code" style="padding: var(--dds-space-md); border: 1px solid var(--dds-surface-border-color); border-radius: var(--dds-radius-md); background: var(--dds-surface-bg-color); box-shadow: var(--dds-surface-shadow-shape) var(--dds-surface-shadow-color);">
    <l-stack style="--space: var(--dds-space-xs);">
      <span style="font-family: var(--dds-font-technical); font-size: var(--dds-text-caption-size); color: var(--dds-text-muted-color);">[data-surface="code"]</span>
      <strong style="color: var(--dds-text-prominent-color);">Code Surface</strong>
      <p style="margin: 0; font-size: var(--dds-text-caption-size); color: var(--dds-text-default-color);">
        Sunken code block with inset shadow depth and syntax contrast.
      </p>
    </l-stack>
  </div>
</l-grid>
```

---

## 8. Rules & Engineering Constraints

1. **Never Hardcode `z-index`**: All stacking declarations must reference `--dds-layer-*-z-index` tokens (`sunken`, `base`, `raised`, `floating`, `overlay`).
2. **Never Create Parent-Targeting Selectors**: Do not write `.sidebar .dds-button` or `.dds-button--sidebar`. Declare a `[data-surface]` attribute and let tokens cascade.
3. **Always Decouple Shadow Shapes and Tints**: Combine `--dds-surface-*-shadow-shape` and `--dds-surface-*-shadow-color` so themes can alter shadow warmth and opacity without recalculating geometric spreads.
4. **Use Backdrop Filter Tokens**: Surfaces with translucent backings (`topbar`, `popout`, `overlay`) must declare their blur using `--dds-surface-*-bg-blur`.
