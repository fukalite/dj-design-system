# Implementation Plan: Built-in `elements` Collection

## Phase 1: Core Static Primitives (`icon`, `button`, `badge`, `notice`, `table`, `breadcrumb`, `form_field`)
- [ ] Write unit and rendering tests for `icon`, `button`, `badge`, `notice`, `table`, `breadcrumb`, and `form_field`
- [ ] Implement co-located `dj_design_system/components/elements/{icon,button,badge,notice,table,breadcrumb,form_field}/` with `.py`, `.html`, `.css` (`@layer blocks` + Tier 3 `--_<component>-*` tokens), `gallery.py`, and `index.md`
- [ ] Run `just test` and `just check`
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Interactive Element Primitives (`code_block`, `tabs`, `popout`, `popout_option`)
- [ ] Write unit and E2E/DOM behaviour tests for `code_block` (`<dds-code-block>`), `tabs` (`<dds-tabs>`), and `popout` / `popout_option` (`<dds-popout>`)
- [ ] Implement co-located `code_block`, `tabs`, `popout`, and `popout_option` with TypeScript Light DOM custom elements, `AbortController` cleanup, `gallery.py`, and `index.md`
- [ ] Compile TypeScript (`just build-ts`) and run `just test` and `just check`
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
