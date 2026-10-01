# Implementation Plan: Gallery Rebuild 1 — Internal Component Foundation

This plan adds registry support for internal (package-owned) components and the gallery visibility settings. No visible change is made.

## Phase 1: `components` Package [checkpoint: d841f15]
- [x] Task: Write Failing Tests (`Red Phase`) [d841f15]
  - [x] Verify `from dj_design_system.components import BaseComponent, TagComponent, BlockComponent` still works.
  - [x] Verify a component in a `dj_design_system/components/<sub>/` module is discovered.
  - [x] Verify the abstract base classes are never registered.
- [x] Task: Implement to Pass Tests (`Green Phase`) [d841f15]
  - [x] Move base classes to `components/base.py`; re-export from `components/__init__.py`.
  - [x] Update internal imports across the package.
- [x] Task: Refactor and Verify Coverage [d841f15]
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) [d841f15]

---

## Phase 2: Internal Components [checkpoint: ba6b5e0]
- [x] Task: Write Failing Tests (`Red Phase`) [ba6b5e0]
  - [x] `ComponentInfo.is_internal` is true for `dj_design_system` components and for `Meta.internal = True`.
  - [x] Internal components register only their qualified tag name; short names are not registered.
  - [x] A consumer component with the same short name as an internal one renders under the short name regardless of `INSTALLED_APPS` order.
  - [x] Built-in qualified names use the `dds` prefix, and consumer `COMPONENT_DIRECTORIES` settings cannot remove it.
  - [x] `get_by_name()` without `app_label`, and `resolve_component()`, ignore internal components; qualified names still resolve.
  - [x] `get_merged_media()` excludes internal media; an internal-media accessor returns it.
  - [x] Markdown canvases do not receive internal media.
- [x] Task: Implement to Pass Tests (`Green Phase`) [ba6b5e0]
  - [x] Add `is_internal` to `ComponentInfo`; honour `Meta.internal`.
  - [x] Update `register_templatetags`, `get_by_name`, `resolve_component`, `get_merged_media`.
  - [x] Add the built-in `dds` prefix resolution.
  - [x] Add the internal-media accessor.
- [x] Task: Refactor and Verify Coverage [ba6b5e0]
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) [ba6b5e0]

---

## Phase 3: Built-in Asset Convention [checkpoint: 809eb48]
- [x] Task: Write Failing Tests (`Red Phase`) [809eb48]
  - [x] Using a test-only built-in component fixture, verify its explicit `template_name` renders with `APP_DIRS: True` and without `ComponentsTemplateLoader`.
  - [x] Verify its `Media` paths resolve with only the default static finders.
  - [x] Convention test: every built-in component declares `template_name` under `dj_design_system/ui/` and has no co-located `.html`/`.css`/`.js`.
- [x] Task: Implement to Pass Tests (`Green Phase`) [809eb48]
  - [x] Create `templates/dj_design_system/ui/` and `static/dj_design_system/ui/` directories. (Not committed empty: git can't track empty directories and a static placeholder would be collected. Track 2 adds them with the first component.)
  - [x] Implement the convention test so it passes vacuously now and guards later tracks.
- [x] Task: Refactor and Verify Coverage [809eb48]
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) [809eb48]

---

## Phase 4: Gallery Visibility Settings [checkpoint: 14b57f2]
- [x] Task: Write Failing Tests (`Red Phase`) [14b57f2]
  - [x] Defaults: `GALLERY_EXCLUDE_APPS == []`, `GALLERY_SHOW_BUILTIN_COMPONENTS is False`.
  - [x] With the flag `False`, `dj_design_system` is excluded even if `GALLERY_EXCLUDE_APPS` is overridden without it.
  - [x] With the flag `True`, `dj_design_system` is shown unless listed in `GALLERY_EXCLUDE_APPS`.
  - [x] Consumer apps in `GALLERY_EXCLUDE_APPS` are hidden.
  - [x] Hidden apps are absent from the nav tree, search index and `total_components`; their node URLs return 404; they are absent from the REST API listing.
  - [x] Hidden components still render as template tags.
- [x] Task: Implement to Pass Tests (`Green Phase`) [14b57f2]
  - [x] Add both settings to `DEFAULTS` and `DjangoDesignSystemSettings`.
  - [x] Add the single visibility helper and use it in navigation, views and API.
  - [x] Set `GALLERY_SHOW_BUILTIN_COMPONENTS = True` in `example_project/settings.py`.
- [x] Task: Refactor and Verify Coverage [14b57f2]
- [x] Task: Confirm the track 0 visual baseline still passes. [14b57f2] (CI run 36560122324)
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md) [14b57f2]
