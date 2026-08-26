# Specification: Explicit Per-Component Gallery Configuration

## Overview
Revamp the component gallery configuration by introducing a strictly-typed, explicit configuration format housed in an optional `gallery.py` file alongside the component file. This file will export a `GalleryConfig` object.

## Functional Requirements
1. **GalleryConfig Class**:
   - Create a typed `GalleryConfig` class in `dj_design_system.gallery`.
   - Properties:
     - `hidden` (bool): Hides the component from the gallery.
     - `icon` (str): Custom icon name for the navigation sidebar (e.g., `"mdi:button"`, mapping to an icon library or SVG path).
     - `theme` (str): Specific theme override for the component preview.
     - `group` (str): Grouping category for the navigation sidebar.
     - `order` (int): Explicit ordering integer for the navigation sidebar. Nodes are sorted by `order` first, then alphabetically. Default is 0.
     - `canvas_template` (str): A highly flexible template string (like the MD canvas ``` functionality) where you can write custom HTML and include the component tag, e.g., `<div class="p-4">{% my_component %}</div>`.
     - `extra_context` (dict): Additional context variables to pass to the preview template.
     - `param_defaults` (dict): Mapping of param names to default values (supports raw values or callables for dynamic values like Model/QuerySet fetches).

2. **Discovery Mechanism**:
   - When registering a component, check if a `gallery.py` file exists in the same directory.
   - If present, import it and read the `config` variable.

3. **Integration**:
   - Update the gallery views and navigation builder (`services/navigation.py`) to respect `hidden`, `icon`, `group`, and `order`.
   - Ensure the sidebar frontend can render the specified `icon` (using the project's existing icon system).
   - Update the canvas renderer (`services/canvas.py`) to parse and render `canvas_template` (mimicking the markdown canvas extension behavior).

4. **Migration & Backwards Compatibility**:
   - **One-off Script**: Create a migration script (e.g., a Django management command or Python script) that scans existing components, extracts legacy gallery configurations from the component `Meta` or attributes, writes them to a new `gallery.py`, and cleans up the component file.
   - Breaking Change: Legacy gallery configurations on the component class itself will be removed.

## Acceptance Criteria
- `GalleryConfig` class is fully implemented with type hints.
- Creating a `gallery.py` with `config = GalleryConfig(hidden=True, order=-10)` successfully hides a component or reorders it.
- `canvas_template` supports arbitrary HTML layout wrapping the component, functioning identically to the MD canvas block.
- Param defaults configured via callables in `GalleryConfig.param_defaults` evaluate correctly.
- The one-off migration script correctly ports existing `example_project` components to the new `gallery.py` format without data loss.
