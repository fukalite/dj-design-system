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
- **`elements/`:** Reusable, domain-agnostic UI primitives (`badge`, `breadcrumb`, `button`, `code_block`, `form_field`, `icon`, `notice`, `popout`, `popout_option`, `table`, `tabs`).
- **`domain/`:** Domain-specific gallery UI blocks ("the way the gallery displays X"). Each represents a meaningful unit of design attention, customisation, and consumer shadowing (`gallery_shell`, `sidebar`, `toolbar`, `nav_tree`, `search_box`, `theme_select`, `folder_listing`, `prose`, `params_table`, `usage_example`, `variant_view`, `split_pane`, `sandbox_toolbar`, `params_form`, `canvas_widget`).

### Granularity Threshold
- Do **not** create 1-line wrapper components for trivial HTML tags or single-loop wrappers (e.g. no `UsageExamples` wrapper component).
- A `domain/` component takes a single primary domain dataclass (e.g. `VariantViewData`, `FolderListingData`, `NavTreeData`) and decomposes it internally, delegating to `elements/` via template tags where appropriate.

### 100% Co-location & Documentation
Every component lives in its own folder (`dj_design_system/components/<collection>/<name>/`) containing:
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
- **Zero HTML String Building & No `mark_safe` in Python:** Component Python modules (`<name>.py`) must **never** import `mark_safe` or `format_html`, and must never construct raw HTML markup. Enforced strictly by automated tests (`test_no_html_or_mark_safe_in_python_module`). Presentation logic prepares context; templates own all markup generation.
- **Parameter Specification & Attribute Reflection (`attr`, `data_attr`, `attr_style`):**
  - Declare HTML attributes and data attributes declaratively on parameter specifications:
    - `attr=True`: Emits `<param-name>="<value>"` (e.g. `name = StrParam(default=None, attr=True)`).
    - `attr="custom-name"`: Emits `<custom-name>="<value>"` (e.g. `pressed = BoolParam(default=None, attr="aria-pressed", attr_style="string")`).
    - `data_attr=True`: Emits `data-<param-name>="<value>"` (e.g. `variant = StrParam(..., data_attr=True)` -> `data-variant="..."`).
    - `data_attr="custom-name"`: Emits `data-<custom-name>="<value>"`.
    - `attr_style="boolean"`: Renders a standalone HTML boolean attribute when `True` (e.g. `disabled = BoolParam(default=False, attr=True, attr_style="boolean")` renders `disabled`), and omits it entirely when `False`.
    - `attr_style="string"` (default): Renders string booleans (e.g. `aria-pressed="true"` / `aria-pressed="false"`).
    - Optional parameters default to `default=None` so unset attributes are automatically omitted by the parameter descriptor engine.
- **Orthogonal Parameter & Variant Design:**
  - A component's `variant` parameter must represent purely semantic or visual intent (e.g. `neutral`, `info`, `success`, `warning`, `error`, `primary`, `danger`, `ghost`).
  - **Never conflate variants with orthogonal dimensions:**
    - Typography (e.g. `is_code = BoolParam(default=False)`) is an orthogonal dimension. Never create a `code` variant.
    - Sizing and geometry (e.g. `size = StrParam(...)`, `icon_only = BoolParam(default=False)`) are orthogonal dimensions.
    - Interactive state (e.g. `disabled`, `selected`, `pressed`) is an orthogonal dimension.
  - Reject pragmatic compromises that collapse orthogonal concerns; refactor the parameter API cleanly and cascade updates across consumer templates, gallery configurations, and unit tests.
- **Structured Data Contracts & Public Re-exports:**
  - When a component accepts structured items or collections (e.g. breadcrumb items, tab items, table headers/rows), define a typed `@dataclass` in `<name>.py` (e.g. `BreadcrumbItem`, `TabItem`).
  - Re-export the dataclass and component in `dj_design_system/components/<collection>/<name>/__init__.py` (e.g. `__all__ = ["Breadcrumb", "BreadcrumbItem"]`).
  - Never accept loose dictionaries or untyped tuples when a structured contract can be typed.
- **Bias Logic into `get_context()`:** All parameter defaults, parameter interaction rules (e.g. `disabled` clearing `href`), data sorting/shaping, and complex state resolution belong in `get_context()` (and private helper methods on the component class).

