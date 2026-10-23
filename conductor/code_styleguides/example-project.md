---
trigger: model_decision
description: When creating, editing, or reviewing components and templates in example_project/
---

# Example Project Styleguide (`example_project/`)

`example_project/` has a distinct purpose from the built-in `dds` gallery components in `dj_design_system/components/` (which are governed by [dds-components.md](dds-components.md)).

## 1. Purpose of `example_project/`

1. **Consumer Feature Showcase:** Demonstrate to external developers how `dj-design-system` can be configured and used in a real Django project.
2. **Breadth-First Integration Testbed:** Exercise the full range of component and gallery features supported by the package engine so regressions are caught early.

## 2. Rules for `example_project/` Components

Unlike `dj_design_system/components/` (which enforces a single strict paradigm of Every Layout + CUBE CSS + 3-tier tokens + Light DOM Web Components), `example_project/` **intentionally mixes patterns** to test and showcase package flexibility:

- **Asset & Template Strategies:**
  - Include both co-located components (`.py`, `.html`, `.css`, `.js` in the same folder) and components using explicit `template_name`, `template_format_str`, or app-level `static/` assets.
- **Component Types & Parameters:**
  - Exercise `BaseComponent`, `BlockComponent` (both default-slot and named `Slots`), and every parameter type (`StringParam`, `IntParam`, `FloatParam`, `BoolParam`, `ChoiceParam`, `ListParam`, `DictParam`, `JSONParam`, `DataclassParam`, `ModelParam`, `ComponentParam`).
- **Directory & Namespace Configurations:**
  - Exercise `GALLERY_DIRECTORY_ALIASES` (`FlattenStrategy.NONE`, `FlattenStrategy.ALL`, `promote_to_app`), themes (`GALLERY_THEMES`), canvas backgrounds (`GALLERY_CANVAS_BACKGROUNDS`), and static snapshots.
- **Error & Edge-Case Coverage (`broken_components`):**
  - Maintain intentional error-case components in `broken_components` to verify graceful gallery error handling and warnings.
- **Gallery Visibility:**
  - `example_project.settings` keeps `GALLERY_SHOW_DDS_COMPONENTS = False` (the default) so the example gallery displays only `example_project` apps (`demo_System`, `broken_components`, etc.), while a dedicated `dds` gallery settings module sets `GALLERY_SHOW_DDS_COMPONENTS = True` to inspect the internal `dds` component library in isolation.
