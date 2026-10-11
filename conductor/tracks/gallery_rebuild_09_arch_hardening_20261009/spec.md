# Specification: Packaging, Engine & Architectural Hardening (`gallery_rebuild_09_arch_hardening_20261009`)

## Overview
Address all packaging, component engine, HTML/JS runtime, theme isolation, Web Component encapsulation, and layered-architecture issues identified across the 8-PR `gallery-rebuild` stack (`origin/main..gallery-rebuild/visual-polish`).

## Scope & Functional Requirements

### 1. Packaging, Build Pipeline & Core Component Engine Co-location (`pyproject.toml`, `.github/workflows/publish*.yml`, `components/base.py`, `components/**`)
- **Include Compiled `.js` Bundles in Wheel & Sdist Builds:**
  - Configure `[tool.hatch.build.targets.wheel]` and `[tool.hatch.build.targets.sdist]` in `pyproject.toml` with `artifacts = ["dj_design_system/components/**/*.js"]` so gitignored compiled Web Component bundles are packaged into releases.
  - Update `.github/workflows/publish.yml` and `.github/workflows/publish-test.yml` to set up Node.js, install npm dependencies (`npm ci`), and compile TypeScript (`npx tsc`) prior to `uv build`.
  - Add a packaging verification test in `tests/test_ts_pipeline.py` that inspects `pyproject.toml` Hatch artifact rules and verifies compiled `.js` files are included in package builds.
- **Reject Undeclared Keyword Arguments in `BaseComponent.__init__`:**
  - Validate that every keyword argument passed to `BaseComponent.__init__` corresponds to a declared `BaseParam` on the component class, raising `TypeError` for unknown keyword arguments so typos in template tags or Python instantiation fail fast.
- **Centralise `BlockComponent` Content & Slot `SafeString` Normalisation:**
  - Normalise `content` and `slots` values into `SafeString` inside `BlockComponent.__init__` (`dj_design_system/components/base.py`) so individual `BlockComponent` subclasses do not need boilerplate `__init__` overrides.
- **Zero-Boilerplate Co-location Across Built-in `dds` Components:**
  - Ensure `BaseComponent.render()` resolves co-located `.html` templates lazily if `_template_name` has not yet been bound on the class.
  - Remove redundant `template_name = ...`, `_template_name = template_name`, co-located `class Media:` declarations, and redundant `SafeString` `__init__` overrides across all 25 built-in `dds` components in `dj_design_system/components/elements/` and `dj_design_system/components/domain/`.

### 2. Bug Fixes, HTML/JS Integrity & Component Composition (`usage_example`, `canvas_widget`, `search_box`, `params_form`, `tabs`, `breadcrumb`)
- **Explicit `show_sandbox_link` Parameter on `UsageExample`:**
  - Add `show_sandbox_link = BoolParam(default=True, required=False)` to `UsageExample` (`dj_design_system/components/domain/usage_example/usage_example.py`) so `has_sandbox_link = bool(self.show_sandbox_link and preview_url and sandbox_href)` honours `show_sandbox_link=False` in `gallery/component.html`.
- **Single-Pass Syntax Highlighting in `CanvasWidget`:**
  - Pass raw unhighlighted source code and raw rendered HTML into `CanvasWidget` from `views/component.py` and `services/markdown_canvas.py`.
  - Remove the `<[^>]+>` regex HTML tag stripper from `CanvasWidget.get_context()` (`canvas_widget.py`) so `{% dds__code_block %}` highlights raw code once without corrupting component markup that contains `<span class="...">` or `<pre>`.
- **Fix `<dds-canvas-widget>` Iframe Resize Race (`canvas_widget.ts`):**
  - Update `DDSCanvasWidgetElement.connectedCallback()` (`canvas_widget.ts`) to inspect already-loaded `this.iframe.contentDocument` (measuring `.canvas-wrapper--basic` directly if `readyState === "complete"`) and listen for `iframe` `load` events so initial height reports sent before custom element upgrade are never lost.
- **Eliminate Duplicate `#gallery-search-index` & Fix Search Debounce (`search_box`, `gallery/base.html`):**
  - Remove `{% gallery_search_index_script %}` from `dj_design_system/templates/dj_design_system/gallery/base.html` so the search index JSON is rendered only once inside `<dds-search-box>` (`search_box.html`).
  - Fix `DDSSearchBoxElement.onInput` (`search_box.ts`) so `this.handleInput()` executes inside the `setTimeout` callback when typing (or immediately when clearing).
