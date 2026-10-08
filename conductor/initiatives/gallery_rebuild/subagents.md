# Subagent Orchestration Strategy & Prompt Templates (`gallery_rebuild`)

To prevent context window exhaustion across Tracks 2–7, the main session acts strictly as **Conductor & Contract Keeper** while delegating file-heavy implementation, TypeScript compilation, CSS token authoring, and multi-styleguide code reviews to four single-responsibility subagents defined in `.agents/agents/`:

| Subagent Name | Definition File | Single Responsibility | Parallelisable? |
| :--- | :--- | :--- | :--- |
| `dds-css-architect` | [`.agents/agents/dds-css-architect.md`](../../../.agents/agents/dds-css-architect.md) | Global `@layer` cascade, Tier 1 (`--_dds-*`) & Tier 2 (`--dds-*`) tokens in `tokens.css`, Every Layout `<l-*>` / `.l-*` rules in `composition.css`, and CSS contract tests. | Single instance per CSS task |
| `dds-component-builder` | [`.agents/agents/dds-component-builder.md`](../../../.agents/agents/dds-component-builder.md) | One self-contained component vertical slice (`dj_design_system/components/<collection>/<name>/` — `.py`, `.html`, `.css`, `gallery.py`, `index.md`) + `tests/components/test_<name>.py`. | **Yes** (2–4 concurrent subagents across non-overlapping component directories) |
| `dds-ts-specialist` | [`.agents/agents/dds-ts-specialist.md`](../../../.agents/agents/dds-ts-specialist.md) | TypeScript build pipeline (`tsconfig.json`, `just build-ts`) and Light DOM `<dds-*>` custom elements (`<name>.ts`) + DOM/Playwright interaction tests. | **Yes** across distinct `<name>.ts` files once `tsconfig.json` exists |
| `dds-reviewer` | [`.agents/agents/dds-reviewer.md`](../../../.agents/agents/dds-reviewer.md) | End-of-phase `/code-review` audit across all 7 styleguides, direct refactoring of violations, and running `just test`, `just check`, and `mypy`. | Single instance at the end of each phase |

> **Fallback Note:** If starting a session where `.agents/agents/*.md` is not pre-loaded in `invoke_subagent`, either register the needed subagent once via `define_subagent` (copying the frontmatter/body from `.agents/agents/<name>.md` with `enable_write_tools=True`) or invoke `TypeName="self"` with the prompt templates below.

---

## 1. Orchestrator Rules (Keeping Main Context Lean)

1. **Never Read Every File in the Main Session:**
   - The main session reads only `conductor/tracks.md`, the active track's `metadata.json`, `spec.md`, and `plan.md`.
   - Do **not** read every styleguide or every component file in the main session—subagents read those in their own disposable context windows and return a <=25-line summary.
2. **Pre-Dispatch Contract Locking:**
   - Before spawning `dds-component-builder` or `dds-ts-specialist` subagents in a phase, the main session locks down the **Component Contract** in the prompt:
     - Exact tag name (`{% dds__<name> %}`) and root element (`<dds-name>` vs `<tag class="dds-name">`).
     - Exact Python parameters (`name`, type, default) and slots.
     - Child `{% dds__* %}` tags it composes (if any) and their parameter names.
     - Custom events (`dds:<event>`) and `data-*` / `aria-*` hooks shared between `<name>.html` and `<name>.ts`.
3. **Parallel Batching without File Contention:**
   - Leaf components (e.g. `icon`, `badge`, `notice`, `table`, `breadcrumb`, `form_field`) have zero dependencies on each other. Spawn up to 3–4 `dds-component-builder` subagents in a **single `invoke_subagent` call** with `Workspace="inherit"`.
   - Because each `dds-component-builder` is restricted to `dj_design_system/components/<collection>/<name>/` and `tests/components/test_<name>.py`, parallel subagents never edit the same file.
   - Composite components that invoke a child component (e.g. `toolbar` invoking `{% dds__search_box %}` and `{% dds__theme_select %}`) are dispatched **after** their child components exist, or with the child's exact tag signature locked in the prompt.
4. **End-of-Phase Drift Consolidation & Workaround Cleanup:**
   - Because parallel subagents operate within strict file boundaries, they may introduce local workarounds when a shared file (`types.ts`, `tokens.css`, `conftest.py`) needs an export or token outside their boundary, reporting it back under **Drift Notes**.
   - At the end of **every phase** (before committing the phase):
     1. **Consolidate Reported Drift:** Collect all drift notes and workarounds reported by the phase's subagents.
     2. **Fix Root Causes & Strip Workarounds:** Apply the canonical fix in the shared module (e.g. exporting `DDSCustomElement` in `dj_design_system/components/types.ts`) and remove any local shims/workarounds (e.g. `declare module` blocks) from the subagent-authored files.
     3. **Update Specs, Plans & `[DRIFT & CONTEXT NOTES]`:** Update `subagents.md` and relevant track `spec.md` / `plan.md` files so downstream phases inherit the clean contract, and mark completed phase tasks `[x]` in `plan.md`.
     4. **Run Phase Review & Commit:** Run `dds-reviewer` (`/code-review`), `just build-ts`, `just test`, `just check`, and `just typecheck`, then create a dedicated phase commit.

