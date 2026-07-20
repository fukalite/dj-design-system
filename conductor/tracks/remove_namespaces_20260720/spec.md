# Spec: Remove Deprecated COMPONENT_NAMESPACES

## Overview
The `COMPONENT_NAMESPACES` configuration option has been deprecated in favor of `COMPONENT_DIRECTORIES`, which provides more advanced capabilities like `promote_to_app`, `label` customization, and robust `FlattenStrategy` enum support. This track removes the deprecated option from the codebase.

## Functional Requirements
- Remove `COMPONENT_NAMESPACES` from `dj_design_system.settings.DEFAULTS` and `DjangoDesignSystemSettings`.
- Remove the deprecation warning added previously.
- Remove fallback logic in `dj_design_system.services.registry._resolve_namespace_prefix`.
- Remove any remaining references in documentation.

## Out of Scope
- Altering `COMPONENT_DIRECTORIES` parsing logic.
