# Implementation Plan

## Phase 1: WCAG Accessibility Fixes
- [x] Task: Fix nested interactive controls (`<a>` inside `<summary>`) in `navtree.html` [9c8776d]
- [x] Task: Add `aria-current="page"` to active nav items [7b2c6f3]
- [x] Task: Fix inaccessible tab switcher radio inputs in `component.html` [0ab3ad5]
- [x] Task: Fix auto-submit on variant selector (or event loop) for keyboard users [55e73ae]
- [x] Task: Add Escape key handlers to toolbar popouts [2602036]
- [x] Task: Make drawer resizer accessible to keyboard users [122bcd7]
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) [a3c8a55]

## Phase 2: UI & Frontend Polish
- [x] Task: Add missing CSS design tokens to `:root` and dark theme [1be5be1]
- [x] Task: Extract icon rendering logic in `navtree.html` to a reusable partial [f68e6d3]
- [x] Task: Replace hardcoded CSS depth indentation with custom properties [cb8da7c]
- [ ] Task: Vendor HTMX locally to remove `unpkg.com` dependency
- [ ] Task: Fix BEM naming inconsistencies
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
