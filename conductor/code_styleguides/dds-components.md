---
trigger: model_decision
description: When creating, editing, or reviewing built-in dj_design_system gallery components (dj_design_system/components/) or gallery CSS/JS/templates
---

# Built-in `dds` Component & Gallery Styleguide

This styleguide governs **only** the built-in gallery components and UI assets inside `dj_design_system/` (registered under the `dds` namespace).

## 1. Rule Scoping Across the Repository

1. **Package Core (`dj_design_system` engine):** Unopinionated about how external consumers structure their own components, CSS, or JavaScript. Never hardcode `dds`-internal conventions into the core component engine or registry in a way that restricts consumers.
2. **Built-in Gallery Components (`dj_design_system/components/`):** Strictly governed by this document.
3. **Example Project (`example_project/`):** Governed by [example-project.md](example-project.md) to showcase and test the full breadth of consumer-facing package features.

---

## 2. Component Organisation, Co-location & Granularity

### Two Collections (`elements/` vs `domain/`)
All built-in gallery components live under `dj_design_system/components/` in one of two top-level collections, flattened (`FlattenStrategy.ALL`) under the `dds` prefix (`{% dds__<name> %}`):
- **`elements/`:** Reusable, domain-agnostic UI primitives (`button`, `icon`, `code_block`, `table`, `notice`, `tabs` + `tabs/tab_trigger`, `popout`, `split_pane`, `search_box`, `breadcrumb`).
- **`domain/`:** Domain-specific gallery UI blocks ("the way the gallery displays X"). Each represents a meaningful unit of design attention, customisation, and consumer shadowing (`gallery_shell`, `nav_tree`, `folder_listing`, `params_table`, `usage_example`, `variant_view`, `canvas_widget`, `sandbox_toolbar`, `params_form`).

### Granularity Threshold
- Do **not** create 1-line wrapper components for trivial HTML tags or single-loop wrappers (e.g. no `Prose`, `UsageExamples`, or `PopoutOption` wrapper components).
- A `domain/` component takes a single primary domain dataclass (e.g. `VariantViewData`, `FolderListingData`, `NavTreeData`) and decomposes it internally, delegating to `elements/` via template tags where appropriate.

### 100% Co-location & Documentation
Every component lives in its own folder (`dj_design_system/components/<collection>/<name>/`, or nested subfolder for tightly coupled sub-components like `tabs/tab_trigger/`) containing:
- `<name>.py` — Component class with a comprehensive docstring explaining what the component does, when to use it, and how/why to use its variants.
- `<name>.html` — Co-located Django template.
- `<name>.css` — Co-located CUBE CSS block stylesheet.
- `<name>.ts` — Co-located TypeScript Web Component module (only for components with client-side interactivity; compiled `<name>.js` is gitignored and built via `just` / package build hooks).
- `gallery.py` — Variants and gallery configuration so every built-in component can be inspected in the internal `dds` gallery.
- `index.md` — Component documentation page.

Python unit and integration tests remain under `tests/` so `ComponentRegistry.autodiscover()` never imports test modules at runtime.

---

## 3. Component Logic & Template Boundaries

### Python (`<name>.py`)
- **View-Level Presentation Logic Only:** Components sit at the presentation boundary. They must **never** call `dj_design_system.services.*` or `dj_design_system.business_logic.*` (views resolve data via services/business logic and pass domain dataclasses into components).
- **No Python-Level Component Composition:** A component must **never** import, instantiate, or call `.render()` on another component inside Python (`get_context()` or helper methods). All component composition happens in `<name>.html` via `{% dds__... %}` template tags and `{% slot %}` blocks.
- **No HTML String Building in Python:** Do not construct markup with `format_html()` or string concatenation inside `<name>.py`.
- **Bias Logic into `get_context()`:** All parameter defaults, parameter interaction rules (e.g. `disabled` clearing `href`), data sorting/shaping, and complex state resolution belong in `get_context()` (and private helper methods on the component class).

### Templates (`<name>.html`)
- **Declarative Structure:** Templates own DOM structure, child component invocation (`{% dds__... %}`), loops (`{% for ... %}` / `{% empty %}`), and structural branching (`{% if %}` / `{% elif %}` / `{% else %}`) to select polymorphic HTML tags (e.g. `<a>` vs `<button>`), widget types, or optional child elements/attributes.
- **No Template Value Computation:** Do not use Django template filters (`|default`, `|lower`, etc.) or multi-clause boolean logic to compute fallback values or transform data in templates—prepare those values in `get_context()`.

