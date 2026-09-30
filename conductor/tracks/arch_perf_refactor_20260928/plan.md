# Implementation Plan

## Phase 1: Core Performance & API Cleanup
- [ ] Task: Add caching to `build_navigation()` and `build_search_index()`, and skip for HTMX requests
- [ ] Task: Clean up `__init__.py` to expose all necessary public API (e.g. `GalleryParameter`, base components)
- [ ] Task: Refactor `Variant.__eq__` to remove string comparison
- [ ] Task: Consolidate scattered exception hierarchy
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: View & Service Decomposition
- [ ] Task: Split `views.py` into a `views/` package (`gallery.py`, `component.py`, `canvas.py`, `decorators.py`)
- [ ] Task: Extract variant parameter merging logic into a single shared helper
- [ ] Task: Decompose `render_component` into smaller functions
- [ ] Task: Move URL resolution logic out of `NavNode` into navigation service
- [ ] Task: Refactor `GalleryConfig` to use a factory method for dict/mapping unpacking
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
