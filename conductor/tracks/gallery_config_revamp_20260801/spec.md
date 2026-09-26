# Specification: Explicit Per-Component Gallery Configuration

## Overview
Revamp the component gallery configuration by introducing a strictly-typed, explicit configuration format housed in an optional `gallery.py` or `<component_name>_gallery.py` file alongside the component file. This file exports a `GalleryConfig` object managing metadata, navigation, canvas wrapping, and named variants.

## Functional Requirements

### 1. `Variant` and `GalleryConfig` Classes (`dj_design_system.gallery`)
- **`Variant` Class**:
  - `name` (str): Unique variant slug (e.g. `"basic"`, `"maximal"`, `"danger"`).
  - `label` (str | None): Display label in navigation and documentation (defaults to title-cased name).
  - `description` (str | None): Optional markdown description explaining the variant.
  - `kwargs` (dict[str, Any]): Parameters passed to the component tag (supports raw values, `GalleryParameter`, or callables).
  - `positional_args` (tuple[Any, ...]): Positional arguments passed to the component tag.
  - `canvas_template` (str | None): Optional variant-specific canvas wrapper override.
  - `extra_context` (dict[str, Any]): Additional template context specific to this variant.
  - `icon` (str | None): Icon identifier for navigation sidebar.
  - `theme` (str | None): Theme override for previewing this variant.
  - `show_in_nav` (bool): Whether to render as a child item in the sidebar navigation (defaults to True for custom variants, False for default basic/maximal).

- **`GalleryConfig` Class**:
  - `hidden` (bool): Hides the component and its variants from gallery navigation and search. Default `False`.
  - `icon` (str | None): Custom icon for the component in the navigation sidebar (e.g., `"mdi:button"` or SVG path).
  - `theme` (str | None): Theme override for the component preview.
  - `group` (str | None): Grouping category for the navigation sidebar.
  - `order` (int): Explicit ordering integer for the navigation sidebar. Nodes are sorted by `order` first, then alphabetically. Default is 0.
  - `canvas_template` (str | None): HTML template layout for previews. Operates in Smart Hybrid mode:
    - If `{{ component }}` placeholder is present, acts as a layout wrapper around the rendered component tag.
    - If `{{ component }}` is absent, renders as raw Django template code with `{% load design_components %}`.
  - `extra_context` (dict[str, Any]): Additional context variables passed to the canvas template.
  - `param_defaults` (dict[str, Any]): Mapping of parameter names to default values (supports raw values or callables for dynamic values like Model/QuerySet fetches).
  - `variants` (list[Variant]): List of configured variants. Supports initialization from `Variant` instances or shorthand dicts. If omitted, default `"basic"` and `"maximal"` variants are synthesized.

### 2. Discovery Mechanism
- When registering or inspecting a component:
  1. Check for `<component_name>_gallery.py` in the component's directory.
  2. If not found, check for `gallery.py` in the component's directory.
  3. Safely import the module and look for a `config` attribute of type `GalleryConfig`.
  4. Backwards compatibility fallback: If `config` is not defined but legacy `basic_kwargs` or `maximal_kwargs` are exported, automatically construct a `GalleryConfig` with corresponding `basic` and `maximal` variants.
  5. Attach the resolved `GalleryConfig` to `ComponentInfo.gallery_config`.

### 3. Navigation & Sidebar Integration (`services/navigation.py`)
- **Ordering**: Sort navigation nodes by `order` first (ascending), then alphabetically by label.
- **Grouping**: Group components under specified `group` sub-folders if defined.
- **Hidden**: Omit components with `hidden=True` from the navigation tree.
- **Icons**: Propagate `icon` to `NavNode` for rendering in `navtree.html`.
- **Variants in Sidebar**:
  - Non-default variants (`show_in_nav=True`) appear as nested child links under the component node.
  - Variant link URL: deep-links with query param `?variant=<name>` (e.g. `/gallery/<app>/<path>/?variant=danger`).
  - Active state: when `?variant=<name>` matches, highlight the variant child link and expand the parent component details node.

### 4. Canvas Rendering (`services/canvas.py` & `services/canvas_renderer.py`)
- Smart Hybrid `canvas_template`:
  - Wrapper mode (`{{ component }}` present): render component with resolved kwargs/slots, then substitute into wrapper and render with `extra_context`.
  - Raw mode (`{{ component }}` absent): render directly as Django template with `extra_context`.
- Callable parameter resolution: evaluate any callable defaults in `param_defaults` or `variant.kwargs` during canvas rendering.
- Respect component/variant `theme` overrides.

### 5. Component View & Variant View (`views.py` & `component.html`)
- **Main View (no `?variant`)**:
  - Displays component documentation, parameters table, minimal and maximal usage examples, and sandbox pane.
- **Variant View (`?variant=<name>`)**:
  - Renders a focused view for the selected variant: variant title, description, live preview canvas (with custom `canvas_template` if set), tag usage snippet, and pre-fills the interactive sandbox form with the variant's kwargs.
- **Sandbox Presets**:
  - Provide a variant selector in the sandbox toolbar to switch presets easily.

### 6. Migration & Backwards Compatibility
- Provide a migration command (`migrate_gallery_configs`) scanning existing components.
- Port legacy `*_gallery.py` files containing `basic_kwargs` / `maximal_kwargs` to the new `GalleryConfig` format.
- Clean up obsolete `_gallery_kwargs` references.

## Acceptance Criteria
- `Variant` and `GalleryConfig` classes fully implemented with strict type hints and validation.
- Discovery seamlessly loads `gallery.py` and `<name>_gallery.py`, with automatic backwards-compatibility fallback for legacy kwargs dicts.
- `hidden`, `icon`, `group`, and `order` behave correctly in `services/navigation.py` and render properly in `navtree.html`.
- Non-default variants appear in the sidebar, active states match `?variant=<name>`, and clicking them displays a focused variant view with pre-filled sandbox.
- Smart Hybrid `canvas_template` works for both `{{ component }}` wrappers and raw template tags.
- Callable `param_defaults` evaluate correctly at render time.
- Migration script converts existing demo components cleanly without loss of preview capability.
- All existing and new tests pass with >80% coverage and `just check` passes cleanly.
