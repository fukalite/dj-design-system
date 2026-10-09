# Implementation Plan: Packaging, Engine & Architectural Hardening (`gallery_rebuild_09_arch_hardening_20261009`)

## Phase 1: Packaging, Build Pipeline & Core Component Engine Co-location Cleanup
- [x] **Task 1.1: Packaging & Release CI Hardening (`pyproject.toml`, `.github/workflows/publish*.yml`, `tests/test_ts_pipeline.py`)**
  - **Red Phase:** Add tests in `tests/test_ts_pipeline.py` asserting that `pyproject.toml` configures `artifacts = ["dj_design_system/components/**/*.js"]` for both `wheel` and `sdist` Hatch targets and that `.github/workflows/publish.yml` and `publish-test.yml` compile TypeScript before `uv build`.
  - **Green Phase:** Update `pyproject.toml`, `.github/workflows/publish.yml`, and `.github/workflows/publish-test.yml`.
- [x] **Task 1.2: `BaseComponent` Kwarg Validation, Lazy Co-located Template Fallback & `BlockComponent` Normalisation (`dj_design_system/components/base.py`)**
  - **Red Phase:** Add unit tests in `tests/test_components.py` verifying that passing an unknown keyword argument to `BaseComponent.__init__` raises `TypeError`, that `BlockComponent.__init__` automatically wraps `content` and `slots` values in `SafeString`, and that `BaseComponent.render()` resolves a co-located `.html` template even on an unregistered subclass.
  - **Green Phase:** Update `BaseComponent.__init__`, `BaseComponent.render`, and `BlockComponent.__init__` in `dj_design_system/components/base.py` (and fix `show_sandbox_link` in `UsageExample` so existing component views pass strict kwarg validation).
- [x] **Task 1.3: Strip Co-location Boilerplate Across All 26 Built-in `dds` Components (`dj_design_system/components/**`, `tests/components/**`)**
  - **Red Phase:** Update component unit tests in `tests/components/test_*.py` to assert co-located template/media resolution via `component_registry.get_info(Cls).template_name` and `Cls.get_media()` and verify no built-in component defines redundant `_template_name` or co-located `Media`.
  - **Green Phase:** Remove `template_name`, `_template_name`, co-located `class Media:`, and redundant `SafeString` `__init__` boilerplate from all 26 built-in `elements/` and `domain/` components; recompile TypeScript (`just build-ts`).
  - **Quality Check:** Run `dds-reviewer`, `just check`, `just typecheck`, and `just test`.
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Bug Fixes, HTML/JS Integrity & `Breadcrumb`/`Popout` Composition
- [x] **Task 2.1: Single-Pass Syntax Highlighting in `CanvasWidget` & Resize Race Fix in `canvas_widget.ts`**
  - **Red Phase:** Write failing unit tests in `tests/components/test_canvas_widget.py` proving that `CanvasWidget` preserves literal `<span class="...">` and `<pre>` tags in raw `rendered_html` / `source_code` without stripping them, and update `tests/test_views.py` / `tests/test_markdown_canvas.py` to expect raw strings passed to `CanvasWidget`.
  - **Green Phase:** Remove pre-highlighting before `CanvasWidget` in `views/component.py` and `services/markdown_canvas.py`; remove regex tag stripping in `CanvasWidget.get_context()`; update `canvas_widget.ts` to sync iframe height on `connectedCallback` and `load` when `iframe.contentDocument` is already ready; run `just build-ts`.
- [x] **Task 2.2: Search Index Deduplication, Search Debounce Fix & `ParamsForm` Declarative Fallback**
  - **Red Phase:** Add tests in `tests/components/test_search_box.py`, `tests/test_views.py`, and `tests/components/test_params_form.py` asserting that rendered gallery pages contain at most one `#gallery-search-index` element, `search_box.ts` invokes `handleInput()` inside its debounce timer callback, and `ParamsForm.get_context()` constructs zero HTML strings in Python.
  - **Green Phase:** Remove `{% gallery_search_index_script %}` from `gallery/base.html`, fix `onInput` debounce in `search_box.ts`, replace `SafeString(f'<input ...>')` in `params_form.py` with declarative markup in `params_form.html`, and clean up dead event code in `params_form.ts`.
