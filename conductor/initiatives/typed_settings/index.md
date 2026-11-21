# Initiative: Typed & Devolved Settings (`typed_settings`)

## Overview
Replace the 29 flat `DJ_DESIGN_SYSTEM` dictionary keys with grouped, deeply immutable, typed `*Settings` dataclasses (`DesignSystemSettings`, `GallerySettings`, `CanvasSettings`, `AppSettings`, `DirectorySettings`), devolve app-scoped defaults onto Django `AppConfig.design_system`, introduce manual and app-delegated navigation ordering, overhaul documentation around a single configuration hub, and deliver a `v0.10.0` deprecation and migration path leading to clean legacy removal in `v1.0.0`.

## Design Document & Styleguides
- [Architecture & Design Document](./design.md) *(canonical reference for all PRs in this initiative)*
- [Python & Django Layered Architecture](../../code_styleguides/layered-architecture.md)
- [Python Styleguide](../../code_styleguides/python.md)
- [General Coding Best Practices](../../code_styleguides/general.md)
- [Example Project Styleguide](../../code_styleguides/example-project.md)

## Tracks
1. [Track 1 — Typed Schema, Import-Safety & 4-Tier Resolution](../../tracks/typed_settings_01_schema_and_resolution_20261121/index.md)
2. [Track 2 — Compatibility Adapter, Migration CLI & Example Project](../../tracks/typed_settings_02_compat_and_migration_20261121/index.md)
3. [Track 3 — Documentation Overhaul & API Reference](../../tracks/typed_settings_03_documentation_overhaul_20261121/index.md)
4. [Track 4 — v1.0.0 Legacy Settings Removal](../../tracks/typed_settings_04_v1_legacy_removal_20261121/index.md)
