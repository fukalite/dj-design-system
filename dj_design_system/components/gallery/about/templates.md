# Template Breakdown & Responsibilities

This document details the gallery template architecture, outlining how templates are structured into modular layers, how data flows through them, and how consuming Django projects can override them.

---

## 1. Template Hierarchy & Organisation

Templates are organized under `dj_design_system/templates/dj_design_system/` in three distinct layers: **Base Shells**, **Area Layouts**, and **Content Panes**:

```text
gallery/base.html (HTML skeleton, @layer stylesheets, <dds-gallery-shell>)
  ├── gallery/areas/topbar.html (Header bar, search, theme select)
  ├── gallery/areas/sidebar.html ([data-surface='sidebar'], <dds-nav-tree>)
  └── gallery/component.html (Main content viewport)
        ├── gallery/areas/tabs.html (Docs vs Sandbox switcher)
        ├── gallery/panes/docs.html (Documentation Pane)
        │     ├── panes/docs/header.html (Title, Badges)
        │     ├── panes/docs/usage.html (Markdown index.md)
        │     ├── panes/docs/params.html (Parameters Table)
        │     └── panes/docs/further.html (Related Links)
        └── gallery/panes/sandbox.html (Interactive Workbench)
              ├── {% dds__sandbox_toolbar %}
              ├── {% dds__canvas_widget %} ──> canvas/iframe.html (Isolated Sandbox)
              └── {% dds__sandbox_params %}
```

---

## 2. Template Layers & Responsibilities

### 1. Base & Shell Templates

- **`gallery/base.html`**:
  - Emits the standard HTML5 document structure (`<!DOCTYPE html>`, `<html lang="en">`).
  - Injects the six CSS cascade layers (`@layer reset, tokens, global, composition, blocks, utilities`).
  - Loads client-side Web Component modules (`gallery-shell.js`, `nav_tree.js`, `search_box.js`).
  - Wraps the entire UI in `<dds-gallery-shell class="dds-gallery-shell">`, managing responsive mobile drawer states and keyboard shortcuts.
- **`gallery/component.html`**:
  - The primary orchestration template for inspecting a component.
  - Composes the top area tabs (`gallery/areas/tabs.html`), the documentation pane (`gallery/panes/docs.html`), and the interactive workbench (`gallery/panes/sandbox.html`).
- **`gallery/documentation.html`**:
  - Dedicated standalone template for rendering non-component documentation articles (such as this architecture guide).

---

### 2. Area Templates (`gallery/areas/`)

Area templates represent high-level visual regions that set up surface contexts:

- **`gallery/areas/topbar.html`**:
  - Sets `data-surface="topbar"`.
  - Hosts the brand title, mobile menu toggle button, global quick search combobox (`{% dds__search_box %}`), theme select popout (`{% dds__theme_select %}`), and external documentation links.
- **`gallery/areas/sidebar.html`**:
  - Sets `data-surface="sidebar"` (establishing the inverted dark theme in light mode).
  - Hosts the recursive navigation tree (`{% dds__nav_tree %}`) and maintains scroll position during page transitions.
- **`gallery/areas/tabs.html`**:
  - Provides the segmented view switcher allowing developers to flip between the **Docs** pane and the **Sandbox** pane.

---

### 3. Pane Templates (`gallery/panes/`)

Panes represent the main content bodies displayed within the viewport:

- **`gallery/panes/docs.html`**:
  - The documentation pane, partitioned into four focused sub-templates:
    - **`header.html`**: Component title, version, status badges, and description.
    - **`usage.html`**: Rendered markdown documentation from co-located `index.md`, including live ```canvas preview widgets.
    - **`params.html`**: Automatically generated parameter specification table documenting parameter names, types, default values, and choices.
    - **`further.html`**: Additional resources, styleguide references, and related components.
- **`gallery/panes/sandbox.html`**:
  - The interactive workbench pane composed of three coordinated domain components:
    - `{% dds__sandbox_toolbar %}`: Controls for viewport resizing, dark/light canvas backgrounds, ruler overlays, and RTL mirroring.
    - `{% dds__canvas_widget %}`: The preview container hosting the isolated component iframe.
    - `{% dds__sandbox_params %}`: The interactive parameter drawer rendering live form controls for tuning component arguments.
- **`gallery/panes/folder.html`**:
  - Folder index view rendering a grid of contained sub-folders, components, and documents.

---

### 4. Canvas Isolation Sandbox (`canvas/iframe.html`)

A critical architectural invariant is the complete separation of component styles from the outer gallery chrome:

- **`canvas/iframe.html`** is an intentionally bare document loaded inside the preview iframe.
- It contains **only** the target component markup, component-scoped CSS/JS, and Every Layout composition rules.
- Outer gallery styling (`topbar`, `sidebar`, `docs` prose) **never leaks** into the previewed component.
- Supports live postMessage auto-resizing, updating `--_canvas-widget-iframe-height` smoothly without vertical scrollbars.

---

## 3. Template Invariants & Consumer Customisation

1. **Zero Business Logic**: Templates never perform database queries, compute fallback calculations, or format raw data. All context is prepared cleanly in Python view and service layers before being passed into templates.
2. **Component Composition via Template Tags**: Templates compose components using `{% dds__<name> %}` and Every Layout primitives (`<l-stack>`, `<l-cluster>`, etc.) rather than hardcoding repetitive HTML markup.
3. **Consumer Shadowing**: Consuming Django projects can override any gallery template simply by creating a file with the identical path in their project's `templates/` directory (e.g. `templates/dj_design_system/gallery/areas/topbar.html`). This allows consumers to replace logos, header actions, or footer metadata without modifying the core package.
