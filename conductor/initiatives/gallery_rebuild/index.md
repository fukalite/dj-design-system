# Initiative: Gallery Rebuild (`gallery_rebuild`)

## Overview
Rebuild the `dj-design-system` component gallery UI cleanly on top of `main` using 100% co-located `dds` components (`elements/` and `domain/` collections flattened as `{% dds__<name> %}`), Every Layout + CUBE CSS (`@layer reset, tokens, global, composition, blocks, utilities`), the 3-Tier Design Token System (`--_dds-*`, `--dds-*`, `--_<component>-*`), and Light DOM `<dds-*>` TypeScript web components.

## Governing Styleguides & Orchestration
- [Subagent Orchestration Strategy & Prompt Templates](./subagents.md)
- [Built-in `dds` Gallery Component Styleguide](../../code_styleguides/dds-components.md)
- [Example Project Component Styleguide](../../code_styleguides/example-project.md)
- [Python & Django Layered Architecture](../../code_styleguides/layered-architecture.md)

## Tracks
1. [Track 1 — Visual Regression Harness & `dds` Component Foundation](../../tracks/gallery_rebuild_01_foundation_20261007/index.md)
2. [Track 2 — CSS Architecture, 3-Tier Design Tokens & TypeScript Pipeline](../../tracks/gallery_rebuild_02_tokens_layout_ts_20261007/index.md)
3. [Track 3 — Built-in `elements` Collection](../../tracks/gallery_rebuild_03_elements_20261007/index.md)
4. [Track 4 — Built-in `domain` Collection: Shell, Navigation & Docs](../../tracks/gallery_rebuild_04_domain_shell_nav_docs_20261007/index.md)
5. [Track 5 — Built-in `domain` Collection: Sandbox, Controls & Canvas](../../tracks/gallery_rebuild_05_domain_sandbox_canvas_20261007/index.md)
6. [Track 6 — Gallery Page Composition, Legacy Asset Removal & Visual Baselines](../../tracks/gallery_rebuild_06_pages_20261007/index.md)
7. [Track 7 — `example_project/` Rework & Consumer Shadowing Showcase](../../tracks/gallery_rebuild_07_example_docs_20261007/index.md)
8. [Track 8 — Visual Parity, Token & Typography Polish](../../tracks/gallery_rebuild_08_visual_polish_20261008/index.md)
9. [Track 9 — Packaging, Engine & Architectural Hardening](../../tracks/gallery_rebuild_09_arch_hardening_20261009/index.md)