- [x] **Task 2.3: Scoped `Tabs` DOM IDs & `Breadcrumb` `{% dds__popout %}` Composition**
  - **Red Phase:** Add tests in `tests/components/test_tabs.py` and `tests/components/test_breadcrumb.py` verifying `id_prefix` scoping on `Tabs` and verifying that `Breadcrumb` composes `{% dds__popout %}` and `{% dds__popout_option %}` (and declares any required media).
  - **Green Phase:** Add `id_prefix` to `Tabs`, update `breadcrumb.html` and `breadcrumb.css` to compose `{% dds__popout %}` + `{% dds__popout_option %}`, and update `conductor/code_styleguides/dds-components.md`.
  - **Quality Check:** Run `dds-reviewer`, `just build-ts`, `just check`, `just typecheck`, and `just test`.
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Consumer Theme Controller Isolation & `GalleryShell` Encapsulation
- [ ] **Task 3.1: Gallery Chrome `prefers-color-scheme` & Consumer-Only `ThemeSelect` Controller**
  - **Red Phase:** Write tests in `tests/test_views.py` and `tests/components/test_theme_select.py` asserting that `get_base_context()` does not derive `theme_body_class` from consumer `active_theme`, `ThemeSelect` does not use `"dark" in theme.lower()` to select moon/sun icons, `tokens.css` includes `@media (prefers-color-scheme: dark)` rules for `:root:not(.gallery-theme-light)`, and `gallery_shell.ts` updates `_dds_theme` without mutating `document.documentElement` / `document.body` theme classes.
  - **Green Phase:** Update `tokens.css`, `views/gallery.py`, `gallery/base.html`, `theme_select.py`, `theme_select.html`, `theme_select.ts`, and `gallery_shell.ts`.
- [ ] **Task 3.2: Decouple `GalleryShell` (`gallery_shell.ts` & `gallery_shell.css`) from Child Component Internals**
  - **Red Phase:** Add tests in `tests/components/test_sandbox_toolbar.py`, `tests/components/test_canvas_widget.py`, and `tests/components/test_gallery_shell.py` verifying `<dds-sandbox-toolbar>` custom element registration and event dispatch, `<dds-canvas-widget>` stage control methods/event handling, and absence of child-component internal selectors in `gallery_shell.css`.
  - **Green Phase:** Create `sandbox_toolbar.ts` (`<dds-sandbox-toolbar>`), extend `canvas_widget.ts` (`<dds-canvas-widget>`) to handle sandbox stage state, simplify `gallery_shell.ts`, and move child-reaching CSS rules from `gallery_shell.css` into `tabs.css`, `split_pane.css`, `sidebar.css`, and `<l-stack>` composition in `gallery/component.html`.
  - **Quality Check:** Run `dds-reviewer`, `just build-ts`, `just check`, `just typecheck`, and `just test`.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 4: Layered View Thinning, Typed Domain Dataclasses & Visual Baseline Verification
- [ ] **Task 4.1: Extract View Business Logic to Services & Introduce Frozen `ParamRowData` (`views/component.py`, `views/canvas.py`, `services/`, `data.py`)**
  - **Red Phase:** Write unit tests in `tests/test_views.py` and `tests/test_data.py` asserting that `views/component.py` and `views/canvas.py` define no private `_`-prefixed helper functions and that building parameter rows does not mutate `BaseParam` descriptors on component classes.
  - **Green Phase:** Add `ParamRowData` to `dj_design_system/data.py`, extract view helpers into `dj_design_system/services/gallery_context.py` and `dj_design_system/services/canvas.py`, and slim `views/component.py` and `views/canvas.py`.
- [ ] **Task 4.2: Replace Duck-Typing in `domain/` Components with Typed Data Normalisers (`data.py`, `components/domain/**`)**
  - **Red Phase:** Add tests in `tests/test_data.py` and `tests/components/` testing typed dataclass construction and normalisation for `NavTree`, `FolderListing`, `ParamsTable`, `ParamsForm`, `SandboxToolbar`, and `ThemeSelect`.
  - **Green Phase:** Refactor `domain/` component `get_context()` methods to use typed dataclasses / normalisers in `dj_design_system/data.py`.
- [ ] **Task 4.3: End-to-End, Visual Regression & Stacked PR Verification**
  - Run `dds-reviewer`, `just build-ts`, `just check`, `just typecheck`, `just test`, `just e2e`, and `just visual-run` (updating any affected visual baselines if needed and inspecting via `view_file`).
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
