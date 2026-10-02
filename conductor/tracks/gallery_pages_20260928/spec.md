# Gallery Rebuild 5 — Page Composition & Legacy Asset Removal

## Overview
Part of the gallery rebuild series (see `gallery_visual_baseline_20260928` for the full list). With every piece built in tracks 2–4, this track rewrites the gallery page templates as compositions of built-in components and removes the remaining legacy CSS/JS.

**Depends on:** `gallery_primitives_20260928`, `gallery_nav_layout_20260928`, `gallery_sandbox_20260928`.

## Functional Requirements

### 1. Template Rewrite
Each gallery template is rewritten to compose `dds__*` components:

| Template | Composition |
| --- | --- |
| `gallery/base.html` | `GalleryShell` → `Sidebar` (`SearchBox`, `NavTree`) + `Toolbar` (`ThemeSelect`, breadcrumb block) + content block |
| `gallery/index.html` | `Page` + `Notice` (snapshot) |
| `gallery/folder.html` | `Page` + `FolderListing` + `Notice` (debug hint) |
| `gallery/documentation.html` | `Page` + `Prose` |
| `gallery/component.html` | `Tabs` + `SplitPane` → `Pane` (docs: `SectionHeading`, `Prose`, `UsageExample`, `ParamsTable`, `Divider`) + `Pane` (sandbox) |
| `gallery/sandbox_fragment.html` | `SandboxToolbar` (`Popout`, `PopoutOption`, `ToggleButton`) + `CanvasWidget` + `ParamsForm` (`FormRow`) |
| `canvas_widget.html` | Becomes a thin wrapper that renders `CanvasWidget`. Kept for backwards compatibility with `markdown_canvas.py` and any consumer includes. |

- **Template blocks preserved:** `title`, `extra_css`, `toolbar`, `breadcrumb`, `toolbar_actions`, `content` and `extra_js` keep their names and positions, so consumer templates that `{% extends %}` the gallery base keep working.
- **Legacy partials:** `breadcrumb.html`, `navtree.html` and `toolbar.html` become thin wrappers that render the corresponding component, so consumer `{% include %}`s keep working. They are marked deprecated in the changelog.
- **Deriving `UsageExample` from its example (design once #86 is in):** today `UsageExample` takes `code` and `preview_url` separately, so the caller must keep them describing the same example. Consider a parameter that takes the example itself and derives both, from the tag signature code and `build_canvas_url`. Design it after Marcel's #86 (`GalleryConfig` and named `Variant`s) has merged, because that changes what an example is, so a variant-shaped input (e.g. component + variant) is likely a better fit than a component instance. Notes from the discussion:
  - An instance loses which arguments were positional, the sample values and slot/block content. A `CanvasSpec` or variant keeps them.
  - Built-in gallery examples travel as URL query parameters and are edited in the sandbox form, so the parameter needs a string form and a form field, as `ModelParam` has with its primary key.
  - The preview URL also needs page state (the active theme, `mode=basic`), so it still needs a `theme` or the request.
- **Views:** Views build component-friendly context (e.g. tab lists, toolbar option lists) where the templates previously hard-coded markup. Viewport and zoom option lists move from the template into view context or component defaults.

### 2. Asset Loading
- `base.html` loads gallery assets solely through internal component media. No hard-coded `<link>`/`<script>` tags for gallery CSS/JS remain, except HTMX.
- HTMX is loaded only by pages that need it (the component page), as it is today.

### 3. Legacy Asset Removal
- `gallery.css`, `gallery-highlight.css`, `gallery-markdown.css` and any remaining legacy JS are deleted once empty. Any rules left over are either assigned to an owning component or proven unused and removed.
- `canvas.css` and `canvas-resize.js` (iframe side) remain, because they belong to the plain canvas iframe.
- Verify nothing else references the deleted files (templates, `save_canvas_pages.py`, docs, tests).

## Non-Functional Requirements
- **No visual or behavioural change:** The track 0 visual baseline and all e2e tests pass.
- **Backwards compatibility:** `.gallery-*` classes, `--gallery-*` tokens, template block names, element IDs and legacy include paths are preserved. Consumers who **override** (rather than extend) gallery templates may need to update; this is called out in the changelog.
- **Performance:** Page render time for the component page does not regress noticeably. Measure before and after on the example project.

## Acceptance Criteria
- [ ] Every gallery template is composed from built-in components.
- [ ] Template block names and legacy include paths still work.
- [ ] Legacy gallery CSS/JS files are deleted and unreferenced.
- [ ] The static demo export (`save_canvas_pages.py`) still works.
- [ ] The track 0 visual baseline passes; `just check`, `just test` and `just e2e` pass.

## Out of Scope
- Visual redesign of the gallery.
- Documentation updates (track 6).
