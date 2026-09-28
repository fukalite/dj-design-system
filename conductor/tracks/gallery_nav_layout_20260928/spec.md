# Gallery Rebuild 3 — Navigation & Layout Components

## Overview
Part of the gallery rebuild series (see `gallery_visual_baseline_20260928` for the full list). This track builds the built-in components that make up the gallery's structure: the shell, sidebar, search, navigation tree, breadcrumb, toolbar, tabs, split panes and page containers.

**Depends on:** `gallery_foundation_20260928`, `gallery_primitives_20260928`.

Follows the conventions defined in `gallery_primitives_20260928/spec.md`: explicit `ui/` asset paths, `dds__` qualified names, existing `.gallery-*` classes and `--gallery-*` tokens, move-don't-copy CSS migration, and a gallery side-car for every component.

## Functional Requirements

### 1. Layout Components
| Component | Type | Replaces |
| --- | --- | --- |
| `GalleryShell` | Block (slots: `sidebar`, `toolbar`, `content`) | `.gallery` wrapper, `.gallery-main` and `.gallery-content-area` in `base.html`. Includes the mobile menu toggle and overlay. |
| `MobileMenuToggle` | Tag | CSS-only hamburger checkbox, label and overlay (`.gallery-hamburger`, `.gallery-overlay`). Keeps the no-JS behaviour. |
| `Sidebar` | Block (slots: `header`, `search`, `nav`) | `.gallery-sidebar` and its header/title. |
| `Toolbar` | Block (slots: `start`, `actions`) | `.gallery-toolbar`, breadcrumb area and actions area. |
| `SplitPane` | Block (slots: `primary`, `secondary`) | `.gallery-split` with documentation and sandbox panes, including pane headers and the wide/narrow responsive layout. |
| `Pane` | Block | `.gallery-split__pane` with `.gallery-split__pane-header` / `-body`. Params: `title`, `pane_id`, extra body attributes. |
| `Page` | Block | `.gallery-page` / `.gallery-docs` standalone page container. |
| `Prose` | Block | `.gallery-markdown` rich content container; owns `gallery-markdown.css` and `gallery-highlight.css`. |

### 2. Navigation Components
| Component | Type | Replaces |
| --- | --- | --- |
| `SearchBox` | Tag | Sidebar search input, results listbox and `gallery-search.js`. Reads the existing `gallery-search-index` JSON script. |
| `NavTree` | Tag | Recursive `navtree.html`. Takes the nav tree and `active_path`; renders app groups, `<details>` folders and leaf links, with icons via `Icon`. |
| `Breadcrumb` | Tag | `breadcrumb.html`, including the full path, the collapsed path and the CSS-only flyout. Takes a list of `{label, url}`. |
| `ThemeSelect` | Tag | Global gallery theme `<select>` and `gallery-theme.js`. Renders nothing when fewer than two themes are available. |
| `Tabs` | Tag | CSS radio tabs (`.gallery-tabs`) and `gallery-tabs.js`. Takes a list of `{id, label}` and the checked tab. |
| `FolderListing` | Tag | `.gallery-folder-list` with type icons. |

### 3. Behaviour Parity
- All existing JavaScript behaviour moves into component-owned JS files unchanged in function: search keyboard navigation, theme persistence, tab/hash syncing.
- CSS-only behaviours (hamburger, breadcrumb flyout, `<details>` folders) remain CSS-only.
- Element IDs relied on by JS or by consumers (`gallery-search-input`, `gallery-nav`, `gallery-sidebar-toggle`, `pane-docs`, `pane-sandbox`, etc.) are preserved.
- CSP nonce support is preserved for every script tag.

### 4. Recursive Rendering
`NavTree` must render recursively without the per-level template include cost growing unreasonably. Use a single template with a recursive include, or build the nested structure in `get_context()`, and add a test with a deep tree.

## Non-Functional Requirements
- **No visual change:** The track 0 visual baseline passes after every CSS move.
- **Accessibility:** ARIA roles and attributes (`listbox`, `aria-label`, `aria-current`, `aria-hidden`) match the legacy templates exactly.
- **Testing:** TDD per `workflow.md`; >80% coverage; e2e checks for search, tabs and theme switching still pass.

## Acceptance Criteria
- [ ] All fourteen components exist with templates, CSS/JS, docstrings and gallery side-cars.
- [ ] Their CSS/JS has been moved (not copied) out of the legacy assets.
- [ ] JS behaviour, element IDs and CSP nonce handling are preserved.
- [ ] The track 0 visual baseline passes; `just check`, `just test` and `just e2e` pass.

## Out of Scope
- Using these components in the gallery templates (track 5).
- Sandbox, canvas and parameter UI (track 4).
