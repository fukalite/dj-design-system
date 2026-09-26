# Implementation Plan: Explicit Per-Component Gallery Configuration

## Core Concepts & Architectural Decisions
- **`Variant` & `GalleryConfig`**: First-class dataclasses in `dj_design_system.gallery`.
- **Discovery**: Supports `<component_name>_gallery.py` and `gallery.py`, with automatic backwards-compatibility fallback for legacy `basic_kwargs` / `maximal_kwargs`.
- **Navigation & Sidebar**: Respects `hidden`, `icon`, `group`, and `order`. Custom variants appear as child links in the sidebar navigation using `?variant=<name>` deep links.
- **Variant View**: Navigating to `?variant=<name>` displays a focused view for that variant with dedicated preview, code snippet, and pre-filled sandbox.
- **Smart Hybrid `canvas_template`**: Wraps with `{{ component }}` when placeholder is present; renders as raw template when absent.
- **Dynamic Callables**: Evaluates callable parameter values at render time.

---

## Phase 1: `Variant`, `GalleryConfig` & Component Discovery
- [x] Task: Implement `Variant` and `GalleryConfig` in `dj_design_system.gallery` [ca6872a]
  - [ ] Write failing unit tests for `Variant` and `GalleryConfig` attributes, validations, defaults, and dictionary coercions in `tests/test_gallery_config.py`.
  - [ ] Implement `dj_design_system/gallery.py` with `Variant`, `GalleryConfig`, and helper functions.
- [ ] Task: Update Component Discovery in `ComponentInfo`
  - [ ] Write failing unit tests in `tests/test_discovery_gallery.py` verifying that `ComponentInfo.gallery_config` loads from `gallery.py` or `<name>_gallery.py`, and falls back to synthesized config when legacy `basic_kwargs` exist.
  - [ ] Update `dj_design_system/data.py` to discover and attach `gallery_config`.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 2: Navigation, Sorting & Sidebar Updates
- [ ] Task: Update Navigation Builder (`services/navigation.py`)
  - [ ] Write failing unit tests for `hidden` exclusion, `icon` propagation, `order` sorting, `group` sub-folders, and variant child nodes in `tests/test_navigation_gallery.py`.
  - [ ] Implement ordering, grouping, hidden filtering, and variant node insertion in `services/navigation.py`.
  - [ ] Update `NavNode` in `dj_design_system/data.py` to support `icon`, `order`, and variant node representations.
- [ ] Task: Update Frontend Sidebar (`navtree.html` and styles)
  - [ ] Update `dj_design_system/templates/dj_design_system/gallery/navtree.html` to render custom icons and handle variant child links with active state matching `?variant=<name>`.
  - [ ] Add necessary CSS styling in `dj_design_system/static/dj_design_system/gallery.css`.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 3: Canvas Rendering & Smart Hybrid `canvas_template`
- [ ] Task: Canvas Renderer Service Updates (`services/canvas.py` and `services/canvas_renderer.py`)
  - [ ] Write failing unit tests in `tests/test_canvas_gallery_config.py` verifying Smart Hybrid `canvas_template` (`{{ component }}` vs raw template), `extra_context`, and callable parameter resolution.
  - [ ] Implement `canvas_template` wrapping and callable evaluation in `services/canvas.py` / `services/canvas_renderer.py`.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 4: Component View, Variant View & Sandbox Integration
- [ ] Task: Update Gallery Views & Templates (`views.py` & `component.html`)
  - [ ] Write tests in `tests/test_variant_views.py` verifying that requesting `?variant=<name>` activates the variant view and pre-fills sandbox form kwargs.
  - [ ] Update `views.py` to resolve active variant, construct preview URLs, and pass variant context.
  - [ ] Update `component.html` and `sandbox_fragment.html` to render focused variant view and sandbox preset dropdown.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 5: Migration Script & Cleanup
- [ ] Task: Migration Script (`migrate_gallery_configs`)
  - [ ] Write migration management command `dj_design_system/management/commands/migrate_gallery_configs.py` that parses legacy `*_gallery.py` files and transforms them into modern `GalleryConfig` exports.
  - [ ] Write unit tests verifying the migration script on sample legacy components.
  - [ ] Execute migration script on `example_project` components.
- [ ] Task: Deprecation & Cleanup
  - [ ] Deprecate legacy `_gallery_kwargs` properties in favor of `gallery_config`.
  - [ ] Ensure all existing tests in `tests/` pass cleanly with full coverage.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 6: Documentation & Examples
- [ ] Task: Comprehensive Documentation
  - [ ] Document `GalleryConfig`, `Variant`, `canvas_template`, navigation ordering, and callables in project docs.
- [ ] Task: Example Project Showcase
  - [ ] Add rich examples in `example_project` demonstrating custom variants, custom icons, groupings, and canvas templates.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
