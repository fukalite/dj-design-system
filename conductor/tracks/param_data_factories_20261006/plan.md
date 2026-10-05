# Implementation Plan: Parameter Data Factories

## Phase 1: Factory Core & Registry
- [ ] Task: Resolve open questions in spec (dependency choice, registration mechanism)
- [ ] Task: Define the factory protocol and registry
  - [ ] Write failing tests for registering/resolving factories by param class (MRO lookup) and by component parameter.
  - [ ] Implement the registry and seeded generation context.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 2: Built-in Factories
- [ ] Task: Primitive and CSS class param factories
  - [ ] Write failing tests asserting generated values pass `validate()` and respect `choices` / `required` / `default`.
  - [ ] Implement factories.
- [ ] Task: Django-backed param factories (`ModelParam`, `UserParam`, `FileParam`, `ImageParam`)
  - [ ] Write failing tests, including `factory_boy` integration for `ModelParam`.
  - [ ] Implement factories.
- [ ] Task: `build_component_kwargs(component, seed=...)` helper
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 3: Gallery, Sandbox & Testing Integration
- [ ] Task: Allow generated values in `Variant.kwargs` / `GalleryConfig.param_defaults`
- [ ] Task: Sandbox "fill with sample data" action
- [ ] Task: Expose generation to `dj_design_system.testing` / `IterationEngine`
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

## Phase 4: Documentation
- [ ] Task: Document built-in factories and custom factory registration in `docs/`
- [ ] Task: Add a custom factory example to `example_project`
- [ ] Task: Update `CHANGELOG.md` under `[Unreleased]`
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
