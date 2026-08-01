# Component API Integration

## Overview
Introduce a new API to `dj-design-system` that serves component metadata and live interactive previews. This API acts as the foundational backend required for future external integrations, specifically a Figma plugin and automated integration testing (e.g., Playwright). The API is designed to serve both component registries and isolated HTML/CSS sandbox environments.

## Functional Requirements
1. **Registry Endpoint:** Provide a base API endpoint/view that serializes and returns a list of all registered components, their accepted properties, and variants as JSON.
2. **Render Endpoint:** Provide an API endpoint (or utilize existing gallery sandbox infrastructure) to serve the live, isolated HTML/CSS of a specific component state.
3. **Wholesale Routing:** Provide a pre-configured URL router (`urls.py`) that consumers can include wholesale in their Django project (e.g., `path('api/components/', include('dj_design_system.api.urls'))`).

## Non-Functional Requirements
- **Extensibility & Security:** The base views must be easily subclassable so consumers can override them to inject custom authentication, permissions, or caching logic.
- **Serializer Modifiability (CRITICAL):** The serializers and output formats used by the endpoints must be highly decoupled and easily extensible. Consumers must be able to modify the payload structure to support varying future needs (e.g., specific metadata required for Playwright tests vs. Figma node generation).
- **Forward Compatibility:** The rendered HTML payload structure must be designed with the future "HTML-to-Figma" conversion feature in mind (e.g., ensuring all necessary styles and contextual CSS are included).

## Acceptance Criteria
- [ ] A developer can include the API route in their Django project with a single `include()` statement.
- [ ] A GET request to the registry endpoint returns a valid JSON payload containing all registered components.
- [ ] A GET request to the render endpoint for a valid component returns its isolated, rendered HTML/CSS.
- [ ] The API can be secured by a consumer subclassing the views and adding custom permission classes.
- [ ] The API response structure can be altered by a consumer extending the default serializers.

## Out of Scope
- Development of the actual Figma plugin (handled in a separate track).
- Writing the Playwright integration tests (handled in a separate track).
- Converting HTML/CSS into native Figma vector layers.
