# Implementation Plan: Gallery Page Composition, Legacy Asset Removal & Visual Baselines

## Phase 1: Page Template Composition & Legacy Asset Removal
- [ ] Rewrite `dj_design_system/templates/dj_design_system/` page templates using `{% dds__* %}` components and Every Layout `.l-*` primitives
- [ ] Remove legacy BEM CSS and `js/gallery.js`, replacing `gallery.css` with `@layer reset, tokens, global, composition, blocks, utilities` imports
- [ ] Run `just test` and `just check`
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: E2E, Accessibility & Visual Baseline Verification
- [ ] Run E2E and accessibility (`axe-core`) tests and resolve any regressions
- [ ] Regenerate visual regression baselines (`just visual-update`) and verify `just visual-test` passes cleanly
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