### Canonical Shared Contracts & Drift Ledger
- **`dj_design_system/components/types.ts`:** Exports `DdsCustomEventDetail` and `DDSCustomElement` (`connectedCallback(): void; disconnectedCallback(): void`). Subagents must import `type { DDSCustomElement } from '../../types.js';` directly—never add `declare module` augmentations in `<name>.ts`.
- **`ListParam` / `DictParam` Defaults & Normalisation (`python.md`):** Never pass a mutable default (`default=[]` or `default={}`) or `default=list`; when `required=False`, pass `default=None` and normalise `list(self.items) if self.items is not None else []` inside `get_context()` (always use `is not None` rather than implicit boolean evaluation `if self.items` so lazy iterables/QuerySets are not prematurely evaluated).
- **Module-Level Constants (`python.md`):** Always define module-level collection constants as immutable tuples `(...)` rather than mutable lists `[...]`, converting with `list(...)` only when passing `choices=` to a `BaseParam`.
- **`StrParam` Receiving Domain Objects (`Variant`, etc.):** Because `BaseParam.__set__` validates `isinstance(value, str)` inside `BaseComponent.__init__`, any `StrParam` that may receive a `Variant` instance or object with `.name` (e.g. `active_variant`) must normalise `kwargs["active_variant"] = str(getattr(raw, "name", raw))` in `__init__` before calling `super().__init__(**kwargs)`.
- **`BlockComponent` with `Meta.slots`:** `BlockComponent.get_context()` populates individual slot names rather than a `slots` dict, and `BlockComponent.__init__` sets `self.content = None` when `has_slots()` is `True`. Components referencing `{{ slots.<name> }}` or `{{ content }}` in templates must normalise `normalized_slots = {name: safestring.SafeString(val) if val else val for name, val in (slots or {}).items()}` and `normalized_content = safestring.SafeString(content) if content is not None else ""` in `__init__` **before** calling `super().__init__(content=normalized_content, slots=normalized_slots, **kwargs)`, set `self.content = normalized_content` immediately after `super().__init__`, and set `context["slots"] = self.slots` and `context["content"] = self.content or ""` in `get_context()`. In Django templates, any block body inside a `BlockComponent` that declares `Meta.slots` must be wrapped in `{% slot "<name>" %}...{% endslot %}` tags (for example, `{% dds__popout %}` declares optional `"trigger"` and `"menu"` slots).
- **`BaseComponent.get_context()` / `get_classes_string()` (`dj_design_system/components/base.py`):** Iterates `type(self).get_params().items()` rather than `self.params.items()` so components defining a parameter named `params` (e.g. `ParamsTable`, `ParameterControls`) can call `super().get_context()` directly without shadowing the parameter descriptor map. Notice that mypy requires `# type: ignore[assignment]` when a subclass defines `params = parameters.ListParam(...)`.
- **`dds__icon` Contract (`dj_design_system/components/elements/icon/`):** Exports `Icon` and `ICON_NAMES` (26 icons: `external-link`, `eye`, `code`, `file-code`, `monitor`, `box-model`, `ruler`, `rtl`, `component`, `doc`, `folder`, `folder-open`, `search`, `menu`, `close`, `chevron-right`, `chevron-down`, `copy`, `check`, `sun`, `moon`, `reset`, `info`, `success`, `warning`, `error`). Accepts `name` (positional), `size` (`xs`, `sm`, `md`, `lg`), `label`.

---

## 2. Adaptable Subagent Prompt Templates

