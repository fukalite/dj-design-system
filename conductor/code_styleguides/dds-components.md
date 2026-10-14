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

### Two Component Groups (`elements/` vs `composites/`) + Areas & Panes
All built-in gallery components live under `dj_design_system/components/gallery/` in one of two groups, flattened (`FlattenStrategy.ALL`) under the `dds` prefix (`{% dds__<name> %}`):
- **`elements/`:** Reusable, domain-agnostic UI primitives (`badge`, `breadcrumb`, `button`, `code_block`, `form_field`, `icon`, `notice`, `popout`, `popout_option`, `split_pane`, `table`, `tabs`, `tooltip`).
- **`composites/`:** Domain-specific gallery composite components (`canvas_widget`, `nav_tree`, `sandbox_params`, `sandbox_toolbar`, `search_box`, `theme_select`).
- **Areas & Panes (`dj_design_system/templates/dj_design_system/gallery/`):** Structural chrome areas (`topbar`, `sidebar`, `tabs`) and content panes (`docs`, `sandbox`, `folder`, `index`, `prose`) are Django templates documented in [Areas & Panes](../../dj_design_system/components/gallery/areas/index.md), not wrapper components.

### Granularity Threshold
- Do **not** create 1-line wrapper components for trivial HTML tags or single-loop wrappers.
- Page-level areas and panes compose `elements/` and `composites/` via template tags and `{% slot %}` blocks.

### 100% Co-location & Documentation
Every component lives in its own folder (`dj_design_system/components/gallery/<group>/<name>/`) containing:
- `<name>.py` — Component class with a comprehensive docstring explaining what the component does, when to use it, and how/why to use its variants.
- `<name>.html` — Co-located Django template.
- `<name>.css` — Co-located CUBE CSS block stylesheet.
- `<name>.ts` — Co-located TypeScript Web Component module (only for components with client-side interactivity; compiled `<name>.js` is gitignored and built via `just build-ts` / package build hooks).
- `gallery.py` — Variants and gallery configuration so every built-in component can be inspected in the internal `dds` gallery.
- `index.md` — Component documentation page.

Python unit tests live under `tests/components/test_<name>.py` and native TypeScript behavioural DOM tests live under `tests/ts/<name>.test.ts` so `ComponentRegistry.autodiscover()` never imports test modules at runtime.

---

## 3. Component Logic & Template Boundaries

### Python (`<name>.py`)
- **View-Level Presentation Logic Only:** Components sit at the presentation boundary. They must **never** call `dj_design_system.services.*` or `dj_design_system.business_logic.*` (views resolve data via services/business logic and pass data into components).
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
- **Component-Local Dataclasses & Public Re-exports:**
  - When a component accepts structured items or collections (e.g. breadcrumb items, tab items, theme options, search entries, sandbox controls, nav tree nodes), define a self-contained `@dataclass(frozen=True)` in `<name>.py` (e.g. `BreadcrumbItem`, `TabItem`, `ThemeOption`, `SearchIndexEntry`, `SandboxControlOption`, `NavTreeNode`).
  - Re-export the dataclass and component in `dj_design_system/components/gallery/<group>/<name>/__init__.py` (e.g. `__all__ = ["ThemeSelect", "ThemeOption"]`).
  - Never couple component modules to internal engine dataclasses in `dj_design_system.data`; accept the component's own dataclass plus duck-typed objects/mappings normalized in `get_context()`.
- **No Leaked Page Routing or HTMX Targets:**
  - Never hardcode gallery routing query inputs (`_iss`, `_dds_theme`, `_dds_variant`) or page-layout HTMX target selectors (e.g. `closest [data-gallery-sandbox-body]`) inside component classes or templates. Expose slots (e.g. `{% slot "extra_inputs" %}`) and explicit parameters (`hx_target = StrParam(default=None)`) so the hosting pane template supplies page-level wiring.
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

## 7. Web Components (`<name>.ts`), Page Mediators & Native Testing

- **Light DOM Only:** All `<dds-*>` custom elements operate in Light DOM (no `attachShadow()`), enhancing server-rendered HTML in place.
- **Selector Rule:** Only components with client-side JS behaviour use a `<dds-*>` custom element root; purely static components use semantic HTML tags with a `.dds-<name>` class.
- **Strict DOM Encapsulation & Public Method APIs:**
  - A Web Component may only query or mutate elements within its own subtree (`this.querySelector(...)` / `this.querySelectorAll(...)`). Reaching outside the component boundary (`document.querySelector(...)` for sibling/parent components) is forbidden.
  - Parent components or page managers must **never** pierce a child custom element's internal DOM (e.g. querying `[data-popout-trigger] > span` from a parent). Instead, child custom elements expose public methods for downward orchestration (e.g. `popout.selectValue(value)`, `searchBox.focusInput()`, `toolbar.applyState(state)`, `canvas.setStageState(state)`) and emit bubbling `CustomEvent`s (`dds:<action>`) upward.
- **Zero Global Side-Effects in Components (Page Mediator Pattern):**
  - Element and composite `.ts` files must **never** mutate `document.cookie`, `localStorage`, `sessionStorage`, or `window.location.href`, and must not register un-scoped global keyboard shortcuts (such as `/` on `document`).
  - All persistence, URL navigation, cross-component state coordination, and global shortcuts belong in the modular page-level managers (`ThemeManager`, `PaneManager`, `SandboxManager` in `dj_design_system/static/dj_design_system/`) orchestrated by `<dds-gallery-shell>`.
- **Iframe Boundary Discipline (`postMessage` Only):**
  - Host components (`<dds-canvas-widget>`) must **never** penetrate a preview iframe's `contentDocument` to inject `<style>` tags or mutate DOM attributes (`dir="rtl"`).
  - Communicate stage state across the iframe boundary exclusively via `iframe.contentWindow.postMessage({ type: 'dds:canvas-stage', ... }, '*')`, handled inside the iframe by `canvas-resize.ts` and `canvas.css` (`[data-canvas-outline]`, `[data-canvas-measure]`).
- **HTMX-Safe Lifecycle:** `connectedCallback()` must be idempotent, and `disconnectedCallback()` must abort an instance `AbortController` to clean up any `window`/`document` listeners, timers, or observers.
- **Native TypeScript Testing (`Vitest` + `happy-dom`):**
  - All `<dds-*>` custom elements and static TypeScript managers must be tested behaviourally in `tests/ts/<name>.test.ts` using Vitest (`just test-ts` / `just test`).
  - **Never** write Python `pytest` tests that read `.ts` files as strings to assert on TypeScript syntax or implementation details. Python component tests (`tests/components/test_<name>.py`) test Python contracts, template rendering, CSS layers/tokens, and gallery configurations; Vitest tests DOM behaviour, events, ARIA state, and lifecycle cleanup.
- **Tooling:** Write strict TypeScript in `<name>.ts` following [javascript.md](javascript.md). Compiled `.js` files are gitignored and generated via `just build-ts` and package build hooks.

