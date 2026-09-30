# Implementation Plan

## Phase 1: Core Performance & API Cleanup [checkpoint: 7d939e1]
- [x] Task: Add caching to `build_navigation()` and `build_search_index()`, and skip for HTMX requests [b157511]
- [x] Task: Clean up `__init__.py` to expose all necessary public API (e.g. `GalleryParameter`, base components) [8a1a158]
- [x] Task: Refactor `Variant.__eq__` to remove string comparison [0674c57]
- [x] Task: Consolidate scattered exception hierarchy [313440f]
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) [7d939e1]

## Phase 2: View & Service Decomposition [checkpoint: 50c890b]
- [x] Task: Split `views.py` into a `views/` package (`gallery.py`, `component.py`, `canvas.py`, `decorators.py`) [d093658]
- [x] Task: Extract variant parameter merging logic into a single shared helper [06cd392]
- [x] Task: Decompose `render_component` into smaller functions [30b0ea2]
- [x] Task: Move URL resolution logic out of `NavNode` into navigation service [74a4c95]
- [x] Task: Refactor `GalleryConfig` to use a factory method for dict/mapping unpacking [50c890b]
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) [50c890b]
