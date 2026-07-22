# Figma Plugin Repository

## Overview
Initialize and build `dj-design-system-figma`, a standalone reference Figma plugin for `dj-design-system`. This repository will be set up with a full Conductor environment and matching development tooling (`just`, Vitest, Vite). The plugin connects to the `dj-design-system` API to deliver four core capabilities: live component previews, API/prop linting, design token synchronization, and a hard link between Figma components and Django code.

## Functional Requirements
1. **Repository Setup:** Initialize a new git repository (`dj-design-system-figma`) alongside the main repo, utilizing `just` as the task runner, Vite for the build system, and React/TypeScript for development.
2. **Conductor Setup:** Initialize the Conductor SDD process (`index.md`, `product.md`, `workflow.md`, `tech-stack.md`) in the new repo, mirroring the high standards of the main repo.
3. **Plugin Capabilities:**
   - **Authentication:** Securely store API credentials using `figma.clientStorage`.
   - **Hard Link:** Allow designers to link a Figma node to a specific Django component registry entry.
   - **Live Previews:** Render an interactive iframe of the linked Django component alongside the Figma node.
   - **Prop Linting:** Compare the properties applied to the Figma component against the Django component's accepted props/variants (fetched from the API) and highlight mismatches.
   - **Token Synchronization:** Fetch design tokens (colors, spacing) from the Django backend and automatically update/create corresponding Figma Variables.

## Non-Functional Requirements
- **Tooling Parity:** Ensure the testing (Vitest), linting (ESLint/Prettier), and task execution (`just`) match the rigorous standards of the Django backend.
- **Maintainability:** The plugin architecture must be highly modular so consumers can fork and customize it easily.

## Acceptance Criteria
- [ ] A new `dj-design-system-figma` repository exists and is fully initialized with Conductor.
- [ ] A developer can run `just setup`, `just test`, and `just build` to manage the plugin lifecycle.
- [ ] The plugin can authenticate with the Django API.
- [ ] The plugin provides UI for linking components, previewing them, linting props, and syncing tokens.
