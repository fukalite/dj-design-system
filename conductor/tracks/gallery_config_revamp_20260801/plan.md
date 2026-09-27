# Implementation Plan: Explicit Per-Component Gallery Configuration

## Core Concepts & Architectural Decisions
- **`Variant` & `GalleryConfig`**: First-class dataclasses in `dj_design_system.gallery`.
- **Discovery**: Supports `<component_name>_gallery.py` and `gallery.py`, with automatic backwards-compatibility fallback for legacy `basic_kwargs` / `maximal_kwargs`.
- **Navigation & Sidebar**: Respects `hidden`, `icon`, `group`, and `order`. Custom variants appear as child links in the sidebar navigation using `?variant=<name>` deep links.
- **Variant View**: Navigating to `?variant=<name>` displays a focused view for that variant with dedicated preview, code snippet, and pre-filled sandbox.
- **Smart Hybrid `canvas_template`**: Wraps with `{{ component }}` when placeholder is present; renders as raw template when absent.
- **Dynamic Callables**: Evaluates callable parameter values at render time.

---

## Phase 1: `Variant`, `GalleryConfig` & Component Discovery [checkpoint: 693cf49]
- [x] Task: Implement `Variant` and `GalleryConfig` in `dj_design_system.gallery` [ca6872a]
  - [x] Write failing unit tests for `Variant` and `GalleryConfig` attributes, validations, defaults, and dictionary coercions in `tests/test_gallery_config.py`.
  - [x] Implement `dj_design_system/gallery.py` with `Variant`, `GalleryConfig`, and helper functions.
- [x] Task: Update Component Discovery in `ComponentInfo` [693cf49]
  - [x] Write failing unit tests in `tests/test_discovery_gallery.py` verifying that `ComponentInfo.gallery_config` loads from `gallery.py` or `<name>_gallery.py`, and falls back to synthesized config when legacy `basic_kwargs` exist.
  - [x] Update `dj_design_system/data.py` to discover and attach `gallery_config`.
- [x] Task: Apply Review Improvements (Imports & Type Cleanups) [686f1f2]
  - [x] Streamline imports by moving `load_gallery_config` into `dj_design_system/gallery.py` and removing in-function imports in `data.py`.
  - [x] Simplify `GalleryConfig` by relying on dataclass type conventions rather than redundant primitive `isinstance` checks.
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 2: Navigation, Sorting & Sidebar Updates [checkpoint: d5ff70a]
- [x] Task: Update Navigation Builder (`services/navigation.py`) [447f8ab]
  - [x] Write failing unit tests for `hidden` exclusion, `icon` propagation, `order` sorting, `group` sub-folders, and variant child nodes in `tests/test_navigation_gallery.py`.
  - [x] Implement ordering, grouping, hidden filtering, and variant node insertion in `services/navigation.py`.
  - [x] Update `NavNode` in `dj_design_system/data.py` to support `icon`, `order`, and variant node representations.
- [x] Task: Update Frontend Sidebar (`navtree.html` and styles) [d5ff70a]
  - [x] Update `dj_design_system/templates/dj_design_system/gallery/navtree.html` to render custom icons and handle variant child links with active state matching `?variant=<name>`.
  - [x] Add necessary CSS styling in `dj_design_system/static/dj_design_system/gallery.css`.
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 3: Canvas Rendering & Smart Hybrid `canvas_template`
- [x] Task: Canvas Renderer Service Updates (`services/canvas.py` and `services/canvas_renderer.py`)
  - [x] Write failing unit tests in `tests/test_canvas_gallery_config.py` verifying Smart Hybrid `canvas_template` (`{{ component }}` vs raw template), `extra_context`, and callable parameter resolution.
  - [x] Implement `canvas_template` wrapping and callable evaluation in `services/canvas.py` / `services/canvas_renderer.py`.
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) [checkpoint: 335af63]

---

## Phase 4: Component View, Variant View & Sandbox Integration
- [x] Task: Update Gallery Views & Templates (`views.py` & `component.html`)
  - [x] Write tests in `tests/test_variant_views.py` verifying that requesting `?variant=<name>` activates the variant view and pre-fills sandbox form kwargs.
  - [x] Update `views.py` to resolve active variant, construct preview URLs, and pass variant context.
  - [x] Update `component.html` and `sandbox_fragment.html` to render focused variant view and sandbox preset dropdown.
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) [checkpoint: b3e2b99]

---

## Phase 5: Migration Script & Cleanup
- [x] Task: Migration Script (`migrate_gallery_configs`)
  - [x] Write migration management command `dj_design_system/management/commands/migrate_gallery_configs.py` that parses legacy `*_gallery.py` files and transforms them into modern `GalleryConfig` exports.
  - [x] Write unit tests verifying the migration script on sample legacy components.
  - [x] Execute migration script on `example_project` components.
- [x] Task: Deprecation & Cleanup
  - [x] Deprecate legacy `_gallery_kwargs` properties in favor of `gallery_config`.
  - [x] Ensure all existing tests in `tests/` pass cleanly with full coverage.
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 6: Documentation & Examples
- [ ] Task: Comprehensive API Documentation
  - [ ] Create `docs/api/gallery.md` documenting `GalleryConfig` and `Variant` using `mkdocstrings`.
  - [ ] Add `Gallery Configuration` under `API Reference` in `mkdocs.yml`.
- [ ] Task: Revamped Getting Started (`docs/quickstart.md`)
  - [ ] Add explicit guide on creating `gallery.py` / `{name}_gallery.py` alongside components.
  - [ ] Update component creation walkthrough to demonstrate `GalleryConfig` and custom variants.
- [ ] Task: Overhaul Gallery Documentation & Variants Guide (`docs/gallery.md`)
  - [ ] Replace legacy `basic_kwargs`/`maximal_kwargs` section with explicit `gallery.py` instructions.
  - [ ] Add dedicated comprehensive guide for Named Variants (defaults, custom variants, deep-linking, previewing, and icons).
  - [ ] Document Smart Hybrid `canvas_template` (`{{ component }}` wrapper vs raw template syntax).
  - [ ] Document sidebar properties (`order`, `group`, `icon`, `hidden`).
- [ ] Task: Full Documentation Assessment & Modernization
  - [ ] Review and update `docs/components.md`, `docs/organisation.md`, `docs/testing.md`, `docs/templatetags.md`, and `docs/index.md` to ensure all references to gallery setup and configurations are accurate and cohesive.
- [ ] Task: Example Project Showcase
  - [ ] Add rich, comprehensive examples in `example_project` demonstrating custom variants, custom icons, groupings, themes, and canvas templates across demo components (`button`, `badge`, `card`, `alert`, `quote_oneup`).
  - [ ] Ensure variant examples are formatted and documented so they can be directly referenced and embedded in the revamped documentation.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
