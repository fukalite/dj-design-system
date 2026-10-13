# About the Design System

This section details the design system's front-end architecture, establishing the invariants, styling layers, design tokens, layout primitives, and template hierarchy that govern the gallery and built-in components.

## Architectural Rules & Invariants

1. **Zero Component Margins**: All component roots enforce `margin: 0`. A component never dictates external spacing; all spatial rhythm is the exclusive responsibility of Every Layout primitives (`<l-stack>`, `<l-cluster>`, etc.).
2. **Strict Cascade Layers (CUBE CSS)**: Stylesheets are structured into explicit native layers (`@layer reset, tokens, global, composition, blocks, utilities`) with strictly no BEM syntax and no `!important`.
3. **Three-Tier Token Encapsulation**: Literal primitives (Tier 1) are private to `:root`; public semantic tokens (Tier 2) are consumed by components via private Tier 3 local variables (`--_<component>-*`).
4. **Contextual Area Delegation**: Surface containers (`[data-surface='...']`) remap semantic tokens so child components adapt automatically across light and inverted dark zones without custom classes.
5. **Decoupled Declarative Templates**: Presentation logic in Python prepares typed dataclasses; templates own markup generation with zero embedded business logic.

## 2. Core Pillars of the Architecture

```canvas
<l-grid style="--min: 220px; --space: var(--dds-space-md);">
  <l-box style="--space: var(--dds-space-md);">
    <l-stack style="--space: var(--dds-space-xs);">
      <strong style="color: var(--dds-text-prominent-color); font-size: var(--dds-text-body-size);">1. Three-Tier Tokens</strong>
      <p style="color: var(--dds-text-muted-color); font-size: var(--dds-text-caption-size); margin: 0;">
        Physical separation between raw primitives (tokens/literal.css), semantic tokens (tokens/semantic.css), and component-local variables.
      </p>
    </l-stack>
  </l-box>
  <l-box style="--space: var(--dds-space-md);">
    <l-stack style="--space: var(--dds-space-xs);">
      <strong style="color: var(--dds-text-prominent-color); font-size: var(--dds-text-body-size);">2. Modular CSS Architecture</strong>
      <p style="color: var(--dds-text-muted-color); font-size: var(--dds-text-caption-size); margin: 0;">
        Strict CUBE CSS cascade layers with dedicated stylesheets for chrome areas, workspace panes, and shell orchestration.
      </p>
    </l-stack>
  </l-box>
  <l-box style="--space: var(--dds-space-md);">
    <l-stack style="--space: var(--dds-space-xs);">
      <strong style="color: var(--dds-text-prominent-color); font-size: var(--dds-text-body-size);">3. Every Layout</strong>
      <p style="color: var(--dds-text-muted-color); font-size: var(--dds-text-caption-size); margin: 0;">
        11 intrinsic layout primitives governing spacing, flow, and alignment with zero component outer margins.
      </p>
    </l-stack>
  </l-box>
  <l-box style="--space: var(--dds-space-md);">
    <l-stack style="--space: var(--dds-space-xs);">
      <strong style="color: var(--dds-text-prominent-color); font-size: var(--dds-text-body-size);">4. Area Delegation</strong>
      <p style="color: var(--dds-text-muted-color); font-size: var(--dds-text-caption-size); margin: 0;">
        Contextual surface zoning that remaps semantic tokens for inverted sidebars, code blocks, and modals.
      </p>
    </l-stack>
  </l-box>
</l-grid>
```

---

## 3. CSS Architecture & File Organisation

Static CSS outside components (`dj_design_system/static/dj_design_system/`) is structured into explicit domains mirroring gallery templates and cascade responsibilities:

```text
dj_design_system/static/dj_design_system/
├── gallery.css             # Master entry point declaring @layer order & aggregating all sub-sheets
├── tokens.css              # Aggregator importing literal.css and semantic.css into @layer tokens
├── tokens/
│   ├── literal.css         # Tier 1 primitives: OKLCH palettes, scale curves, shadow shapes (:root)
│   └── semantic.css        # Tier 2 semantic tokens: theming API, [data-surface], dark scheme overrides
├── areas/                  # Structural chrome stylesheets (1:1 with templates/gallery/areas/)
│   ├── topbar.css          # Pinned header bar, brand clusters, actions, search sizing (.dds-toolbar)
│   ├── sidebar.css         # Navigation drawer, sticky header/footer, tree containment (.dds-sidebar)
│   └── tabs.css            # Component view switcher tab strip ([data-component-tabs])
├── panes/                  # Workspace pane stylesheets (1:1 with templates/gallery/panes/)
│   ├── docs.css            # Reference pane: variant stage, usage examples, parameter tables ([data-docs-pane])
│   ├── sandbox.css         # Workbench pane: canvas flex stack, parameter drawer form ([data-sandbox-pane])
│   ├── folder.css          # Directory card grids for unindexed folders (.dds-folder-listing)
│   ├── index.css           # Static notice banner and landing screen ([id='static-snapshot-notice'])
│   └── prose.css           # Fluid typography for rendered Markdown documentation (.dds-prose)
└── gallery-shell.css       # Layout orchestration: split pane collapse, drawer queries, backdrop scrim
```

### Cascade Layer Hierarchy (CUBE CSS)

All stylesheets declare explicit native layers at their top boundary:

```css
@layer reset, tokens, global, composition, blocks, utilities;
```

1. **`reset`**: Normalises box-sizing, root margins, and media elements.
2. **`tokens`**: Encapsulates Tier 1 literal variables and Tier 2 semantic variables.
3. **`global`**: Base font family, line height, and default background colors.
4. **`composition`**: Every Layout custom elements (`<l-stack>`, `<l-cluster>`, `<l-sidebar>`, etc.).
5. **`blocks`**: BEM-free, scoped component classes, areas (`.dds-toolbar`, `.dds-sidebar`), and panes (`[data-docs-pane]`, `[data-sandbox-pane]`).
6. **`utilities`**: Explicit single-purpose classes (e.g. accessibility helpers).

---

## 4. Dedicated Guides

Explore each dimension of the system in the detailed sections below:

- **[Semantic Tokens & Naming Scheme](semantic_tokens.md)**: Comprehensive breakdown of the 3-tier token hierarchy, physical split between `literal.css` and `semantic.css`, naming conventions, and rendered examples.
- **[Typography & Spacing System](typography_and_spacing.md)**: Typographic roles, font purposes, modular spacing scale (`3xs` to `3xl`), gaps, insets, and layout measures with live specimens.
- **[Layout Primitives (Every Layout)](layout_primitives.md)**: Deep dive into the 11 intrinsic `<l-*>` composition elements, custom property controls, and responsive mechanics without media queries.
- **[Elevations & Surfaces](elevations_and_surfaces.md)**: Depth architecture, contextual surface delegation (`[data-surface]`), z-index layering tiers, and elevation shadow geometry.
- **[Areas & Panes](../areas/index.md)**: Dedicated breakdown of gallery area and pane templates, their 1:1 mapped CSS stylesheets, layout orchestration, composite/element components, and override conventions.