### Templates (`<name>.html`)
- **Declarative Structure:** Templates own DOM structure, child component invocation (`{% dds__... %}`), loops (`{% for ... %}` / `{% empty %}`), and structural branching (`{% if %}` / `{% elif %}` / `{% else %}`) to select polymorphic HTML tags (e.g. `<a>` vs `<button>`), widget types, or optional child elements/attributes.
- **Mandatory Template Attribute Consumption (`{{ attrs }}`):**
  - Templates must render `{{ attrs }}` on the target root or interactive element instead of duplicating attribute rendering with manual `{% if %}` attribute conditions.
  - Attributes rendered through `{{ attrs }}` are automatically escaped and formatted by the framework parameter engine.
  - For components with multiple target elements or polymorphic tag branches, use scoped `{{ <param>_attr }}` helpers (e.g. `{{ disabled_attr }}`) or `{{ attrs }}` appropriately.
- **No Template Value Computation:** Do not use Django template filters (`|default`, `|lower`, etc.) or multi-clause boolean logic to compute fallback values or transform data in templates—prepare those values in `get_context()`.

---

## 4. Layout Composition: Every Layout (`<l-*>`)

### Strict Component Outer Boundaries
- Every component's markup, styles, and scripts must stop cleanly at its root boundary.
- Components must **never** set outer margins (`margin: 0` on the component root) and must adapt to fill whatever space their parent layout provides.

### Every Layout Primitives (`@layer composition`)
- Layout between components and internal structural flow is handled by **Every Layout** primitives in `@layer composition`, not ad-hoc flex/grid wrappers.
- The 11 intrinsic primitives: `<l-stack>`, `<l-cluster>`, `<l-sidebar>`, `<l-switcher>`, `<l-box>`, `<l-center>`, `<l-cover>`, `<l-frame>`, `<l-grid>`, `<l-reel>`, and `<l-imposter>`.
- **Usage Rule:** Prefer custom elements (`<l-stack>`, `<l-cluster>`, etc.) in templates. Use the matching `.l-*` class only when the layout container must be a specific semantic HTML element (e.g. `<nav class="l-cluster">`, `<ul class="l-stack">`).
- **Authoritative Reference:** Complete primitive descriptions, control variables (`--space`, `--measure`, `--min`, `--side-width`), and interactive specimens are documented in [Layout Primitives (Every Layout)](../../dj_design_system/components/gallery/foundations/layout_primitives.md).

---

## 5. CSS Architecture: CUBE CSS, Nesting & Stylelint

All component and layout CSS must strictly follow [html-css.md](html-css.md). Static CSS layout, cascade organisation, and area/pane boundaries are documented in [Design System Foundations](../../dj_design_system/components/gallery/foundations/index.md) and [Areas & Panes](../../dj_design_system/components/gallery/areas/index.md). Key invariants:
- **Strictly No BEM:** Never use `__` (element) or `--` (modifier) class naming anywhere in `dds` components or stylesheets. Enforced by Stylelint.
- **Cascade Layers:** All gallery CSS is organised into explicit native `@layer` blocks:
  ```css
  @layer reset, tokens, global, composition, blocks, utilities;
  ```
- **Native CSS Nesting:** Always prefer native nesting (`&`) for pseudo-classes, states, and internal descendants rather than repeating flat selectors at the same level.
- **Component Boundary Encapsulation (Zero Leakage):**
  - Never reach into a child component's internal selectors from a parent component or layout CSS.
  - Components encapsulate their own internal markup, typography, and syntax highlighting.
  - Components must never set outer margins (`margin: 0` on root); parent layout primitives (`<l-*>`) manage spacing.
- **One CSS Module per Component (`@layer blocks`):**
  - Each component's `<name>.css` wraps its rules in `@layer blocks { ... }`.
  - All rules are scoped under the component root selector (`dds-<name>` for interactive Web Components, or `.dds-<name>` for purely static components).
  - Style internal elements using semantic HTML descendants, `aria-*` attributes (`[aria-selected='true']`), or `data-*` state/variant attributes (`[data-variant='ghost']`, `[data-state='open']`).
- **Variant & Interactive State Preservation:**
  - Pseudo-class state rules (`:hover`, `:active`, `:focus-visible`) must never blanket-reset visual properties (`background-color`, `border-color`, `color`) to neutral tokens if the component supports variants (`primary`, `danger`, status variants).
  - State selectors must either use Tier 3 tokens that adjust dynamically per variant, or provide nested variant state rules (e.g. `&[data-variant='primary']:hover`, `&[data-variant='danger']:hover`) so variant identity is maintained during user interactions.
