# Specification: Architecture & Performance Refactoring

## Overview
Address high-severity architectural issues and performance bottlenecks in the gallery system.

## Requirements
1. **Performance:** Cache `build_navigation()` and `build_search_index()`, and skip execution entirely for HTMX fragment requests.
2. **Decomposition:** Split the 800-line `views.py` into a focused `views/` package.
3. **DRY & Decoupling:** Centralize variant parameter merging, remove URL routing logic from `NavNode`, refactor `GalleryConfig` type handling, and consolidate the exception hierarchy.
4. **API Surface:** Expose all necessary public classes in `dj_design_system/__init__.py`.