### Template A: `dds-css-architect` (Track 2 Phase 1 & Token/Layout Updates)
```markdown
## Task
Implement the global CSS cascade, 3-Tier Design Token System, and Every Layout composition primitives for Track 2 Phase 1.

## Assigned Files (Strict Boundary)
- Create/Edit:
  - `dj_design_system/static/dj_design_system/tokens.css`
  - `dj_design_system/static/dj_design_system/composition.css`
  - `dj_design_system/static/dj_design_system/gallery.css` (prepend `@layer` order and `@import` rules only; do not delete legacy rules yet—that happens in Track 6)
  - `tests/test_dds_tokens_and_layout.py`

## Specifications
1. Read `conductor/code_styleguides/dds-components.md` (Sections 4, 5, 6) and `conductor/code_styleguides/html-css.md`.
2. Follow TDD:
   - First write `tests/test_dds_tokens_and_layout.py` asserting:
     - `@layer reset, tokens, global, composition, blocks, utilities;` is declared.
     - All Tier 1 (`--_dds-*`) tokens are defined only on `:root`.
     - All Tier 2 (`--dds-*`) tokens across all 6 domains (`layer`/`surface`, `font`/`text`, `space`/`layout`, `state`, `control`, `status`) are defined on `:root` and `.gallery-theme-dark`.
     - All 8 `[data-surface='<name>']` scopes (`stage`, `code`, `docs`, `sandbox`, `topbar`, `sidebar`, `popout`, `overlay`) alias only Tier 2 `--dds-*` tokens (zero `--_dds-*` references inside `[data-surface]`).
     - All 11 Every Layout primitives (`l-stack`, `l-cluster`, `l-sidebar`, `l-switcher`, `l-box`, `l-center`, `l-cover`, `l-frame`, `l-grid`, `l-reel`, `l-imposter` and matching `.l-*` classes) are defined in `@layer composition`.
   - Implement `tokens.css` and `composition.css` and run `just test` and `just check`.

## [DRIFT & CONTEXT NOTES]
- Do not define `@pytest.fixture` inside `tests/test_dds_tokens_and_layout.py` (use module-level helper functions per `python.md`).
- <Insert any additional notes discovered in session>
```

---

### Template B: `dds-component-builder` (Tracks 3, 4, 5 — Per-Component Vertical Slice)
```markdown
## Task
Build the co-located `dds__<name>` component in `dj_design_system/components/<collection>/<name>/` and its unit tests in `tests/components/test_<name>.py`.

## Assigned Files (Strict Boundary — Do Not Touch Other Files)
- `dj_design_system/components/<collection>/<name>/__init__.py`
- `dj_design_system/components/<collection>/<name>/<name>.py`
- `dj_design_system/components/<collection>/<name>/<name>.html`
- `dj_design_system/components/<collection>/<name>/<name>.css`
- `dj_design_system/components/<collection>/<name>/gallery.py`
- `dj_design_system/components/<collection>/<name>/index.md`
- `tests/components/test_<name>.py`

## Component Contract
- **Class & Tag Type:** `<ClassName>(TagComponent | BlockComponent)` → registered as `{% dds__<name> %}`
- **Root Selector:** `<root_element_and_class, e.g. <button class="dds-button"> or <dds-tabs class="dds-tabs">>`
- **Parameters:**
  - `<param_name>`: `<ParamType(default=..., description=...)>`
- **Slots (if BlockComponent):**
  - `<slot_name>`: `<Slot(...)>`
- **Context Shaping (`get_context()`):**
  - `<Specify any parameter interaction, e.g. icon_only=True requires label for aria-label>`
- **Child Components / Every Layout Primitives Used in `<name>.html`:**
  - `<e.g. {% dds__icon name=icon_name %}, <l-cluster>>`
- **Tier 3 Tokens (`--_<component>-*` in `<name>.css`):**
  - Map exclusively from Tier 2 `--dds-*` tokens defined in `dj_design_system/static/dj_design_system/tokens.css`.

## [DRIFT & CONTEXT NOTES]
- Read `conductor/code_styleguides/dds-components.md`, `conductor/code_styleguides/python.md`, and `conductor/code_styleguides/html-css.md` before writing code.
- **Python Imports & Defaults (`python.md`):** Never import classes, functions, or constants directly (e.g. `from dj_design_system.components import TagComponent` is forbidden). Always import modules/submodules (`import typing`, `from dj_design_system import components, gallery, parameters, slots`, `from dj_design_system.components.elements import icon as icon_element`) and reference `components.TagComponent`, `parameters.StrParam`, `icon_element.ICON_NAMES`, etc. Never import the same module with both `import x` and `from x import y`. Never use mutable defaults (`default=[]` or `default={}`) on `ListParam` or `DictParam`—use `default=None` when `required=False`. Always use keyword arguments when calling functions (`safestring.mark_safe(s=val)`).
- **Component Methods & Booleans (`layered-architecture.md` & `python.md`):** Do not define private helper methods (`def _foo(...)`) on Component classes (Gemini Code Review flags private methods on interface layer classes). Keep `get_context()` self-contained. Use implicit boolean evaluation (`not self.label`) instead of `not bool(self.label)`.
- **TypeScript Imports, Strings & JSDoc (`javascript.md`):** Always include the `.js` extension in relative TypeScript imports, use single quotes (`'`) for all string literals (`import type { DDSCustomElement } from '../../types.js';`), and include JSDoc comments on all classes, fields (including private fields), and methods.
- Never define `@pytest.fixture` inside `tests/components/test_<name>.py`; use module-level helper functions.
- Run `just test-file tests/components/test_<name>.py` and `just check`.
- <Insert any additional drift notes from earlier phases>
```

---

### Template C: `dds-ts-specialist` (Track 2 Phase 2 & Interactive `<dds-*>` Custom Elements)
```markdown
## Task
<Either: "Configure the TypeScript build pipeline (`tsconfig.json`, `just build-ts`)" OR "Implement the Light DOM `<dds-name>` custom element in `dj_design_system/components/<collection>/<name>/<name>.ts` and its tests">

