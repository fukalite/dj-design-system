# Design Token System

## Overview
Introduce a highly flexible, opt-in `TokenRegistry` in Python to manage design tokens. This system acts as a source of truth for design tokens, capable of generating CSS for various build systems, exposing tokens via an API, and providing rich visual rendering inside the gallery and custom documentation.

## Functional Requirements
1. **Token Registry Structure:** An extremely flexible Python API/structure to register design tokens. It must support complex token architectures, including layered definitions (concrete vs. semantic tokens) and switching on dual axes (e.g., themes, light/dark mode variants).
2. **Settings API Refactor:** The library's existing settings and configuration API must be refactored to consume the new Token Registry seamlessly. Existing components and context processors must be updated to read from this new structure if active.
3. **CSS Generation & Emission:** Flexible output mechanisms. The system must be able to emit pure CSS strings, write output to a physical CSS file, render a `<style>` tag, or export tokens for frontend bundlers (Webpack/Vite).
4. **Gallery Rendering & Navigation:** A standard, overridable view for tokens with configurable nav placement (e.g., under "Foundations"), and markdown integration for custom docs.
5. **Theme UI Integration:** The defined registry axes (like light/dark modes) must automatically wire into and power the gallery's global theme selector controls.
6. **API Endpoint:** An API endpoint to serialize and expose the token registry as JSON.

## Non-Functional Requirements
- **Fully Optional:** The entire token registry architecture must remain entirely optional. Projects that prefer to rely exclusively on implicit CSS variables will experience no breakages or forced migrations.

## Acceptance Criteria
- [ ] A developer can define concrete and semantic tokens in Python handling multiple themes/axes.
- [ ] The system correctly generates CSS or Webpack-compatible exports.
- [ ] The library's existing configuration cleanly falls back or utilizes the new registry without breaking changes.
- [ ] The gallery visually renders the tokens on a dedicated page that can be positioned anywhere in the navigation.
- [ ] The gallery's theme selector correctly reflects and toggles between the defined axes.
- [ ] A GET request to the token API endpoint returns a properly serialized payload representing the complex architecture.
