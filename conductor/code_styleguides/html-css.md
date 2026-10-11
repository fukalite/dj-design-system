---
trigger: model_decision
description: When creating, editing, or reviewing HTML or CSS code across templates and stylesheets
---

# HTML & CSS Styleguide

This styleguide defines the mandatory HTML and CSS standards for the project. Automated validation is enforced via Stylelint, djLint, and CI.

---

## 1. CSS Architecture & Layers (CUBE CSS)

All stylesheets are organised into explicit native cascade layers:
```css
@layer reset, tokens, global, composition, blocks, utilities;
```

- **`reset`**: Modern CSS baseline resets.
- **`tokens`**: Design token definitions (`:root` Tier 1 private and Tier 2 semantic variables).
- **`global`**: Fundamental page and document defaults.
- **`composition`**: Every Layout layout primitives (`<l-*>`, `.l-*`).
- **`blocks`**: Component-scoped CSS modules (`<name>.css`).
- **`utilities`**: Pure utility classes (used sparingly).

---

## 2. Native CSS Nesting (`&`)

Always prefer native CSS nesting over repeating flat, compound, or descendant selectors at the same level.

- **Pseudo-classes and States**: Nest under the parent rule with `&`:
  ```css
  /* Good */
  .dds-card {
    background-color: var(--_card-bg-color);

    &:hover {
      background-color: var(--_card-hover-bg-color);
    }

    &:focus-visible {
      outline-width: var(--_card-focus-outline-width);
    }
  }

  /* Bad */
  .dds-card { ... }
  .dds-card:hover { ... }
  .dds-card:focus-visible { ... }
  ```
- **Direct & Descendant Elements**: Group and nest internal child selectors within their enclosing container:
  ```css
  /* Good */
  .dds-folder-listing {
    ...
    & > l-stack { ... }
    & [data-folder-title] { ... }
    & [data-folder-grid] {
      ...
      & > li { ... }
    }
  }

  /* Bad */
  .dds-folder-listing { ... }
  .dds-folder-listing > l-stack { ... }
  .dds-folder-listing [data-folder-title] { ... }
  .dds-folder-listing [data-folder-grid] { ... }
  .dds-folder-listing [data-folder-grid] > li { ... }
  ```
- **Nesting Depth**: Keep nesting hierarchies shallow and performant. Avoid nesting deeper than 3 levels unless structurally necessary.

---

## 3. Component Boundary Encapsulation (Zero Leakage)

Component styles must stop strictly at the component root boundary.

- **No Piercing Child Components**: Never target or alter elements inside a child component from a parent component's CSS.
  - *Example*: A gallery or layout stylesheet must not style `dds-code-block code`, `dds-icon svg`, or `.dds-button span`.
  - Child components are independent units that own and encapsulate their internal DOM, typography, and syntax highlighting.
- **Root Zero Margins**: Components must never set outer margins on their own root selector (`margin: 0` on root). Outer spacing and alignment are the exclusive responsibility of parent Every Layout primitives (`<l-stack>`, `<l-cluster>`, etc.).
- **Scoped Theme Variables**: If a parent must influence a child, pass values via CSS custom property overrides on the component element or use `data-*` attributes.

---

## 4. Stylelint & Quality Constraints

Automated linting is enforced via `just check` (`npx stylelint "dj_design_system/**/*.css"`) and runs on every CI pull request.

- **Strictly No BEM**: Never use `__` (element) or `--` (modifier) naming in CSS classes. Enforced via `selector-class-pattern`.
  - Use semantic tags (`pre`, `code`, `header`), `data-*` attributes (`[data-surface='code']`, `[data-variant='primary']`), or `aria-*` attributes (`[aria-selected='true']`).
- **No `!important`**: Forbidden without exception (`declaration-no-important`).
- **No ID Selectors**: Forbidden in CSS rules (`selector-max-id: 0`).
- **No Duplicate or Unknown Properties**: Clean, valid CSS only.

---

## 5. Declaration Grouping & Property Order

Declarations within every CSS rule must be grouped by type and strictly ordered as follows. Do not add section comments; preserve the order directly:

1. **Positioning**:
   `position`, `top`, `right`, `bottom`, `left`, `inset`, `inset-block`, `inset-inline`, `z-index`.
2. **Display & Box Model**:
   `display`, `flex`, `flex-*`, `grid`, `grid-*`, `gap`, `align-items`, `justify-content`, `order`, `box-sizing`, `width`, `min-width`, `max-width`, `height`, `min-height`, `max-height`, `inline-size`, `block-size`, `margin`, `margin-block`, `margin-inline`, `padding`, `padding-block`, `padding-inline`, `border`, `border-radius`, `outline`, `overflow`, `overflow-x`, `overflow-y`, `contain`.
3. **Colour & Visuals**:
   `color`, `background`, `background-color`, `box-shadow`, `opacity`, `visibility`.
4. **Typography**:
   `font`, `font-family`, `font-size`, `font-weight`, `font-style`, `font-variant`, `line-height`, `letter-spacing`, `text-align`, `text-decoration`, `text-transform`, `white-space`, `tab-size`.
5. **Other / Misc**:
   `cursor`, `transition`, `transition-*`, `animation`, `transform`, `pointer-events`, `appearance`, `user-select`.

*(Use `npx stylelint --fix` to format automatically).*

---

## 6. Design Tokens Over Magic Numbers

Never hard-code magic numbers or raw colour codes in component stylesheets or layouts.

- **Tokens Required**:
  - Colours: `var(--dds-surface-*)`, `var(--dds-text-*)`, `var(--dds-state-*)`, `var(--dds-control-*)`.
  - Spacing & Insets: `var(--dds-space-*)`, `var(--dds-space-gap-*)`, `var(--dds-space-inset-*)`.
  - Typography: `var(--dds-text-<role>-<prop>)`, `var(--dds-font-*)`.
  - Border Widths: `var(--dds-surface-*-border-width)`, `var(--dds-control-border-width)`.
  - Border Radii: `var(--dds-surface-border-radius)`, `var(--dds-control-border-radius)`.
- **Private Tier 3 Tokens**: Component-local CSS must map all internal properties to `--_<component>-*` variables declared at the component root and sourced exclusively from Tier 2 `--dds-*` tokens.

---

## 7. HTML Standards & Semantics

- **Valid HTML5**: Use semantic elements for their intended purpose (`<nav>`, `<header>`, `<main>`, `<article>`, `<button>`, `<a>`).
- **Lowercase**: Use lowercase for all element names, attributes, and values.
- **Quotes**: Double quotes (`""`) for HTML attribute values; single quotes (`''`) for CSS attribute selectors (`[data-state='open']`).
- **Separation of Concerns**: Markup owns structure, CSS owns presentation, JavaScript/TypeScript owns behaviour.
- **Accessibility (a11y)**:
  - Interactive elements must be keyboard accessible and use appropriate `aria-*` attributes (`aria-label`, `aria-expanded`, `aria-selected`).
  - Provide `alt` text for images and transcripts/labels for icons.
