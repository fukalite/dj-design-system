# Implementation Plan: Built-in `domain` Collection — Shell, Navigation & Docs

## Phase 1: Shell & Navigation Components (`gallery_shell`, `toolbar`, `sidebar`, `nav_tree`, `search_box`, `theme_select`, `folder_listing`)
- [ ] Write unit and rendering tests for `gallery_shell`, `toolbar`, `sidebar`, `nav_tree`, `search_box`, `theme_select`, and `folder_listing`
- [ ] Implement co-located `dj_design_system/components/domain/{gallery_shell,toolbar,sidebar,nav_tree,search_box,theme_select,folder_listing}/` with `.py`, `.html`, `.css`, `.ts` (where interactive), `gallery.py`, and `index.md`
- [ ] Compile TypeScript (`just build-ts`) and run `just test` and `just check`
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Documentation Components (`prose`, `params_table`, `usage_example`, `variant_view`)
- [ ] Write unit and rendering tests for `prose`, `params_table`, `usage_example`, and `variant_view`
- [ ] Implement co-located `dj_design_system/components/domain/{prose,params_table,usage_example,variant_view}/` with `.py`, `.html`, `.css`, `gallery.py`, and `index.md`
- [ ] Run `just test` and `just check`
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
