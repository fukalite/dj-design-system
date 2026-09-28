# Implementation Plan

## Phase 1: WCAG Accessibility Fixes
- [x] Task: Fix nested interactive controls (`<a>` inside `<summary>`) in `navtree.html` [9c8776d]
- [x] Task: Add `aria-current="page"` to active nav items [7b2c6f3]
- [x] Task: Fix inaccessible tab switcher radio inputs in `component.html` [0ab3ad5]
- [ ] Task: Fix auto-submit on variant selector (or event loop) for keyboard users
- [ ] Task: Add Escape key handlers to toolbar popouts
- [ ] Task: Make drawer resizer accessible to keyboard users
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: UI & Frontend Polish
- [ ] Task: Add missing CSS design tokens to `:root` and dark theme
- [ ] Task: Extract icon rendering logic in `navtree.html` to a reusable partial
- [ ] Task: Replace hardcoded CSS depth indentation with custom properties
- [ ] Task: Vendor HTMX locally to remove `unpkg.com` dependency
- [ ] Task: Fix BEM naming inconsistencies
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