- **Eliminate Raw HTML String Construction in `ParamsForm` (`params_form.py`, `params_form.html`, `params_form.ts`):**
  - Remove `safestring.SafeString(f'<input type="text" id="{field_id}" name="{name}">')` from `ParamsForm.get_context()` and render fallback `<input>` markup declaratively in `params_form.html`.
- **Scope Tab/Panel DOM IDs in `Tabs` & Compose `Popout` in `Breadcrumb`:**
  - Add an optional `id_prefix = StrParam(default="dds", required=False)` to `Tabs` (`tabs.py`, `tabs.html`) so multiple `<dds-tabs>` instances on a page never collide on DOM IDs.
  - Refactor `breadcrumb.html` to compose `{% dds__popout %}` and `{% dds__popout_option %}` instead of inlining raw `<dds-popout>` markup, and update `conductor/code_styleguides/dds-components.md` to reflect `popout_option` and `tabs`.

### 3. Consumer Theme Controller Isolation & `GalleryShell` Encapsulation (`tokens.css`, `views/gallery.py`, `theme_select`, `sandbox_toolbar`, `canvas_widget`, `gallery_shell`)
- **Gallery Chrome Follows `prefers-color-scheme`; Topbar Theme Controller Controls Consumer Themes Only:**
  - Update `tokens.css` so dark gallery chrome tokens apply automatically under `@media (prefers-color-scheme: dark)` on `:root:not(.gallery-theme-light)` in addition to explicit `.gallery-theme-dark` (preserving visual test compatibility).
  - Keep `{% dds__theme_select %}` in its current topbar location in `Toolbar`, but make it strictly control the consumer's `GALLERY_THEMES` (`_dds_theme` query parameter, navigation links, HTMX params, and preview `iframe[src]` URLs).
  - Remove all `"dark" in theme.lower()` heuristics from `views/gallery.py`, `theme_select.py`, `theme_select.ts`, and `gallery_shell.ts`; stop toggling `.gallery-theme-dark` / `.gallery-theme-light` on `<html>` / `<body>` when the user switches consumer component themes.
- **Decouple `GalleryShell` from Child Component Internals (`gallery_shell.ts`, `gallery_shell.css`, `sandbox_toolbar`, `canvas_widget`, `split_pane`, `tabs`, `sidebar`):**
  - Introduce `<dds-sandbox-toolbar>` (`sandbox_toolbar.ts`) to manage its own popout triggers and toggle buttons and dispatch semantic custom events (`dds:sandbox-bg`, `dds:sandbox-viewport`, `dds:sandbox-zoom`, `dds:sandbox-toggle`, `dds:sandbox-reset`).
  - Move sandbox canvas state management (background class, viewport width, zoom scale, outline, measure overlay, RTL direction) into `<dds-canvas-widget>` (`canvas_widget.ts`) so `gallery_shell.ts` only coordinates shell-level drawer/navigation/tab/theme state.
  - Move child-internal CSS rules out of `gallery_shell.css` into their owning block stylesheets (`tabs.css`, `split_pane.css`, `sidebar.css`) and replace `.dds-usage-example + .dds-usage-example` sibling margins with Every Layout `<l-stack>` composition in `gallery/component.html`.

### 4. Layered Architecture, View Thinning & Typed Domain Dataclasses (`views/`, `services/`, `data.py`, `components/domain/`)
- **Thin Views & Service Extraction (`views/component.py`, `views/canvas.py`, `services/`):**
  - Move private `_`-prefixed helpers out of `views/component.py` and `views/canvas.py` into `dj_design_system/services/canvas.py` and `dj_design_system/services/gallery_context.py`, leaving view modules as pure HTTP request/response orchestrators per `conductor/code_styleguides/layered-architecture.md`.
- **Immutable `ParamRowData` Dataclass (No In-Place `BaseParam` Mutation):**
  - Replace `spec_param.type_name = _get_type_name(param_type)` in-place mutation of shared class-level `BaseParam` descriptors with a frozen `ParamRowData` dataclass in `dj_design_system/data.py`.
