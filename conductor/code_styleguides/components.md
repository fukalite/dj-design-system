---
trigger: model_decision
description: When working on Design System components based on dj-design-system; this might include Python, HTML, CSS/SASS or JavaScript/TypeScript
---

# UI Component Architecture Rules

> **Reference Architecture:** For complete platform, multisite, hydration, and CSS styling guidelines, see [src/abc/architecture.md](../../src/abc/architecture.md).

When creating or refactoring `dj-design-system` / `design-components` UI components, adhere strictly to the following rules:

## 1. File Structure and Co-location
- **Co-location:** Every component must have its Python file, HTML template, and SCSS file co-located in the same directory (e.g., `googlecms/content/components/person_card/`).
- **Optional TypeScript (.ts):** Co-located `.ts` files are **optional**. Only create a `.ts` file if client-side behavior, event listening, or element hydration is required. Do NOT create empty `.ts` files for static HTML/CSS components.
- **Tests:** Component tests must be broken out into a folder (`googlecms/content/tests/components/`), with exactly one test file per component (e.g., `test_person_card.py`). Do not group them into a single monolithic test file. Test the python implementation only.
- **Auto-discovery:** Do not pass explicit `template_name` parameters in the component class unless the template cannot be auto-discovered. The framework will find it automatically by naming convention.

## 2. Abstraction and Domain Types
- **Strict Typing and Casting:** Components must take custom parameters that are strictly type-locked to the specific domain models they represent (e.g., `profile: DirectoryProfile`).
- **No Type Redundancy:** Do not accept loose types or perform redundant instance checks (like accepting both `User` and `DirectoryProfile` and picking one). Force the caller to provide the correct abstraction.
- **Maintain Abstraction Layers:** Components should not reach outside their bounds or perform database queries. Pass the fully hydrated domain object directly.

## 3. Markup & DOM Architecture
- **No BEM Classes:** Never use BEM classes anywhere. Use minimal semantic nested CSS classes (`.title`, `.media`) or bare HTML tags scoped inside the custom element root (`abc-card { .title { ... } }`).
- **Minimal DOM & Classes:** Avoid unnecessary intermediate wrapper elements (`.content`, `.meta`, etc.) and unnecessary classes. Keep markup as lean and minimal as possible to output the required information.
- **No Django Default Filters in Templates:** Never use Django `|default:"..."` filters in templates. If a default is needed, declare it explicitly on the parameter descriptor attribute in Python (`default=...`). 
- **Declarative HTML Data Attributes:** Use `dj-design-system`'s built-in parameter attribute support (`data_attr=True`, `data_attr="name"`, `attr_style="boolean"`) on descriptors so templates can use `<element {{ attrs }}>` instead of writing conditional `{% if %}` template logic for data attributes.

## 4. Python Component Logic
- **Fat Models, Thin Contexts:** Business logic, data formatting, and conditional derivations come from the service layer. Do not put this logic inside the component.
- **Extract Parameters:** Extract the logic for fetching individual rendering parameters into separate `get_xxx(self, context, ...)` methods; and only if needed. The `get_context` function should do little more than call these methods to consolidate the dictionary.
- **Direct Parameter Attribute Access:** Never use `getattr(self, "param_name", default)` on parameter descriptors. `dj_design_system` parameters are descriptors that are always safely accessible directly via instance attributes (`self.param_name`).
- **Use Parameter Defaults, No Magic Fallbacks:** Declare explicit default values on parameter descriptors (e.g., `default=""`, `default=CardLayoutVariant.STANDARD`). Never write defensive fallback magic strings or conditional default overrides inside component methods.
- **No Redundant Context Assignment:** Do not re-assign parameter values back into `context` in `get_context()` (e.g., avoid `context["url"] = self.url` or `context["variant"] = self.variant`). `super().get_context()` automatically populates all declared parameter attributes into the context dictionary.
- **Convention Over Configuration in Meta:** Do not manually specify `name`, `verbose_name`, `template`, or `abstract = False` on concrete component `Meta` classes when using standard conventions. `dj_design_system` automatically derives component names from the class name (`FooBarComponent` -> `"foo_bar"`), resolves co-located templates (`{name}.html`), and marks components as concrete by default. Only specify `Meta.abstract = True` on base classes and `Meta.slots` when slots are declared.
- **Centralised Parameter Definitions:** All reusable custom parameter descriptors (`*Param`) and domain data types (e.g., `MediaItem`) must be defined in `googlecms/content/components/parameters.py` and imported by components.
- **Thorough Testing:** Ensure all individual `get_xxx` functions are properly unit-tested in the corresponding component test file.
- **Fixtures over Mocks:** Use `factory_boy` factories to generate rich test fixtures. Do not use PII (personally identifiable information) or real names in test fixtures.

## 5. Custom Elements & Accessibility
- **Display Properties for Custom Tags:** Custom element tags (e.g. `<abc-header>`, `<abc-footer>`) default to `display: inline` in browsers. Component SCSS must explicitly declare layout display properties (`display: block` or `display: flex`) on custom element root selectors.
- **Accessibility Landmarks:** When Custom Element tags replace native HTML5 landmark elements (such as replacing `<header>` and `<footer>` with `<abc-header>` and `<abc-footer>`), preserve explicit ARIA landmark roles (e.g., `role="banner"`, `role="contentinfo"`).

## 6. CSS & Styling Guidelines
- **Nesting:** Write CSS using native nesting to keep scoping clear.
- **Attribute-Driven Variants (BEM Replacement):** Use key-value `data-*` attributes (`data-variant="split"`, `data-state="active"`) for layout configuration and lifecycle states instead of BEM modifier classes (`.card--split`).
- **3-Tier Custom Property Scoping:** Map public API variables (`--abc-component-prop`) to internal private variables (`--_property`) at the component root selector to prevent cascade inheritance bleed to child components.
- **Theming & Polymorphism:** Components must consume dynamic `--theme-*` tokens (e.g., `--theme-color-surface`, `--theme-color-border`) rather than hardcoded generic variables.
- **Theme Locking:** For product-specific polymorphic components (like `directory_card`), their specific themes should be "locked in" by applying `data-product="directory"` to their root wrapper HTML, so they render correctly regardless of the page's global theme.