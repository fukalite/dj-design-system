# Specification: Documentation Overhaul & API Reference

Reference architecture: [Typed & Devolved Settings Design Document](../../initiatives/typed_settings/design.md) (§6).

## Overview
Restructure the user-facing documentation around legibility, progressive disclosure, and a single source of truth for configuration: introduce `docs/configuration.md` as the top-level configuration hub, replace the hand-maintained `docs/api/settings.md` with auto-generated `mkdocstrings` documentation, reorganise `mkdocs.yml`, and holistically rewrite affected guides to remove shadow tables and accumulated drift.

## Functional Requirements
1. **New `docs/configuration.md` Hub**:
   - Four-tier progressive disclosure: project settings overview (`DesignSystemSettings`), split settings with `.replace(...)`, disabling gallery per environment (`GallerySettings(enabled=False)`), devolved app defaults (`AppConfig.design_system = AppSettings(...)`), 4-tier override stack + additive render cascades, manual and app-delegated `nav_order` / `app_order`, a Reusable & Contrib App Author Guide (including `extra_css`/`extra_js` overrides and `verbose_name` fallback), external asset URLs, system checks (`E001`–`E020`, `W001`–`W012`), manual loader/finder registration, and Migrating from dict settings (including `manage.py migrate_dds_settings` and key mapping table).
2. **`mkdocs.yml` & API Reference Overhaul**:
   - Promote `Configuration: configuration.md` directly after `Quick Start`; group thematic pages under `Guides:`; rename `Themes and Assets` to `Themes & Styling`.
   - Replace the 294-line hand-written `docs/api/settings.md` with `mkdocstrings` directives targeting `dj_design_system.config` (and `dj_design_system.services.config` public accessors).
   - Replace orphan `docs/api-reference.md` with `docs/api/index.md` mounted as the API Reference index.
3. **Holistic Cross-Page Rewrites & Bug Fixes**:
   - `docs/quickstart.md`: Streamline to Tier 0 zero-config install (note auto-registered loader/finder), remove wrong `is_staff=True` claim, fix per-app `{% load components %}` typo.
   - `docs/organisation.md`: Add app-level configuration patterns (`AppConfig.design_system`, `DirectorySettings`, `nav_order`) and fix obsolete `{% demo_components:button %}` syntax.
   - `docs/themes.md`: Scope strictly to theming/styling, move app asset docs to `configuration.md`, document the full theme availability cascade.
   - `docs/gallery.md`: Delete the 13-row shadow `## Settings` table, update all inline snippets to `*Settings`, fix stale Tier 2 token names and wrong `GALLERY_CANVAS_EXTRA_BACKGROUNDS` schema.
   - `docs/templatetags.md`: Fix lowercase `dj_design_system` dict typos, duplicated `### Qualified Name` heading, and document `app_label=` / `theme=` kwargs on `{% global_stylesheets %}` / `{% global_scripts %}`.
   - `docs/index.md`, `docs/registry.md`, `docs/testing.md`: Add Configuration to navigation table, fix duplicate `StrParam` import and `/gallery/` demo link, document `@override_settings` with `.replace(...)` and the startup-bound vs request-time boundary.

## Non-Functional Requirements
- `just docs-build` succeeds cleanly with zero broken internal links or `mkdocstrings` resolution errors.
- All docs use British English, relative links, positive target-state voice, and zero shadow catalogues.

## Acceptance Criteria
- Every configuration concept has one canonical home; zero duplicated settings tables remain across `docs/`.
- `docs/api/settings.md` renders all 6 public `*Settings` classes cleanly via `mkdocstrings` with readable type annotations.
- All audited factual errors in existing docs are resolved.
