# Gallery Rebuild 1 — Internal Component Foundation

## Overview
Part of the gallery rebuild series, which rebuilds the gallery UI (sidebar, navigation, toolbar, sandbox, canvas widget, pages) out of dj-design-system's own components. This track delivers no visible change. It adds support for **"internal" components** shipped by the package itself: components that are only reachable by their qualified name, never leak CSS/JS into consumer pages, and are hidden from the gallery unless explicitly enabled.

**Depends on:** `gallery_visual_baseline_20260928`.

### Track series
0. Visual Baseline & CI Visual Regression (`gallery_visual_baseline_20260928`)
1. **Internal Component Foundation** (this track)
2. Primitive Components
3. Navigation & Layout Components
4. Sandbox & Canvas Components
5. Page Composition & Legacy Asset Removal
6. Example Project Showcase & Documentation

Each track ships as its own PR and must leave the gallery visually identical to the track 0 baseline.

## Background & Risks Addressed
Adding components to the `dj_design_system` app naively would break consumer projects:

- **Short tag name collisions:** `ComponentRegistry.register_templatetags` registers every component's short name, and the last one discovered wins. A built-in `button` would either shadow the consumer's `{% button %}` or be shadowed by it (breaking the gallery), depending on `INSTALLED_APPS` order.
- **Ambiguous lookups:** `get_by_name()` / `resolve_component()` raise `MultipleComponentsFound` for ambiguous short names, so existing markdown `{% canvas %}` blocks referencing `button` would start failing.
- **Media leakage:** `get_merged_media()` feeds `{% component_stylesheets %}`, `{% component_scripts %}` and `markdown_canvas`. Gallery CSS/JS would be injected into every consumer canvas iframe and page.
- **Optional loader/finder:** Co-located component files only resolve when `ComponentsTemplateLoader` and `ComponentsStaticFinder` are configured, which is optional. The gallery must work without them.

## Functional Requirements

### 1. `components` Package
- Convert `dj_design_system/components.py` into a `dj_design_system/components/` package.
- Base classes move to `dj_design_system/components/base.py`. `dj_design_system/components/__init__.py` re-exports `BaseComponent`, `TagComponent`, `BlockComponent`, so `from dj_design_system.components import TagComponent` continues to work unchanged.
- Autodiscovery must not register the abstract base classes.
- Built-in components will live in subpackages (e.g. `components/primitives/`, `components/navigation/`, `components/layout/`, `components/sandbox/`) in later tracks.

### 2. Internal Components
A component is **internal** when either:
- it is discovered in the `dj_design_system` app, or
- its own `Meta` declares `internal = True` (allowing consumers to mark private components too).

`ComponentInfo` exposes an `is_internal` property. For internal components:
- **Template tags:** Only the qualified name is registered (e.g. `{% dds__navigation__breadcrumb %}`). The short name is never registered, so internal components cannot shadow or be shadowed by consumer tags. They are registered in the existing `design_components` library (no separate library needed).
- **Lookups:** `get_by_name(name)` without `app_label`, and `resolve_component()` short-name resolution, ignore internal components. They resolve only via their qualified name (or an explicit `app_label`).
- **Media:** Excluded from `get_merged_media()`, and therefore from `{% component_stylesheets %}`, `{% component_scripts %}` and markdown canvases. A new `get_internal_media()` (or equivalent) lets the gallery shell load them explicitly.
- **Qualified name prefix:** Built-in components use the `dds` prefix (e.g. `dds__primitives__button`) rather than `dj_design_system__…`, applied via the same mechanism as `COMPONENT_DIRECTORIES`, as a built-in default that consumer settings cannot accidentally remove.

### 3. Explicit Asset Paths for Built-ins
Built-in components do **not** use co-location. They declare explicit paths that resolve through Django's default machinery:

```
dj_design_system/components/navigation/breadcrumb.py
dj_design_system/templates/dj_design_system/ui/navigation/breadcrumb.html
dj_design_system/static/dj_design_system/ui/navigation/breadcrumb.css
```

```python
class Breadcrumb(TagComponent):
    template_name = "dj_design_system/ui/navigation/breadcrumb.html"

    class Media:
        css = "dj_design_system/ui/navigation/breadcrumb.css"
```

- The `ui/` namespace deliberately avoids `dj_design_system/components/…`, which is the namespace `ComponentsTemplateLoader` / `ComponentsStaticFinder` claim for the `dj_design_system` app.
- A test enforces this convention: no built-in component may rely on co-located `.html`, `.css` or `.js` files.

### 4. Gallery Visibility Settings
Two new settings:

| Setting | Default | Purpose |
| --- | --- | --- |
| `GALLERY_EXCLUDE_APPS` | `[]` | App labels hidden from the gallery. Generic — consumers can hide their own apps. |
| `GALLERY_SHOW_BUILTIN_COMPONENTS` | `False` | When `False`, `dj_design_system` is always excluded, regardless of `GALLERY_EXCLUDE_APPS`. |

- Effective exclusions = `GALLERY_EXCLUDE_APPS` ∪ (`{"dj_design_system"}` if `GALLERY_SHOW_BUILTIN_COMPONENTS` is `False`).
- A single helper (e.g. `get_gallery_components()` / `is_app_visible()`) is the only place this is computed. It is used by:
  - navigation tree building (`services/navigation.py`), and therefore the search index;
  - the `total_components` count on the index page;
  - `gallery_node` URL resolution (hidden apps return 404);
  - the REST API component listing (`api/views.py`).
- Hidden components remain usable as template tags; visibility affects the gallery only.
- The example project sets `GALLERY_SHOW_BUILTIN_COMPONENTS = True`. (The example project will have no built-in components to show until track 2.)

## Non-Functional Requirements
- **No visual change:** The track 0 visual baseline must pass at the end of this track.
- **Backwards compatibility:** Public import paths, existing settings, tag names and consumer behaviour are unchanged.
- **Testing:** TDD per `workflow.md`; >80% coverage of new code; `just check` and `just test` pass.

## Acceptance Criteria
- [x] The track 0 visual baseline passes.
- [x] `dj_design_system.components` is a package; existing imports work.
- [x] Internal components register only qualified tag names, prefixed `dds__` for built-ins.
- [x] Short-name lookups and `resolve_component()` ignore internal components.
- [x] Internal component media is excluded from merged media and consumer canvases.
- [x] `Meta.internal = True` marks a consumer component as internal.
- [x] `GALLERY_EXCLUDE_APPS` and `GALLERY_SHOW_BUILTIN_COMPONENTS` behave as specified across nav, search, count, node URLs and API.
- [x] A convention test forbids co-located assets for built-in components.
- [x] Example project sets `GALLERY_SHOW_BUILTIN_COMPONENTS = True`.

## Out of Scope
- Building any actual gallery components (tracks 2–4).
- Changing any gallery template (track 5).
- Documentation of the new settings (track 6), beyond docstrings.