- **Declaration Grouping & Property Order:** Strictly follow the 5-group property order (Positioning -> Display & Box -> Colour -> Type -> Other). Verified via `just check` (`stylelint`).

---

## 6. Three-Tier Design Token System (`@layer tokens`)

The design system enforces a strict three-tier token hierarchy. Detailed token listings, naming grammar, and rendered specimens are documented in [Semantic Tokens & Naming Scheme](../../dj_design_system/components/gallery/foundations/semantic_tokens.md), [Typography & Spacing System](../../dj_design_system/components/gallery/foundations/typography_and_spacing.md), [Elevations & Surfaces](../../dj_design_system/components/gallery/foundations/elevations_and_surfaces.md), and [Areas & Panes](../../dj_design_system/components/gallery/areas/index.md).

### Tier 1: Literal / Primitive Tokens (Private, `:root` only)
- **Naming:** `--_dds-<palette-or-scale>-<step>` (leading `_` denotes private).
- **Rule:** Defined exclusively on `:root` inside `tokens.css` (specifically `tokens/literal.css`). Never referenced outside `tokens/semantic.css` semantic mappings and `.gallery-theme-dark` overrides. Components, areas, and panes must never consume Tier 1 primitives directly.

### Tier 2: Semantic Tokens (Public Theming API)
- **Naming:** `--dds-<domain>-<role>-<property>` (or `--dds-<domain>-<property>`).
- **Rule:** Defined in `tokens/semantic.css` on `:root` and overridden for dark schemes. Surface selectors (`[data-surface='...']`) only alias `:root` Tier 2 tokens—they must **never** reference Tier 1 `--_dds-*` literals directly, ensuring consumer overrides on `:root` always propagate.
- **Authoritative Reference:** Complete naming grammar, token domains, and live visual specimens are documented in [Semantic Tokens & Naming Scheme](../../dj_design_system/components/gallery/foundations/semantic_tokens.md), [Typography & Spacing System](../../dj_design_system/components/gallery/foundations/typography_and_spacing.md), and [Elevations & Surfaces](../../dj_design_system/components/gallery/foundations/elevations_and_surfaces.md).

### Tier 3: Component-Local Tokens (Private, top of `<name>.css`)
- **Naming:** `--_<component>-<prop>` (leading `_` denotes private to the component).
- **Rule:** Declared at the top of `<name>.css` on the component root selector (`dds-<name>` or `.dds-<name>`), never on `:root`. Every Tier 3 token must map exclusively from Tier 2 `--dds-*` tokens, and all declarations inside `<name>.css` must reference only the component's own `--_<component>-*` tokens.

### Token Tier Usage Matrix

| Token Tier | Prefix / Format | Where Defined | Where Referenced | Usable in Component CSS Rules? |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1: Primitive** | `--_dds-*` | `:root` in `tokens/literal.css` | `:root` semantic maps in `tokens/semantic.css` | ❌ **Forbidden** |
| **Tier 2: Semantic** | `--dds-*` | `:root`, surfaces in `tokens/semantic.css` | Layouts, `<l-*>`, component root Tier 3 maps | ❌ **Only as Tier 3 source** |
| **Tier 3: Component** | `--_<component>-*` | Component root in `<name>.css` | Component internal rules in `<name>.css` | ✅ **Exclusively required** |

---

## 7. Web Components (`<name>.ts`)

- **Light DOM Only:** All `<dds-*>` custom elements operate in Light DOM (no `attachShadow()`), enhancing server-rendered HTML in place.
- **Selector Rule:** Only components with client-side JS behaviour use a `<dds-*>` custom element root; purely static components use semantic HTML tags with a `.dds-<name>` class.
- **Strict DOM Encapsulation:** A Web Component may only query or mutate elements within its own subtree (`this.querySelector(...)` / `this.querySelectorAll(...)`). Reaching outside the component boundary (`document.querySelector(...)` for other components) is forbidden; use bubbling `CustomEvent`s (`dds:<action>`) to communicate upward.
- **HTMX-Safe Lifecycle:** `connectedCallback()` must be idempotent, and `disconnectedCallback()` must abort an instance `AbortController` to clean up any `window`/`document` listeners or observers.
- **Tooling:** Write strict TypeScript in `<name>.ts` following [javascript.md](javascript.md). Compiled `<name>.js` files are gitignored and generated via `just` and package build hooks.
