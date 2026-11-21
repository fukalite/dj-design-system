# Implementation Plan: Track 3 — Documentation Overhaul & API Reference

## Phase 1: `docs/configuration.md` & API Reference Foundation
- [ ] Task: Write `docs/configuration.md` covering Tiers 1–2 mental models, 4-tier override stack, additive render cascades, split settings (`.replace(...)`), `GallerySettings.enabled`, manual & app-delegated `nav_order` / `app_order`, Reusable & Contrib App Author Guide, external URLs, system checks, manual loader/finder setup, and dict migration guide (`manage.py migrate_dds_settings`).
- [ ] Task: Replace `docs/api/settings.md` with `mkdocstrings` directives for `dj_design_system.config` and verify clean rendering of type aliases (`HtmlAttrsDict`, `WebpackBundleSpec`, `NavOrderSpec`).
- [ ] Task: Replace orphan `docs/api-reference.md` with `docs/api/index.md` and update `mkdocs.yml` navigation.
- [ ] Task: Quality Check (`just docs-build`, `just check`)
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Holistic Rewrite of Thematic Guides
- [ ] Task: Rewrite `docs/quickstart.md` (Tier 0 zero-config install) and `docs/index.md` (navigation table + bug fixes).
- [ ] Task: Rewrite `docs/organisation.md` (devolved `AppConfig.design_system`, `DirectorySettings`, `nav_order`, fix colon syntax) and `docs/themes.md` (strictly theming/styling + full availability cascade).
- [ ] Task: Rewrite `docs/gallery.md` (remove shadow settings table, update snippets, fix token names), `docs/templatetags.md` (fix lowercase dict typos, add `app_label`/`theme` kwargs), `docs/registry.md`, and `docs/testing.md` (`@override_settings` + startup vs request-time boundary).
- [ ] Task: Quality Check (`just docs-build --strict`, `just check`, `just test`)
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