---

## 4. Layout Composition: Every Layout (`<l-*>`)

### Strict Component Outer Boundaries
- Every component's markup, styles, and scripts must stop cleanly at its root boundary.
- Components must **never** set outer margins (`margin: 0` on the component root) and must adapt to fill whatever space their parent layout provides.

### Every Layout Primitives (`@layer composition`)
- Layout between components and internal structural flow is handled by **Every Layout** primitives in `@layer composition`, not ad-hoc flex/grid wrappers:
  - `<l-stack>` (`.l-stack`) — Vertical flow with recursive/direct gap (`--space`).
  - `<l-cluster>` (`.l-cluster`) — Wrapping horizontal groups (toolbars, badges, breadcrumbs).
  - `<l-sidebar>` (`.l-sidebar`) — Fixed-basis sidebar alongside flexible main content.
  - `<l-switcher>` (`.l-switcher`) — Container-width responsive row-to-column switching.
  - `<l-box>` (`.l-box`) — Padded container/surface box.
  - `<l-center>` (`.l-center`) — Horizontally centred max-measure container (`--measure`).
  - `<l-cover>` (`.l-cover`) — Vertically centred hero/empty-state layout.
  - `<l-frame>` (`.l-frame`) — Aspect-ratio / viewport frame container.
  - `<l-grid>` (`.l-grid`) — Responsive auto-fit grid (`--min`).
  - `<l-reel>` (`.l-reel`) — Horizontal scrolling strip (e.g. overflow tabs/chips).
  - `<l-imposter>` (`.l-imposter`) — Positioned overlay/floating container.
- **Usage Rule:** Prefer custom elements (`<l-stack>`, `<l-cluster>`, etc.) in templates. Use the matching `.l-*` class only when the layout container must be a specific semantic HTML element (e.g. `<nav class="l-cluster">`, `<ul class="l-stack">`).
- **Documentation:** Every `<l-*>` primitive must have Markdown documentation in the `dds` gallery with visual debug/outline styling to demonstrate its behaviour.

---

## 5. CSS Architecture: CUBE CSS & `@layer`

- **Strictly No BEM:** Never use `__` (element) or `--` (modifier) class naming anywhere in `dds` components or stylesheets.
- **Cascade Layers:** All gallery CSS is organised into explicit native `@layer` blocks:
  ```css
  @layer reset, tokens, global, composition, blocks, utilities;
  ```
- **One CSS Module per Component (`@layer blocks`):**
  - Each component's `<name>.css` wraps its rules in `@layer blocks { ... }`.
  - All rules are scoped under the component root selector (`dds-<name>` for interactive Web Components, or `.dds-<name>` for purely static components).
  - Style internal elements using semantic HTML descendants, `aria-*` attributes (`[aria-selected='true']`), or `data-*` state/variant attributes (`[data-variant='ghost']`, `[data-state='open']`).
  - Never reach into a child component's internal selectors from a parent component's CSS.

---

## 6. Three-Tier Design Token System (`@layer tokens`)

### Tier 1: Literal / Primitive Tokens (Private, `:root` only)
- **Naming:** `--_dds-<palette-or-scale>-<step>` (leading `_` denotes private).
- **Rule:** Defined exclusively on `:root` inside `tokens.css`. Never referenced outside `:root` / `.gallery-theme-dark` semantic mappings.

### Tier 2: Semantic Tokens (Public Theming API)
- **Naming:** `--dds-<domain>-<role>-<property>` (or `--dds-<domain>-<property>`).
- **Rule:** All Tier 2 tokens are defined on `:root` (and `.gallery-theme-dark`). Surface selectors (`[data-surface='...']`) only alias `:root` Tier 2 tokens—they must **never** reference Tier 1 `--_dds-*` literals directly, ensuring consumer overrides on `:root` always propagate.

#### Domain 1: Elevation Layers & Named Surfaces
- **Elevation Layers (`--dds-layer-<layer>-z-index`):**
  `sunken` (`0`), `base` (`1`), `raised` (`10`), `floating` (`20`), `overlay` (`30`).
