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
        Strict separation between raw primitives, semantic tokens, and component-local variables.
      </p>
    </l-stack>
  </l-box>
  <l-box style="--space: var(--dds-space-md);">
    <l-stack style="--space: var(--dds-space-xs);">
      <strong style="color: var(--dds-text-prominent-color); font-size: var(--dds-text-body-size);">2. Every Layout</strong>
      <p style="color: var(--dds-text-muted-color); font-size: var(--dds-text-caption-size); margin: 0;">
        11 intrinsic layout primitives governing spacing, flow, and alignment with zero component outer margins.
      </p>
    </l-stack>
  </l-box>
  <l-box style="--space: var(--dds-space-md);">
    <l-stack style="--space: var(--dds-space-xs);">
      <strong style="color: var(--dds-text-prominent-color); font-size: var(--dds-text-body-size);">3. Area Delegation</strong>
      <p style="color: var(--dds-text-muted-color); font-size: var(--dds-text-caption-size); margin: 0;">
        Contextual surface zoning that remaps semantic tokens for inverted sidebars, code blocks, and modals.
      </p>
    </l-stack>
  </l-box>
  <l-box style="--space: var(--dds-space-md);">
    <l-stack style="--space: var(--dds-space-xs);">
      <strong style="color: var(--dds-text-prominent-color); font-size: var(--dds-text-body-size);">4. Template Hierarchy</strong>
      <p style="color: var(--dds-text-muted-color); font-size: var(--dds-text-caption-size); margin: 0;">
        Declarative Django templates decoupled from business logic, structured into modular areas and panes.
      </p>
    </l-stack>
  </l-box>
</l-grid>
```

---

## 3. Dedicated Guides

Explore each dimension of the system in the detailed sections below:

- **[Semantic Tokens & Naming Scheme](semantic_tokens.md)**: Comprehensive breakdown of the 3-tier token hierarchy, naming conventions, semantic domains (surfaces, actions, status, controls), and rendered examples.
- **[Typography & Spacing System](typography_and_spacing.md)**: Typographic roles, font purposes, modular spacing scale (`3xs` to `3xl`), gaps, insets, and layout measures with live specimens.
- **[Layout Primitives (Every Layout)](layout_primitives.md)**: Deep dive into the 11 intrinsic `<l-*>` composition elements, custom property controls, and responsive mechanics without media queries.
- **[Areas & Token Delegation](areas_and_token_delegation.md)**: How gallery areas (`topbar`, `sidebar`, `stage`, `docs`, `sandbox`) create visual contexts by delegating and overriding semantic tokens.
- **[Template Breakdown & Responsibilities](templates.md)**: The Django template architecture, detailing how shell, area, and pane templates divide responsibilities and facilitate consumer shadowing.
