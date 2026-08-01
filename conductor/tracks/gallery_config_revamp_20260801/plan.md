# Implementation Plan: Explicit Per-Component Gallery Configuration

## Phase 1: `GalleryConfig` Core & Discovery
- [ ] Task: Implement `GalleryConfig` class
  - [ ] Write failing unit test for `GalleryConfig` definition and property validation.
  - [ ] Implement `GalleryConfig` in `dj_design_system.gallery` (or a suitable new module).
- [ ] Task: Update Component Discovery
  - [ ] Write failing tests verifying that `gallery.py` is loaded during discovery and its `config` object is correctly attached to the component's node.
  - [ ] Implement discovery logic to dynamically import `gallery.py` safely.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Navigation & Sorting Updates
- [ ] Task: Update Navigation Builder (`services/navigation.py`)
  - [ ] Write failing tests for `hidden` exclusion, custom `icon` mapping, `group` aggregation, and `order` sorting.
  - [ ] Implement the changes in the tree builder to output the correct JSON/structures for the frontend.
- [ ] Task: Update Frontend Sidebar (if necessary)
  - [ ] Ensure the frontend can render the dynamic `icon` and respects the new groupings.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Canvas Rendering Updates
- [ ] Task: Update Canvas Renderer (`services/canvas.py`)
  - [ ] Write failing tests verifying `canvas_template` rendering, `extra_context` passing, and `param_defaults` (including callable execution).
  - [ ] Implement the rendering pipeline changes to intercept component contexts and wrap them in the `canvas_template`.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 4: Migration Script & Cleanup
- [ ] Task: Migration Script creation
  - [ ] Write a robust management command (or standalone script) that traverses the `example_project` components.
  - [ ] Extract legacy config (e.g. `Meta` canvas background) and generate well-formatted `gallery.py` files.
- [ ] Task: Execute Migration & Cleanup Core
  - [ ] Run the migration script on the codebase.
  - [ ] Remove deprecated gallery settings from the core component base classes and settings.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 5: Documentation & Examples
- [ ] Task: Comprehensive Documentation
  - [ ] Write detailed documentation for the `GalleryConfig` API covering all attributes, examples of callables, themes, and wrappers.
- [ ] Task: Examples in Demo
  - [ ] Create robust examples in `example_project` demonstrating every feature of `GalleryConfig` (e.g. complex `canvas_template`, `param_defaults` fetching DB models, custom ordering).
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