## Assigned Files (Strict Boundary)
- `<List exact .ts, tsconfig.json, justfile, or test files>`

## Custom Element Contract (when implementing `<name>.ts`)
- **Custom Element Tag:** `<dds-name>`
- **DOM Queries (within `this` only):** `<e.g. [data-trigger], [role='tab'], iframe>`
- **State / ARIA Mutations:** `<e.g. aria-expanded, aria-selected, data-state='open'>`
- **Bubbling CustomEvents Dispatched:** `<e.g. dds:tab-change, dds:theme-change, dds:params-change>`
- **Lifecycle Cleanup:** Abort instance `AbortController` in `disconnectedCallback()` for all listeners and observers.

## [DRIFT & CONTEXT NOTES]
- Read `conductor/code_styleguides/dds-components.md` (Section 7) and `conductor/code_styleguides/javascript.md`.
- Always include the `.js` extension in relative TypeScript imports, use single quotes (`'`) for all string literals (`import type { DDSCustomElement } from '../../types.js';`), and include JSDoc comments on all classes, fields (including private fields), and methods.
- Compiled `<name>.js` files in `dj_design_system/components/**/*.js` are gitignored; verify compilation via `just build-ts`.
- <Insert any additional drift notes from earlier phases>
```

---

### Template D: `dds-reviewer` (End-of-Phase Quality & Architecture Gate)
```markdown
## Task
Execute the `/code-review` audit on all files created or modified in the current phase before the phase checkpoint.

## Target Files to Audit
- `<List directories/files touched in this phase>`

## Audit Instructions
1. Read `conductor/code_styleguides/dds-components.md`, `conductor/code_styleguides/example-project.md` (if `example_project/` was touched), `conductor/code_styleguides/general.md`, `conductor/code_styleguides/python.md`, `conductor/code_styleguides/layered-architecture.md`, `conductor/code_styleguides/html-css.md`, and `conductor/code_styleguides/javascript.md`.
2. Inspect every target file against the styleguides:
   - Check 100% co-location (`<name>.py`, `<name>.html`, `<name>.css`, `<name>.ts`, `gallery.py`, `index.md`).
   - Check zero BEM (`__` or `--`), `@layer blocks` wrapping, `margin: 0` on component roots, and Tier 3 `--_<component>-*` tokens mapped exclusively from Tier 2 `--dds-*` tokens.
   - Check Python-biased `get_context()` (no template filters for value computation, no `.render()` in Python, no `services/` imports in components).
   - Check Python module-only imports (`from dj_design_system import components, gallery, parameters, slots`; zero direct class/constant imports; zero duplicate `import` + `from ... import` of the same module) and TypeScript `.js` import extensions (`from "../../types.js"`).
   - Check test files for zero inline `@pytest.fixture` decorators and module-level imports.
3. Immediately fix any violations found using IDE edit tools.
4. Run `just test`, `just check`, and `just typecheck`.
5. Return a <=25-line summary of fixes applied and verification output. Do NOT run any `git` stage/commit commands.

## [DRIFT & CONTEXT NOTES]
- **Track 6 Phase 1 Consolidation:**
  - `build_script_tags()` in `dj_design_system/services/media.py` emits `type="module"` when `is_module=True` or when a script path starts with `dj_design_system/components/`.
  - `dj_design_system_gallery` template tag library exposes `{% internal_component_stylesheets %}`, `{% internal_component_scripts %}`, and `{% gallery_search_index_script %}` (`id="gallery-search-index"`, matching `dds__search_box` default `index_id`).
  - Gallery views (`dj_design_system/views/gallery.py` and `dj_design_system/views/component.py`) pre-compute `theme_body_class`, `total_components_label`, `component_tabs`, `declared_slots`, and `sandbox_reset_url` (`f"{node.url}#pane-sandbox"`) in Python so all 7 page templates remain 100% free of template filters (`|`) and BEM classes (`__` / `--`).
  - `<dds-gallery-shell>` (`gallery_shell.ts`) coordinates `#pane-sandbox` / `#param-*` hash navigation, `[data-tab-trigger]` pane switching, `dds:theme-change` iframe/cookie/URL sync, `[data-sandbox-control]` popout selection/restoration (`sessionStorage['dds_toolbar_state']`), `[data-action]` sandbox toggles, and `canvas-resize` message resizing.
```
