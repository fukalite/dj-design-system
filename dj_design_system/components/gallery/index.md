# DJ Design System

> The UI system powering the gallery

`dj-design-system` dogfoods its own architectural principles: the entire component gallery interface—from its header chrome and navigation tree to interactive split-pane workbenches—is built using the tokens, layout primitives, elements, and composite components defined within this package.

- **Foundations**: 3-tier CSS custom property tokens, fluid typography, modular spacing, and Every Layout primitives.
- **Chrome & Surfaces**: Modular area templates enforcing surface contexts (`data-surface="topbar"`, `data-surface="sidebar"`, `data-surface="docs"`).
- **Component Architecture**: 100% co-located Django component packages, Light DOM Web Components, and CUBE CSS encapsulation.

```canvas
<div style="border: 2px dashed var(--dds-control-accent-color); background: var(--dds-state-hover-bg-color); border-radius: var(--dds-radius-md); padding: var(--dds-space-md);">
  <div style="font-family: var(--dds-text-code-font); font-size: 11px; font-weight: 700; color: var(--dds-control-accent-color); text-transform: uppercase; margin-bottom: 8px;">
    Gallery System Architecture
  </div>

  <l-grid style="--min: 220px; --space: 12px;">
    <!-- 1. Foundations -->
    <div style="background: var(--dds-surface-bg-color); border: 1px solid var(--dds-control-border-color); border-radius: var(--dds-control-border-radius); padding: 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.1);">
      <div style="font-size: 12px; font-weight: 700; color: var(--dds-text-prominent-color); margin-bottom: 4px;">1. Foundations (about/)</div>
      <div style="font-size: 11px; color: var(--dds-text-muted-color); margin-bottom: 8px;">Global design tokens &amp; structural layout primitives.</div>
      <l-stack style="--space: 4px;">
        <span style="background: var(--dds-control-bg-color); color: var(--dds-text-default-color); border: 1px solid var(--dds-control-border-color); padding: 3px 6px; border-radius: var(--dds-control-border-radius); font-size: 10px; font-weight: 600;">Semantic Tokens (3-Tier Cascade)</span>
        <span style="background: var(--dds-control-bg-color); color: var(--dds-text-default-color); border: 1px solid var(--dds-control-border-color); padding: 3px 6px; border-radius: var(--dds-control-border-radius); font-size: 10px; font-weight: 600;">Typography &amp; Fluid Spacing</span>
        <span style="background: var(--dds-control-bg-color); color: var(--dds-text-default-color); border: 1px solid var(--dds-control-border-color); padding: 3px 6px; border-radius: var(--dds-control-border-radius); font-size: 10px; font-weight: 600;">Every Layout Web Components</span>
      </l-stack>
    </div>

    <!-- 2. Interface Areas -->
    <div style="background: var(--dds-surface-bg-color); border: 1px solid var(--dds-control-border-color); border-radius: var(--dds-control-border-radius); padding: 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.1);">
      <div style="font-size: 12px; font-weight: 700; color: var(--dds-text-prominent-color); margin-bottom: 4px;">2. Areas (areas/)</div>
      <div style="font-size: 11px; color: var(--dds-text-muted-color); margin-bottom: 8px;">Persistent chrome &amp; split-pane workspace viewports.</div>
      <l-stack style="--space: 4px;">
        <span style="background: var(--dds-status-info-bg-color); color: var(--dds-status-info-text-color); border: 1px solid var(--dds-status-info-border-color); padding: 3px 6px; border-radius: var(--dds-control-border-radius); font-size: 10px; font-weight: 600;">Topbar, Sidebar, &amp; Tabs Areas</span>
        <span style="background: var(--dds-status-info-bg-color); color: var(--dds-status-info-text-color); border: 1px solid var(--dds-status-info-border-color); padding: 3px 6px; border-radius: var(--dds-control-border-radius); font-size: 10px; font-weight: 600;">Documentation Reference Pane</span>
        <span style="background: var(--dds-status-info-bg-color); color: var(--dds-status-info-text-color); border: 1px solid var(--dds-status-info-border-color); padding: 3px 6px; border-radius: var(--dds-control-border-radius); font-size: 10px; font-weight: 600;">Interactive Sandbox Workbench</span>
      </l-stack>
    </div>

    <!-- 3. Element Primitives -->
    <div style="background: var(--dds-surface-bg-color); border: 1px solid var(--dds-control-border-color); border-radius: var(--dds-control-border-radius); padding: 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.1);">
      <div style="font-size: 12px; font-weight: 700; color: var(--dds-text-prominent-color); margin-bottom: 4px;">3. Elements (elements/)</div>
      <div style="font-size: 11px; color: var(--dds-text-muted-color); margin-bottom: 8px;">Atomic, single-responsibility UI primitives.</div>
      <l-stack style="--space: 4px;">
        <span style="background: var(--dds-status-success-bg-color); color: var(--dds-status-success-text-color); border: 1px solid var(--dds-status-success-border-color); padding: 3px 6px; border-radius: var(--dds-control-border-radius); font-size: 10px; font-weight: 600;">Buttons, Badges, &amp; Icons</span>
        <span style="background: var(--dds-status-success-bg-color); color: var(--dds-status-success-text-color); border: 1px solid var(--dds-status-success-border-color); padding: 3px 6px; border-radius: var(--dds-control-border-radius); font-size: 10px; font-weight: 600;">Notices, Tables, &amp; Code Blocks</span>
        <span style="background: var(--dds-status-success-bg-color); color: var(--dds-status-success-text-color); border: 1px solid var(--dds-status-success-border-color); padding: 3px 6px; border-radius: var(--dds-control-border-radius); font-size: 10px; font-weight: 600;">Popouts, Tabs, &amp; Split Panes</span>
      </l-stack>
    </div>

    <!-- 4. Composite Widgets -->
    <div style="background: var(--dds-surface-bg-color); border: 1px solid var(--dds-control-border-color); border-radius: var(--dds-control-border-radius); padding: 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.1);">
      <div style="font-size: 12px; font-weight: 700; color: var(--dds-text-prominent-color); margin-bottom: 4px;">4. Composites (composites/)</div>
      <div style="font-size: 11px; color: var(--dds-text-muted-color); margin-bottom: 8px;">Domain components assembling multiple primitives.</div>
      <l-stack style="--space: 4px;">
        <span style="background: var(--dds-control-bg-color); color: var(--dds-control-accent-color); border: 1px solid var(--dds-control-border-color); padding: 3px 6px; border-radius: var(--dds-control-border-radius); font-size: 10px; font-weight: 600;">State-Preserving Navigation Tree</span>
        <span style="background: var(--dds-control-bg-color); color: var(--dds-control-accent-color); border: 1px solid var(--dds-control-border-color); padding: 3px 6px; border-radius: var(--dds-control-border-radius); font-size: 10px; font-weight: 600;">Fuzzy Search Combobox &amp; Theme Select</span>
        <span style="background: var(--dds-control-bg-color); color: var(--dds-control-accent-color); border: 1px solid var(--dds-control-border-color); padding: 3px 6px; border-radius: var(--dds-control-border-radius); font-size: 10px; font-weight: 600;">Isolated Canvas Widget &amp; HTMX Drawer</span>
      </l-stack>
    </div>
  </l-grid>
</div>
```

