# DJ Design System

> The UI system powering the gallery

`dj-design-system` dogfoods its own architectural principles: the entire component gallery interface—from its header chrome and navigation tree to interactive split-pane workbenches—is built using the tokens, layout primitives, elements, and composite components defined within this package.

- **Foundations**: 3-tier CSS custom property tokens, fluid typography, modular spacing, and Every Layout primitives.
- **Chrome & Surfaces**: Modular area templates enforcing surface contexts (`data-surface="topbar"`, `data-surface="sidebar"`, `data-surface="docs"`).
- **Component Architecture**: 100% co-located Django component packages, Light DOM Web Components, and CUBE CSS encapsulation.

```canvas
<div style="border: 2px dashed #6366f1; background: rgba(99, 102, 241, 0.03); border-radius: 8px; padding: 14px;">
  <div style="font-family: monospace; font-size: 11px; font-weight: 700; color: #4338ca; text-transform: uppercase; margin-bottom: 8px;">
    Gallery System Architecture
  </div>

  <l-grid style="--min: 220px; --space: 12px;">
    <!-- 1. Foundations -->
    <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 6px; padding: 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
      <div style="font-size: 12px; font-weight: 700; color: #0f172a; margin-bottom: 4px;">1. Foundations (about/)</div>
      <div style="font-size: 11px; color: #64748b; margin-bottom: 8px;">Global design tokens &amp; structural layout primitives.</div>
      <l-stack style="--space: 4px;">
        <span style="background: #f1f5f9; color: #334155; padding: 3px 6px; border-radius: 4px; font-size: 10px; font-weight: 600;">Semantic Tokens (3-Tier Cascade)</span>
        <span style="background: #f1f5f9; color: #334155; padding: 3px 6px; border-radius: 4px; font-size: 10px; font-weight: 600;">Typography &amp; Fluid Spacing</span>
        <span style="background: #f1f5f9; color: #334155; padding: 3px 6px; border-radius: 4px; font-size: 10px; font-weight: 600;">Every Layout Web Components</span>
      </l-stack>
    </div>

    <!-- 2. Interface Areas -->
    <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 6px; padding: 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
      <div style="font-size: 12px; font-weight: 700; color: #0f172a; margin-bottom: 4px;">2. Areas (areas/)</div>
      <div style="font-size: 11px; color: #64748b; margin-bottom: 8px;">Persistent chrome &amp; split-pane workspace viewports.</div>
      <l-stack style="--space: 4px;">
        <span style="background: #e0f2fe; color: #0369a1; padding: 3px 6px; border-radius: 4px; font-size: 10px; font-weight: 600;">Topbar, Sidebar, &amp; Tabs Areas</span>
        <span style="background: #e0f2fe; color: #0369a1; padding: 3px 6px; border-radius: 4px; font-size: 10px; font-weight: 600;">Documentation Reference Pane</span>
        <span style="background: #e0f2fe; color: #0369a1; padding: 3px 6px; border-radius: 4px; font-size: 10px; font-weight: 600;">Interactive Sandbox Workbench</span>
      </l-stack>
    </div>

    <!-- 3. Element Primitives -->
    <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 6px; padding: 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
      <div style="font-size: 12px; font-weight: 700; color: #0f172a; margin-bottom: 4px;">3. Elements (elements/)</div>
      <div style="font-size: 11px; color: #64748b; margin-bottom: 8px;">Atomic, single-responsibility UI primitives.</div>
      <l-stack style="--space: 4px;">
        <span style="background: #f0fdf4; color: #166534; padding: 3px 6px; border-radius: 4px; font-size: 10px; font-weight: 600;">Buttons, Badges, &amp; Icons</span>
        <span style="background: #f0fdf4; color: #166534; padding: 3px 6px; border-radius: 4px; font-size: 10px; font-weight: 600;">Notices, Tables, &amp; Code Blocks</span>
        <span style="background: #f0fdf4; color: #166534; padding: 3px 6px; border-radius: 4px; font-size: 10px; font-weight: 600;">Popouts, Tabs, &amp; Split Panes</span>
      </l-stack>
    </div>

    <!-- 4. Composite Widgets -->
    <div style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 6px; padding: 12px; box-shadow: 0 1px 2px rgba(0,0,0,0.05);">
      <div style="font-size: 12px; font-weight: 700; color: #0f172a; margin-bottom: 4px;">4. Composites (composites/)</div>
      <div style="font-size: 11px; color: #64748b; margin-bottom: 8px;">Domain components assembling multiple primitives.</div>
      <l-stack style="--space: 4px;">
        <span style="background: #faf5ff; color: #6b21a8; padding: 3px 6px; border-radius: 4px; font-size: 10px; font-weight: 600;">State-Preserving Navigation Tree</span>
        <span style="background: #faf5ff; color: #6b21a8; padding: 3px 6px; border-radius: 4px; font-size: 10px; font-weight: 600;">Fuzzy Search Combobox &amp; Theme Select</span>
        <span style="background: #faf5ff; color: #6b21a8; padding: 3px 6px; border-radius: 4px; font-size: 10px; font-weight: 600;">Isolated Canvas Widget &amp; HTMX Drawer</span>
      </l-stack>
    </div>
  </l-grid>
</div>
```
