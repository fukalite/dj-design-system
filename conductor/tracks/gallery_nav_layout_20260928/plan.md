# Implementation Plan: Gallery Rebuild 3 — Navigation & Layout Components

Builds the gallery's structural components, moving their CSS/JS out of the legacy assets without visual or behavioural change.

## Phase 1: Layout Components [checkpoint: 07a8d4c]
- [x] Task: Write Failing Tests (`Red Phase`) [e6d2fa5]
  - [x] `GalleryShell`, `Sidebar`, `Toolbar`, `SplitPane`, `Pane`, `Page`, `Prose` render their slots with the legacy markup, classes and IDs.
  - [x] `MobileMenuToggle` renders the checkbox, label and overlay with the legacy IDs and ARIA.
- [x] Task: Implement to Pass Tests (`Green Phase`) [e6d2fa5]
  - [x] Implement components, templates and gallery side-cars.
  - [x] Move shell, sidebar, toolbar, split-pane, page, hamburger and responsive CSS, and the `.gallery-markdown` rules under `Prose`. (Spec correction: `gallery-markdown.css` is the markdown canvas widget's CSS, so it moves with that widget in track 4; `gallery-highlight.css` is the shared Pygments theme used by `CodeBlock`, docs `<pre>` and the canvas widget, so it moves once those are all components.)
- [x] Task: Refactor and Verify Coverage [e6d2fa5]
- [x] Task: Confirm the track 0 visual baseline passes. [07a8d4c]
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) [07a8d4c]

---

## Phase 2: `Breadcrumb`, `NavTree`, `FolderListing`
- [x] Task: Write Failing Tests (`Red Phase`) [a2e5cc4]
  - [x] `Breadcrumb` renders full and collapsed paths for 1, 2 and more than 2 crumbs.
  - [x] `NavTree` renders app groups, folders (open when on the active path), leaves, icons and active states; handles a deep tree.
  - [x] `FolderListing` renders folder, component and document icons.
- [x] Task: Implement to Pass Tests (`Green Phase`) [a2e5cc4]
  - [x] Implement components, templates and gallery side-cars (using sample nav data).
  - [x] Move breadcrumb, nav tree, depth indentation, nav icon and folder listing CSS.
- [x] Task: Refactor and Verify Coverage [a2e5cc4]
- [x] Task: Confirm the track 0 visual baseline passes. [4a87d6a]
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 3: `SearchBox`, `ThemeSelect`, `Tabs`
- [ ] Task: Write Failing Tests (`Red Phase`)
  - [ ] Each renders the legacy markup and IDs, and includes its script with CSP nonce support.
  - [ ] `ThemeSelect` renders nothing with fewer than two themes and marks the active theme as selected.
  - [ ] `Tabs` renders the given tabs with the correct one checked.
- [ ] Task: Implement to Pass Tests (`Green Phase`)
  - [ ] Implement components, templates and gallery side-cars.
  - [ ] Move `gallery-search.js`, `gallery-theme.js` and `gallery-tabs.js` into component assets, plus their CSS.
- [ ] Task: Refactor and Verify Coverage
- [ ] Task: Confirm the track 0 visual baseline passes and the e2e search, tabs and theme tests pass.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
