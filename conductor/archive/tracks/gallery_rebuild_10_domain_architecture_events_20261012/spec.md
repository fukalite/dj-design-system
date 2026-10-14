# Specification: Domain Component Architecture, Event Decoupling & Shell Mediator (`gallery_rebuild_10_domain_architecture_events_20261012`)

## Overview
Establish a clean **Mediator (Smart Shell & Focused Page Managers, Thin Self-Contained Widgets)** architecture across the built-in Component Gallery composite collection (`theme_select`, `search_box`, `sandbox_params`, `nav_tree`, `sandbox_toolbar`, `canvas_widget`), the `popout` element primitive, and the page-level scripts in `dj_design_system/static/dj_design_system/`.

Composite components are legitimately domain-aware—they understand component trees, canvas viewports, and sandbox parameters. However, their current client-side scripts suffer from severe architectural overreach: leaf widgets act as autonomous application controllers that write cookies, hijack `window.location.href`, penetrate preview iframe DOMs, pierce child custom elements, and attach un-scoped document-level listeners. Meanwhile, page-level scripts in `static/dj_design_system/` consist of a 946-line monolithic `gallery-shell.ts` alongside legacy untyped `.js` IIFEs (`canvas-resize.js` and `gallery-snapshot-notice.js`).

This track decouples all global browser side-effects (cookies, web storage, URL query routing, global keyboard shortcuts, and iframe stage synchronisation) out of composite components into focused, testable TypeScript managers orchestrated by [`<dds-gallery-shell>`](file:///home/marcel/projects/dj-design-system/dj_design_system/static/dj_design_system/gallery-shell.ts), upgrades all page-level and iframe scripts to strict TypeScript, and leaves composite components as thin, event-driven widgets that communicate exclusively via attributes, public methods, slots, and standard bubbling `CustomEvent`s.

---

## Architectural Principles: Thin Composites & Modular Page Managers

```
┌────────────────────────────────────────────────────────────────────────────┐
│                   <dds-gallery-shell> (Orchestrator)                       │
│  ┌────────────────────┐ ┌──────────────────────┐ ┌──────────────────────┐  │
│  │   ThemeManager     │ │   SandboxManager     │ │  PaneAndNavManager   │  │
│  │ (UI/consumer theme,│ │ (sessionStorage,     │ │ (drawer, tabs/split, │  │
│  │  colour scheme,    │ │  variant URL routing,│ │  hash routing, '/'   │  │
│  │  cookies, storage, │ │  toolbar <-> canvas  │ │  search hotkey,      │  │
│  │  iframe sync)      │ │  stage coordination) │ │  snapshot notice)    │  │
│  └─────────┬──────────┘ └──────────┬───────────┘ └──────────┬───────────┘  │
└────────────┼───────────────────────┼────────────────────────┼──────────────┘
             │ (Events & Methods)    │ (Events & Methods)     │ (Events & Methods)
             ▼                       ▼                        ▼
┌──────────────────────┐  ┌─────────────────────────┐  ┌─────────────────────┐
│  <dds-theme-select>  │  │  <dds-sandbox-toolbar>  │  │  <dds-search-box>   │
│  <dds-canvas-widget> │  │  <dds-sandbox-params>   │  │  <dds-nav-tree>     │
│  (Thin local UI)     │  │  (Thin local UI)        │  │  (Thin local UI)    │
└──────────────────────┘  └─────────────────────────┘  └─────────────────────┘
```

1. **Domain Semantics Allowed:** Composite components may accept domain-level data structures (`ThemeOption`, `NavTreeNode`, `SearchIndexEntry`, `SandboxControlOption`) and use domain terminology.
2. **Zero Global Side-Effects in Composites:** Composite custom elements must never mutate `document.cookie`, `window.localStorage`, `window.sessionStorage`, or `window.location.href`.
3. **Outward Communication via Bubbling Events, Inward via Methods/Attributes:** State transitions are communicated upwards solely through standard, bubbling `dds:*` `CustomEvent`s with typed details; managers update widgets via public methods or declarative attributes.
4. **Focused Page-Level Managers:** Instead of a single 1,000+ line God class, `dj_design_system/static/dj_design_system/` decomposes page-level responsibilities into focused TypeScript manager modules (`theme-manager.ts`, `sandbox-manager.ts`, `pane-manager.ts`) orchestrated by `gallery-shell.ts`, plus a typed `canvas-resize.ts` inside preview iframes.

---

## Detailed Functional & Architectural Requirements

### 1. Theme Selection, Storage Decoupling & `ThemeManager` (`theme_select` & `static/`)
- **Remove Cookie & LocalStorage Mutation from `theme_select.ts`:**
  - Strip `document.cookie` and `window.localStorage.setItem('dds_theme', ...)` from [`DDSThemeSelectElement`](file:///home/marcel/projects/dj-design-system/dj_design_system/components/gallery/composites/theme_select/theme_select.ts).
  - Component solely updates `this.dataset.activeTheme` and dispatches `new CustomEvent('dds:theme-change', { bubbles: true, detail: { theme } })`.
- **Extract `ThemeManager` (`static/dj_design_system/theme-manager.ts`):**
  - Centralise gallery UI theme (`desert` / `classic`, light/dark chrome) and consumer theme / colour scheme persistence (`document.cookie`, `localStorage`, `_dds_theme` / `_dds_color_scheme` URL query parameters, hidden `<input>` syncing, and `iframe[src]` / `srcdoc` updates) into a dedicated `ThemeManager` delegated by `DDSGalleryShellElement`.
- **Typed `ThemeOption` Dataclass:**
  - Export a co-located `@dataclasses.dataclass(frozen=True) class ThemeOption:` (`value: str`, `label: str`, `icon: str = "sun"`, `supports_dark_mode: bool = False`) from `theme_select.py` and `__init__.py`.

### 2. Search Box Global Hotkey, Combobox A11y & `PaneManager` (`search_box` & `static/`)
- **Decouple Document-Level Keydown Listener:**
  - Remove unconditional, un-scoped `document.addEventListener('keydown')` for `'/'` from [`search_box.ts`](file:///home/marcel/projects/dj-design-system/dj_design_system/components/gallery/composites/search_box/search_box.ts).
  - Expose a public `focusInput(): void` method on `DDSSearchBoxElement`.
  - Coordinate global `'/'` and `⌘K` / `Ctrl+K` hotkey focus from the shell/pane manager so multi-instance previews never hijack focus.
- **WAI-ARIA Combobox Accessibility Implementation:**
  - Implement complete WAI-ARIA 1.2 Combobox pattern: generate deterministic unique `id`s (`${resultsId}-option-${idx}`) for search result options and dynamically update `aria-activedescendant` on the `<input>` as arrow keys are pressed (clearing it on reset/close).
  - Automatically scroll active options into view (`scrollIntoView({ block: 'nearest' })`) when available.
- **Typed `SearchIndexEntry` Dataclass:**
  - Export `@dataclasses.dataclass(frozen=True) class SearchIndexEntry:` (`label: str`, `url: str = ""`, `type: str = ""`, `breadcrumb: str = ""`, `content: str = ""`) in `search_box.py` and `__init__.py`.
- **Extract `PaneManager` & Fold `gallery-snapshot-notice.js`:**
  - Extract drawer toggling, tab/split-pane hash routing (`#pane-sandbox`, `#param-*`), global search shortcut coordination, and static snapshot notice visibility (`#static-snapshot-notice`) into `pane-manager.ts` (orchestrated by `gallery-shell.ts`), removing the standalone legacy `gallery-snapshot-notice.js` script tag from `base.html`.

### 3. Popout Encapsulation & Sandbox Toolbar Decoupling (`popout` & `sandbox_toolbar`)
- **Enhance `DDSPopoutElement` (`elements/popout/popout.ts`):**
  - When a `[role="menuitemradio"]` option is selected in `<dds-popout>`, automatically update `[data-popout-trigger] > span` with the option's label text and include `{ value, label }` in the `dds:popout-select` event detail.
  - Expose a public `selectValue(value: string): void` method on `DDSPopoutElement` that updates `[data-popout-option]` `aria-checked` states and the trigger `<span>` label without dispatching an event.
- **Eliminate URL Hijacking, Storage & Child DOM Piercing in `sandbox_toolbar.ts`:**
  - Remove `window.location.href = ...` mutations, query parameter parsing, and `#pane-sandbox` hash evaluations from [`sandbox_toolbar.ts`](file:///home/marcel/projects/dj-design-system/dj_design_system/components/gallery/composites/sandbox_toolbar/sandbox_toolbar.ts). Emit a bubbling `dds:sandbox-variant` `CustomEvent` with `{ variant: value }`.
  - Remove queries into child `dds-popout` DOM internals (`[data-popout-trigger] > span`, `[data-value]`); call child `popout.selectValue(value)` via `applyState(state)` instead.
  - Remove `sessionStorage` (`'dds_toolbar_state'`) reads/writes from `sandbox_toolbar.ts`; expose `applyState(state)` so `SandboxManager` restores and coordinates toolbar state.
  - Export co-located typed `@dataclass(frozen=True) class SandboxControlOption:` in `sandbox_toolbar.py` and `__init__.py`.

### 4. Canvas Widget, Iframe `postMessage` Protocol & `SandboxManager` (`canvas_widget`, `canvas-resize.ts`, `sandbox-manager.ts`)
- **Eliminate Preview Iframe DOM Penetration in `canvas_widget.ts`:**
  - Remove all code in [`canvas_widget.ts`](file:///home/marcel/projects/dj-design-system/dj_design_system/components/gallery/composites/canvas_widget/canvas_widget.ts) that inspects `iframe.contentDocument` to mutate `.canvas-wrapper` classes, inject `<style id="dds-outline-style">` / `<style id="dds-measure-style">`, set `wrapper.style.zoom`, or mutate `dir="rtl"`.
  - Remove document-level listeners for sibling `<dds-sandbox-toolbar>` events (`dds:sandbox-*`), `data-canvas-id="sandbox"` special-casing, and `sessionStorage` lookups from `canvas_widget.ts`.
  - Keep `DDSCanvasWidgetElement` focused on local mode toggling (`preview` / `code` / `html`), `canvas-resize` height handling, `setViewport()`, `setBackground()`, `setZoom()`, and `setStageState()`, posting `{ type: 'dds:canvas-stage', ... }` to `iframe.contentWindow.postMessage(...)`.
- **Upgrade `canvas-resize.js` to TypeScript (`static/dj_design_system/canvas-resize.ts`) & `canvas.css`:**
  - Convert `canvas-resize.js` to strict TypeScript `canvas-resize.ts` (compiled to `canvas-resize.js`).
  - Handle incoming `{ type: 'dds:canvas-stage', background, zoom, outline, measure, rtl }` `postMessage` payloads inside the iframe document by updating `.canvas-wrapper` classes/styles, `[data-canvas-outline]`, `[data-canvas-measure]`, and `document.documentElement.dir`, backed by clean rules in `canvas.css`.
- **Create `SandboxManager` (`static/dj_design_system/sandbox-manager.ts`):**
  - Listen for bubbling `dds:sandbox-bg`, `dds:sandbox-viewport`, `dds:sandbox-zoom`, `dds:sandbox-toggle`, `dds:sandbox-variant`, and `dds:sandbox-reset` events on the shell.
  - Manage `sessionStorage` (`'dds_toolbar_state'`) persistence, coordinate state across `<dds-sandbox-toolbar>` (`applyState`) and `<dds-canvas-widget>` (`setStageState`), and handle variant URL navigation and parameter form reset.

### 5. HTMX & Client-Side Loop Harmonisation (`sandbox_params`)
- **Resolve Reactive Loop Contradiction:**
  - Harmonise client-side input debouncing in `DDSSandboxParamsElement` so `dds:params-change` dispatches serialized parameter values for programmatic callers without triggering redundant HTMX submission loops.
- **Remove Leaked Application Query Parameters & Host DOM Coupling:**
  - Remove hardcoded hidden inputs for `_iss`, `_dds_theme`, and `_dds_variant` from `sandbox_params.html`; provide a named `{% slot "extra_inputs" %}` slot populated by `templates/dj_design_system/gallery/panes/sandbox.html`.
  - Remove hardcoded `DEFAULT_HX_TARGET = "closest [data-gallery-sandbox-body]"` from `sandbox_params.py`; default `hx_target` to `""` (omitted when empty) and pass `hx_target="[data-gallery-sandbox-body]"` explicitly in `panes/sandbox.html`.

### 6. Navigation Tree Data Contract & Semantic Structure (`nav_tree`)
- **Export Typed `NavTreeNode` Dataclass:**
  - Define and export `@dataclasses.dataclass(frozen=True) class NavTreeNode:` from `nav_tree.py` and `__init__.py`.
  - Eliminate direct coupling to `data.NavItemInputData` inside `nav_tree.py`.