- **Named Surfaces (`[data-surface='<name>']`):**
  - `stage` → `sunken` (recessed letterbox area around fixed-width preview iframes; the preview iframe itself is 100% exempt from gallery tokens).
  - `code` → `sunken` (dark in light mode).
  - `docs` → `base` (documentation pane and standalone pages).
  - `sandbox` → `base` (sandbox pane and parameter drawer).
  - `topbar` → `raised` (top header bar and sandbox toolbar).
  - `sidebar` → `raised` (`overlay` on mobile; dark in light mode).
  - `popout` → `floating` (dropdowns, search results, breadcrumb flyout).
  - `overlay` → `overlay` (mobile drawer scrim, modals).
- **Uniform Properties per Surface (`--dds-surface-<name>-<prop>` aliased to `--dds-surface-<prop>`):**
  `bg-color`, `bg-blur`, `border-color`, `border-style`, `border-width`, `border-radius`, `shadow-color`, `shadow-shape`, `z-index` (plus foreground text/state remapping on inverted surfaces like `sidebar` and `code`).

#### Domain 2: Typography & Text
- **Font Purposes (`--dds-font-<purpose>`):** `ui`, `prose`, `technical`.
- **Text Roles (`--dds-text-<role>-<prop>`):**
  - Roles: `title`, `heading`, `subheading`, `overline`, `prose`, `body`, `control`, `caption`, `code`.
  - Properties per role: `font`, `size`, `line-height`, `weight`, `letter-spacing`.
- **Text Prominence (`--dds-text-<level>-color`):** `prominent`, `default`, `muted`.

#### Domain 3: Spacing & Layout
- **Scale (`--dds-space-<step>`):** `3xs`, `2xs`, `xs`, `sm`, `md`, `lg`, `xl`, `2xl`, `3xl`.
- **Gaps (`--dds-space-gap-<role>`):** `tight`, `default`, `section`.
- **Insets (`--dds-space-inset-<role>`):** `compact`, `default`, `page`.
- **Layout Dimensions (`--dds-layout-<prop>`):** `sidebar-width`, `prose-measure`.

#### Domain 4: Interactive States
- **States (`--dds-state-<state>-<prop>`):** `interactive`, `hover`, `focus`, `active`, `selected`, `disabled`.
- **Uniform Properties per State:**
  `text-color`, `bg-color`, `border-color`, `border-style`, `border-width`, `outline-color`, `outline-style`, `outline-width`, `outline-offset`, `shadow-color`, `shadow-shape`, `opacity`.
- **Transitions (`--dds-state-<direction>-<prop>`):**
  `entry-duration`, `entry-easing`, `exit-duration`, `exit-easing`.

#### Domain 5: Controls (Form Fields & Interactive Widgets)
- **Control Box (`--dds-control-<prop>`):**
  `bg-color`, `border-color`, `border-style`, `border-width`, `border-radius`, `shadow-color`, `shadow-shape`, `accent-color`.

#### Domain 6: Status
- **Status Levels (`--dds-status-<level>-<prop>`):** `info`, `success`, `warning`, `error`.
- **Uniform Properties per Status:**
  `text-color`, `bg-color`, `border-color`, `border-style`, `border-width`, `border-radius`, `shadow-color`, `shadow-shape`.

### Tier 3: Component-Local Tokens (Private, top of `<name>.css`)
- **Naming:** `--_<component>-<prop>` (leading `_` denotes private to the component).
- **Rule:** Declared at the top of `<name>.css` on the component root selector (`dds-<name>` or `.dds-<name>`), never on `:root`. Every Tier 3 token must map exclusively from Tier 2 `--dds-*` tokens, and all declarations inside `<name>.css` must reference only the component's own `--_<component>-*` tokens.

---

## 7. Web Components (`<name>.ts`)

- **Light DOM Only:** All `<dds-*>` custom elements operate in Light DOM (no `attachShadow()`), enhancing server-rendered HTML in place.
- **Selector Rule:** Only components with client-side JS behaviour use a `<dds-*>` custom element root; purely static components use semantic HTML tags with a `.dds-<name>` class.
- **Strict DOM Encapsulation:** A Web Component may only query or mutate elements within its own subtree (`this.querySelector(...)` / `this.querySelectorAll(...)`). Reaching outside the component boundary (`document.querySelector(...)` for other components) is forbidden; use bubbling `CustomEvent`s (`dds:<action>`) to communicate upward.
- **HTMX-Safe Lifecycle:** `connectedCallback()` must be idempotent, and `disconnectedCallback()` must abort an instance `AbortController` to clean up any `window`/`document` listeners or observers.
- **Tooling:** Write strict TypeScript in `<name>.ts` following [javascript.md](javascript.md). Compiled `<name>.js` files are gitignored and generated via `just` and package build hooks.
