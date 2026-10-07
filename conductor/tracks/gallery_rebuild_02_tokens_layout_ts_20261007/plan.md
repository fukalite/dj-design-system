# Implementation Plan: CSS Architecture, 3-Tier Design Tokens & TypeScript Pipeline

## Phase 1: 3-Tier Design Tokens & Every Layout Composition Layer
- [ ] Write automated tests verifying the presence and structure of `@layer reset, tokens, global, composition, blocks, utilities`, all Tier 1 `--_dds-*` and Tier 2 `--dds-*` tokens across all 6 domains, `.gallery-theme-dark`, `[data-surface]`, and `.l-*` Every Layout classes
- [ ] Implement `@layer reset, tokens, global, composition` with all Tier 1 and Tier 2 tokens and the 7 Every Layout primitives
- [ ] Run `just test` and `just check`
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: TypeScript Build Pipeline for Co-located Web Components
- [ ] Configure `tsconfig.json` and `just build-ts` to compile `dj_design_system/components/**/*.ts` into sibling `.js` files
- [ ] Add a test verifying TypeScript compilation and staticfinder resolution of compiled `.js` assets
- [ ] Update `justfile` and `.github/workflows/ci.yml` to run `just build-ts` where needed
- [ ] Run `just test` and `just check`
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
