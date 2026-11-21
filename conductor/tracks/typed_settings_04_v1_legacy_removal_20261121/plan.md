# Implementation Plan: Track 4 — v1.0.0 Legacy Settings Removal

## Phase 1: Migrate Remaining Test Overrides
- [x] Task: Audit all `DJ_DESIGN_SYSTEM = {...}` usages across `tests/` and migrate them to `DesignSystemSettings` / `.replace(...)`.
- [x] Task: Quality Check (`just check`, `just typecheck`, `just test`)
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Delete Legacy Adapter, Proxy & Migration CLI
- [x] Task: Red Phase — Replace legacy dict acceptance tests with assertions that plain `dict` triggers `E009` and `ImproperlyConfigured`.
- [x] Task: Green Phase — Remove the legacy dict adapter, `dds_settings` / `DEFAULTS` / `BUILTIN_*` shims, `E020` / `W010`–`W012`, `RemovedInDjDS10Warning`, and `manage.py migrate_dds_settings`.
- [x] Task: Refactor Phase — Clean up `docs/configuration.md` and promote initiative design decisions as appropriate before initiative closure.
- [x] Task: Quality Check (`just check`, `just typecheck`, `just test`, `just docs-build`)
- [x] Task: Phase Verification & Checkpoint (Refer to workflow.md)