- **Typed Domain Normalisation Helpers & Dataclasses (`data.py`, `components/domain/`):**
  - Introduce clean typed dataclasses and conversion helpers in `dj_design_system/data.py` for domain component items (`ParamRowData`, `FormFieldRowData`, `ThemeOptionData`, `SandboxControlOptionData`, `BreadcrumbItemData`, `TabItemData`) to eliminate repetitive `isinstance`/`getattr` duck-typing chains in `domain/` `get_context()` methods.

### 5. Inbuilt Integration Test Harness & CI Wiring (`dj_design_system/testing/`, `tests/settings.py`, `tests/e2e/test_package_components.py`, `justfile`, `.github/workflows/ci.yml`)
- **Gallery Variant Iteration in `IterationEngine` & `PlaywrightAssessmentPlugin`:**
  - Enhance `IterationEngine.get_combinations()` (`dj_design_system/testing/engine.py`) so that when `variants is None`, it yields `"basic"`, `"maximal"`, and every named `Variant` defined in `comp.gallery_config.variants` (deduplicated, preserving order) for each component.
  - Enhance `PlaywrightAssessmentPlugin._navigate_to_component()` (`dj_design_system/testing/plugins.py`) so named `gallery.py` variants pass `variant=<variant_name>` in the `/_canvas/` query string alongside `_dds_theme`.
- **Internal Component Library Harness Configuration (`tests/settings.py`, `tests/e2e/test_package_components.py`, `example_project/tests/test_components.py`):**
  - Configure `DJ_DESIGN_SYSTEM["GALLERY_THEMES"]` in `tests/settings.py` with `"light"` (`html_attrs: {"html": {"class": "gallery-theme-light"}}`) and `"dark"` (`html_attrs: {"html": {"class": "gallery-theme-dark"}}`, `canvas_background: "dark-grey"`) so `IterationEngine` genuinely tests all 26 internal `dj_design_system` components across both light and dark themes (including Axe-core colour contrast and HTML validation across every `basic`, `maximal`, and `gallery.py` `Variant`).
  - Filter out internal `is_internal` components in `example_project/tests/test_components.py` so `just test-demo` assesses consumer showcase components cleanly.
- **CI Execution (`justfile`, `.github/workflows/ci.yml`):**
  - Ensure the internal component integration test harness (`tests/e2e/test_package_components.py`) is wired into `justfile` and executed in `.github/workflows/ci.yml`.

## Acceptance Criteria
- [x] `pyproject.toml` includes `dj_design_system/components/**/*.js` in wheel and sdist targets, and `publish.yml` / `publish-test.yml` build TypeScript before `uv build`.
- [x] `BaseComponent.__init__` raises `TypeError` on unknown keyword arguments.
- [x] All 26 built-in `dds` components omit redundant `template_name`, `_template_name`, co-located `class Media:`, and duplicate `BlockComponent.__init__` boilerplate.
- [x] `UsageExample` declares `show_sandbox_link`; `CanvasWidget` no longer strips HTML tags with regex or double-highlights code; `<dds-canvas-widget>` resizes deterministically on initial load without lost `postMessage` races.
- [x] `#gallery-search-index` appears at most once per page; `search_box.ts` properly debounces `handleInput()`; `ParamsForm` builds zero HTML strings in Python; `breadcrumb.html` composes `{% dds__popout %}` + `{% dds__popout_option %}`.
- [x] Gallery chrome inherits `prefers-color-scheme` (with `.gallery-theme-light`/`.gallery-theme-dark` overrides preserved), and `ThemeSelect` in the topbar controls only the consumer's `GALLERY_THEMES` (`_dds_theme`) with zero `"dark" in theme.lower()` heuristics.
- [x] `gallery_shell.ts` and `gallery_shell.css` no longer reach into child component internals; `<dds-sandbox-toolbar>` and `<dds-canvas-widget>` encapsulate sandbox controls and stage state.
- [x] `views/component.py` and `views/canvas.py` contain zero private `_`-prefixed business-logic helpers and never mutate `BaseParam` instances in-place.
- [x] `IterationEngine` and `PlaywrightAssessmentPlugin` exercise `basic`, `maximal`, and all `gallery.py` `Variant`s across `light` and `dark` themes for all 26 internal `dj_design_system` components with `AccessibilityPlugin` and `HTMLValidationPlugin` in CI.
- [x] `just check`, `just typecheck`, `just test`, `just e2e`, and `just visual-run` pass with 0 errors.
