---
trigger: model_decision
description: When editing CSS, SCSS, HTML, or TypeScript frontend code
---

# Frontend Coding Rules (CSS, SCSS, HTML, TypeScript)

## 1. Architectural Airgap & Scope Boundaries
- **New Architecture Paths**: Files in `src/abc/`, `src/sites/`, and `googlecms/content/components/`.
  - Must strictly adhere to modern platform standards ([architecture.md](../../src/abc/architecture.md)) and the rules defined below.
  - For Django/Wagtail UI components in `googlecms/content/components/`, also adhere to co-location and component architecture rules ([components.md](./components.md)).
- **Legacy Architecture Paths**: Files in `src/site/` and legacy Django templates/scripts outside `components/`.
  - Must defer to existing legacy patterns ([frontend.md](../../src/site/frontend.md)).
  - Permitted to use BEM naming conventions (`.block__element--modifier`), `.spacer-*` utility classes, legacy breakpoints (`@include mixins.mq('md')`), and legacy CSS variables.
  - **Do not unilaterally refactor legacy code to new architecture standards.**

## 2. CSS & SCSS Standards (New Architecture)
- **Cascade Layers**: Sheet entries must use native `@layer` (`reset, tokens, theme, layout, components, utilities`) as defined in `@abc/styles/layers` ([_layers.scss](../../src/abc/styles/_layers.scss)).
- **BEM Deprecation**:
  - Do not use BEM (`__` or `--` modifiers) in modern components.
  - Use clean class names for structural identity (`.dmi-article-card`, `.track`, `.fill`).
  - Use attribute selectors for visual variants and dynamic states (`&[data-variant="split"]`, `&[data-orientation="portrait"]`, `&[aria-expanded="true"]`).
- **Maximum Nesting Depth**: Enforce a strict **maximum nesting depth of 3 levels** in SCSS. Use flat internal class names (`.card-title` or `.title` at level 2) to prevent specificity bloat.
- **3-Tier Custom Property Pattern**:
  1. **System tokens (`--token-*`, `--layout-*`, `--theme-*`)**: Global primitives and layout tokens.
  2. **Public Component API (`--<brand>-<component>-<property>`)**: External customisation contracts (e.g. `--dmi-scroll-progress-fill-color`).
  3. **Private Internal Variables (`--_<variable>`)**: Component-local variables prefixed with `_` used for calculations and internal styling (e.g. `--_fill-color`).
- **Scoping & Encapsulation Rules**:
  - Re-declare all private `--_` variables at the component root selector, mapping public API variables to default tokens with fallbacks (`--_fill-color: var(--dmi-scroll-progress-fill-color, var(--token-color-black));`) to prevent inheritance bleed.
  - Do not create self-referencing (cyclic) variables (`--var: var(--var, default)` is forbidden).
  - Do not define Python-side `default="..."` when Python component parameters use `data_attr=True` and CSS fallback properties provide defaults.
  - Attribute selectors (`&[data-variant="split"]`) must mutate private internal variables (`--_variant: split`), never public API variables.

## 3. TypeScript & Web Components Standards (New Architecture)
- **Inheritance & Naming**:
  - Custom elements must extend [BaseElement](../../src/abc/runtime/element.ts) (`@abc/runtime/element`).
  - Declare `static override readonly tagName = '<brand>-<component>'`.
  - Shared platform components use `abc-<name>`; tenant components must prefix their `tagName` and public CSS properties with their brand (`dmi-`, `gdm-`, `gai-`).
- **DOM Encapsulation (Light DOM Default)**:
  - Components in `googlecms/content/components/` must render in **Light DOM** (`this.innerHTML = ...`) by default so they participate in Cascade Layers, container queries, and global `@abc/styles` tokens.
  - Do not use Shadow DOM unless strict DOM encapsulation is explicitly required.
- **Lifecycle Hooks**:
  - Implement `setup()`, `connect()`, and `disconnect()`.
  - Never override raw DOM callbacks (`connectedCallback`, `disconnectedCallback`) directly when inheriting from `BaseElement`.
- **Event Cleanup**:
  - Bind all DOM event listeners using `this.listen(target, eventName, handler)` inside `connect()` so `BaseElement` unbinds them automatically on disconnect.
- **DOM Queries & Attribute Parsing**:
  - Use `this.$()`, `this.$required()`, and `this.$$()` for descendant queries instead of raw `querySelector`/`querySelectorAll`.
  - Use `this.getAttributeAsString()`, `this.getAttributeAsBoolean()`, and `this.getAttributeAsNumber()` for safe attribute parsing with fallbacks.
- **Cross-Component Events**:
  - Use `this.dispatchCustomEvent('eventName', detail)` to emit namespaced events (`<tag-name>:eventName`).
- **Hydration & Dynamic Imports**:
  - Components are hydrated by site entry point bootstrappers (`@abc/runtime/bootstrap`) using eager hydration by default or hydration directives (`client:load`, `client:idle`, `client:visible`).
  - Use explicit Webpack magic comments in dynamic loaders (`/* webpackChunkName: "components/<brand>_<component>" */`).
  - Use `webpackPrefetch: true` selectively (only for ubiquitous components appearing on ~80% of pages); never use `webpackPreload: true` in registries.
- **Headless Behaviours**:
  - Non-visual page-level behaviours (cursors, shortcuts, telemetry) must be implemented as headless custom elements extending `BaseElement` without template rendering.
