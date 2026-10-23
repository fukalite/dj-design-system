# Specification: Built-in `domain` Collection — Shell, Navigation & Docs

## Overview
Implements the gallery shell, topbar, sidebar navigation tree, search box, theme selector, folder listing, and documentation rendering components in `dj_design_system/components/domain/<name>/`.

## Functional Requirements
1. **Shell & Navigation (`dj_design_system/components/domain/`):**
   - `gallery_shell` (`{% dds__gallery_shell %}` + `<dds-gallery-shell>`): Outer frame composing the topbar (`data-surface="topbar"`), collapsible sidebar (`data-surface="sidebar"`), mobile backdrop (`data-surface="overlay"`), and main content slot using Every Layout `.l-sidebar`.
   - `toolbar` (`{% dds__toolbar %}`): Topbar header containing brand link, mobile drawer toggle, search box, and theme selector.
   - `sidebar` (`{% dds__sidebar %}`): Sidebar container hosting the navigation tree.
   - `nav_tree` (`{% dds__nav_tree %}` + `<dds-nav-tree>`): Recursive navigation tree with collapsible folder sections and active node highlighting (`aria-current="page"`).
   - `search_box` (`{% dds__search_box %}` + `<dds-search-box>`): Client-side instant search input and dropdown results with keyboard navigation (`/` shortcut, arrow keys, `Escape`).
   - `theme_select` (`{% dds__theme_select %}` + `<dds-theme-select>`): Gallery theme selector persisting theme choice and dispatching `dds:theme-change`.
   - `folder_listing` (`{% dds__folder_listing %}`): Grid/stack card listing of child folders, components, and documents within a folder node.
2. **Documentation Components (`dj_design_system/components/domain/`):**
   - `prose` (`{% dds__prose %}`): Styled Markdown prose region (`data-surface="docs"`, `--dds-layout-prose-measure`, `--dds-type-prose-*`).
   - `params_table` (`{% dds__params_table %}`): Structured parameter and slot reference table composing `{% dds__table %}` and `{% dds__badge %}`.
   - `usage_example` (`{% dds__usage_example %}`): Template tag usage snippet composing `{% dds__code_block %}`.
   - `variant_view` (`{% dds__variant_view %}`): Named component variant preview card and code snippet.

## Acceptance Criteria
- Every component in `dj_design_system/components/domain/` adheres strictly to `conductor/code_styleguides/dds-components.md`:
  - 100% co-located directory (`<name>.py`, `<name>.html`, `<name>.css`, `<name>.ts` if interactive, `gallery.py`, `index.md`).
  - Zero BEM (`__` or `--`); CUBE CSS `@layer blocks` + Tier 3 `--_<component>-*` tokens.
  - Template composition via `{% dds__* %}` tags; zero `.render()` calls inside Python `get_context()`.