---

## Gallery Structure Guide

### 1. Foundations (`about/`)

The foundational guides document the core styling architecture shared by all components:

- **[Semantic Tokens](about/semantic_tokens.md)**: The three-tier CSS variable hierarchy separating global values, semantic role aliases, and component-scoped variables.
- **[Typography & Spacing](about/typography_and_spacing.md)**: Fluid font scales, system font stacks, and modular spacing scales (`--dds-space-*`).
- **[Layout Primitives](about/layout_primitives.md)**: Zero-layout-CSS composition using Light DOM web components (`<l-stack>`, `<l-cluster>`, `<l-sidebar>`, `<l-grid>`, `<l-frame>`, `<l-switcher>`).

### 2. Interface Areas (`areas/`)

Areas define the structural chrome, persistent surface zones, and content viewports:

- **[Topbar Area](areas/topbar.md)**: Header bar hosting brand identity, drawer toggles, breadcrumb navigation, universal quick search, and consumer theme selection.
- **[Sidebar Area](areas/sidebar.md)**: Navigation drawer enforcing an inverted dark theme surface context (`data-surface="sidebar"`).
- **[Tabs Area](areas/tabs.md)**: View switcher pinned above component documentation to toggle between reference docs and interactive workbenches.
- **[Documentation Area](areas/docs/index.md)**: Master reference layout orchestrating header details, live usage examples, parameter tables, and extended prose.
- **[Sandbox Area](areas/sandbox/index.md)**: Workbench environment hosting responsive controls, isolated preview stages, and dynamic HTMX parameter drawers.
- **[Templates](areas/templates/index.md)**: Fallback directory card grids (`folder.html`) and library landing screens (`index.html`).

### 3. Elements (`elements/`)

Atomic UI components designed with zero style leakage:

- **[Button](elements/button/index.md)**: Interactive button supporting solid, ghost, outline, and icon-only variants.
- **[Badge](elements/badge/index.md)**: Compact metadata indicators, status dots, and code type badges.
- **[Icon](elements/icon/index.md)**: Accessible SVG icon renderer with standardized size scales.
- **[Notice](elements/notice/index.md)**: Contextual banners for alerts, tips, and configuration guidance.
- **[Table](elements/table/index.md)**: Dense, responsive tabular data presentation for parameters and slots.
- **[Breadcrumb](elements/breadcrumb/index.md)**: Hierarchical trail navigation with truncation.
- **[Code Block](elements/code_block/index.md)**: Syntax-highlighted code viewer with clipboard copying.
- **[Popout](elements/popout/index.md)**: Accessible floating dropdown menus and action lists.
- **[Split Pane](elements/split_pane/index.md)**: Resizable two-panel container coordinating side-by-side viewports.

### 4. Composites (`composites/`)

High-level domain components tailored for the gallery experience:

- **[Navigation Tree](composites/nav_tree/index.md)**: Hierarchical tree navigator preserving scroll positions and expanded folder states.
- **[Search Box](composites/search_box/index.md)**: Client-side fuzzy search combobox querying the gallery index.
- **[Theme Select](composites/theme_select/index.md)**: Live theme switcher menu swapping active consumer theme bundles.
- **[Canvas Widget](composites/canvas_widget/index.md)**: Iframe preview container featuring auto-resizing and source code modals.
- **[Sandbox Toolbar](composites/sandbox_toolbar/index.md)**: Viewport preset selector, background color switcher, RTL toggle, and measurement rulers.
- **[Sandbox Parameters](composites/sandbox_params/index.md)**: HTMX-powered parameter mutation drawer generating live form inputs.
