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

## 6. Three-Tier Design Token Hierarchy & Usage Boundaries

Never hard-code magic numbers or raw colour codes in component stylesheets or layouts. All styling must strictly respect the three-tier token architecture:

```
Tier 1: Primitive Tokens (--_dds-*) [Private, :root only]
   │
   ▼
Tier 2: Semantic Tokens (--dds-*) [Public Theming API, :root & surfaces]
   │
   ├──▶ Consumed by Layouts & Composition Primitives (<l-*>, layout CSS)
   │
   ▼
Tier 3: Component-Local Tokens (--_<component>-*) [Private, component root]
   │
   └──▶ Consumed by Component CSS Declarations (<name>.css)
```

### Tier 1: Literal / Primitive Tokens (Private, `:root` only)
- **Format:** `--_dds-<palette-or-scale>-<step>` (leading `_` denotes private to token definition).
- **Where Defined:** Exclusively on `:root` inside `tokens.css`.
- **Usage Boundary:** **NEVER referenced outside `tokens.css` `:root` and theme overrides (`.gallery-theme-dark`).** Components, layouts, utilities, and surfaces must never consume Tier 1 tokens directly.

### Tier 2: Semantic Tokens (Public Theming API)
- **Format:** `--dds-<domain>-<role>-<property>` or `--dds-<domain>-<property>` (e.g. `--dds-surface-code-bg-color`, `--dds-text-body-font`, `--dds-space-md`, `--dds-control-border-width`).
- **Where Defined:** On `:root` in `tokens.css`. Surface selectors (`[data-surface='...']`) alias `:root` Tier 2 tokens without touching Tier 1 literals.
- **Usage Boundary:**
  - Layout stylesheets and Every Layout composition primitives (`<l-*>`) consume Tier 2 tokens directly.
  - Component stylesheets consume Tier 2 tokens **exclusively to map their Tier 3 tokens** at the component root.

### Tier 3: Component-Local Tokens (Private, `<name>.css`)
- **Format:** `--_<component>-<prop>` (leading `_` denotes private to the component).
- **Where Defined:** At the top of `<name>.css` on the component root selector (`dds-<name>` or `.dds-<name>`). **NEVER on `:root`**.
- **Usage Boundary:**
  - Every Tier 3 token must map **exclusively from Tier 2 `--dds-*` tokens** (e.g. `--_button-bg-color: var(--dds-state-interactive-bg-color);`).
  - All declarations inside `<name>.css` must reference **only** the component's own `--_<component>-*` tokens. Never reference Tier 2 `--dds-*` directly inside component rules.

### Token Tier Usage Matrix

| Token Tier | Prefix / Format | Where Defined | Where Referenced | Usable in Component CSS Rules? |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1: Primitive** | `--_dds-*` | `:root` in `tokens.css` | `:root` semantic maps in `tokens.css` | ❌ **Forbidden** |
| **Tier 2: Semantic** | `--dds-*` | `:root`, surfaces in `tokens.css` | Layouts, `<l-*>`, component root Tier 3 maps | ❌ **Only as Tier 3 source** |
| **Tier 3: Component** | `--_<component>-*` | Component root in `<name>.css` | Component internal rules in `<name>.css` | ✅ **Exclusively required** |

---

## 7. HTML Standards & Semantics

- **Valid HTML5**: Use semantic elements for their intended purpose (`<nav>`, `<header>`, `<main>`, `<article>`, `<button>`, `<a>`).
- **Lowercase**: Use lowercase for all element names, attributes, and values.
- **Quotes**: Double quotes (`""`) for HTML attribute values; single quotes (`''`) for CSS attribute selectors (`[data-state='open']`).
- **Separation of Concerns**: Markup owns structure, CSS owns presentation, JavaScript/TypeScript owns behaviour.
- **Accessibility (a11y)**:
  - Interactive elements must be keyboard accessible and use appropriate `aria-*` attributes (`aria-label`, `aria-expanded`, `aria-selected`).
  - Provide `alt` text for images and transcripts/labels for icons.
