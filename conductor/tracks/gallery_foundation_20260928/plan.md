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

## Phase 2: Internal Components
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
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 3: Built-in Asset Convention
- [ ] Task: Write Failing Tests (`Red Phase`)
  - [ ] Using a test-only built-in component fixture, verify its explicit `template_name` renders with `APP_DIRS: True` and without `ComponentsTemplateLoader`.
  - [ ] Verify its `Media` paths resolve with only the default static finders.
  - [ ] Convention test: every built-in component declares `template_name` under `dj_design_system/ui/` and has no co-located `.html`/`.css`/`.js`.
- [ ] Task: Implement to Pass Tests (`Green Phase`)
  - [ ] Create `templates/dj_design_system/ui/` and `static/dj_design_system/ui/` directories.
  - [ ] Implement the convention test so it passes vacuously now and guards later tracks.
- [ ] Task: Refactor and Verify Coverage
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 4: Gallery Visibility Settings
- [ ] Task: Write Failing Tests (`Red Phase`)
  - [ ] Defaults: `GALLERY_EXCLUDE_APPS == []`, `GALLERY_SHOW_BUILTIN_COMPONENTS is False`.
  - [ ] With the flag `False`, `dj_design_system` is excluded even if `GALLERY_EXCLUDE_APPS` is overridden without it.
  - [ ] With the flag `True`, `dj_design_system` is shown unless listed in `GALLERY_EXCLUDE_APPS`.
  - [ ] Consumer apps in `GALLERY_EXCLUDE_APPS` are hidden.
  - [ ] Hidden apps are absent from the nav tree, search index and `total_components`; their node URLs return 404; they are absent from the REST API listing.
  - [ ] Hidden components still render as template tags.
- [ ] Task: Implement to Pass Tests (`Green Phase`)
  - [ ] Add both settings to `DEFAULTS` and `DjangoDesignSystemSettings`.
  - [ ] Add the single visibility helper and use it in navigation, views and API.
  - [ ] Set `GALLERY_SHOW_BUILTIN_COMPONENTS = True` in `example_project/settings.py`.
- [ ] Task: Refactor and Verify Coverage
- [ ] Task: Confirm the track 0 visual baseline still passes.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
