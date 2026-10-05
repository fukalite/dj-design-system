# Specification: Parameter Data Factories

## Overview
Component authors currently have to hand-write every value used in gallery variants, sandbox previews and test iterations (`Variant.kwargs`, `GalleryConfig.param_defaults`, `GalleryParameter`). The types are already declared on each component through its `BaseParam` descriptors (`StrParam`, `IntParam`, `DateParam`, `ModelParam`, `UserParam`, ...), along with `choices`, `default` and `required`, so the library has enough information to generate plausible data itself.

This track adds a factory layer that produces valid data for a component from its declared parameters, plus a public extension point so other developers can register their own factories for custom param types or for specific components/parameters.

## Goals
1. **Type-driven generation**: Given a component, produce a kwargs dict where every parameter receives a value that passes that param's `validate()`.
2. **Respect param metadata**: Pick from `choices` when set, honour `required` (optionally leave non-required params as `None`/unset), and use `default` where a "basic" output is requested.
3. **Built-in factories** for every shipped param type:
   - Primitives: `StrParam`, `BoolParam`, `IntParam`, `FloatParam`, `DecimalParam`, `DateParam`, `DateTimeParam`, `UUIDParam`, `DictParam`, `ListParam`, `JSONParam`.
   - CSS class variants: `StrCSSClassParam`, `BoolCSSClassParam`.
   - Django-backed: `ModelParam` / `UserParam` (unsaved model instances populated for `Meta.fields`), `FileParam`, `ImageParam`.
4. **Custom factories**: A documented API that lets developers:
   - Register a factory for their own `BaseParam` subclass (resolved via the param class MRO, so subclasses inherit a parent's factory unless overridden).
   - Override the factory for a specific component parameter (e.g. `Button.label`).
   - Plug in their existing `factory_boy` factories for `ModelParam` types.
   - Optionally declare a factory directly on a param subclass (e.g. a `factory` class attribute/hook).
5. **Determinism**: Accept a seed so generated data is reproducible (required for visual regression baselines and snapshot tests).

## Integration Points
- **Gallery**: Allow `Variant.kwargs` / `GalleryConfig.param_defaults` to reference generated values (e.g. a sentinel or helper such as `generate()`), and optionally auto-generate a variant for components with no gallery config.
- **Sandbox**: Offer a "fill with sample data" action that populates the sandbox form from factories.
- **Testing**: Expose a helper (e.g. `build_component_kwargs(component, seed=...)`) usable from `dj_design_system.testing` and the `IterationEngine` so plugins can iterate components with generated data.
- **`GalleryParameter`**: Generated values for complex types (models, querysets) should be wrapped with a sensible `code` representation for the template tag docs.

## Open Questions
- Should a faker-style dependency be introduced (optional extra) or should built-in factories stay dependency-free with simple deterministic values?
- Registration mechanism: Django setting (`DJ_DESIGN_SYSTEM["FACTORIES"]`), decorator-based registry, or both?
- How should factories handle params with cross-parameter constraints (e.g. one param only valid when another is set)?

## Acceptance Criteria
- Every built-in param type has a factory whose output passes the param's `validate()`.
- A developer can register a factory for a custom `BaseParam` subclass and for a single component parameter, and it takes precedence over built-ins.
- Generation with the same seed yields identical kwargs.
- Generated kwargs render every example project component without errors.
- Documentation covers built-in behaviour and writing/registering custom factories.
