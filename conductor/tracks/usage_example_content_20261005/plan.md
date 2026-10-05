# Implementation Plan: Usage Example Block Content

## Phase 1: Snippets Match Their Previews
- [ ] Task: Build signature kwargs from the merged gallery parameters
  - [ ] Write failing tests: `content` in `param_defaults` appears in both snippets; a variant's `content` overrides it.
  - [ ] Replace the `gallery_basic_kwargs` / `gallery_maximal_kwargs` reads in `generate_tag_signature` with `merge_variant_params(component_class, config, variant)` for the `basic` and `maximal` variants.
- [ ] Task: Make `content` the block body
  - [ ] Write failing tests: no `content=` keyword in a block snippet; a `GalleryParameter` shows its `code`; the placeholder shows when `content` is unset; the canvas specs carry the content.
  - [ ] Pop `content` from the kwargs of non-slotted block components, add a `content` argument to `_build_sig_raw`, and pass the content into `minimal_spec` and `maximal_spec`.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Layout, View Coverage & Changelog
- [ ] Task: Lay out multi-line content readably
  - [ ] Write failing test for multi-line HTML content in a block tag with no parameters.
  - [ ] Update `_format_multiline_example` so the body sits on its own lines.
- [ ] Task: Component page view test
  - [ ] Test that the component page's code snippets and preview URLs carry the same `content`.
- [ ] Task: Changelog
  - [ ] Add an `[Unreleased]` → Fixed entry referencing #154.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
