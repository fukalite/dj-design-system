# Implementation Plan: Figma Plugin Repository

This plan outlines the phases to bootstrap the new `dj-design-system-figma` repository, initialize its Conductor environment, and build the core plugin features using a Test-Driven Development (TDD) workflow.

## Phase 1: Repository & Conductor Initialization
Establish the new repository and enforce the same rigorous SDD and task-running standards as the Django backend.

- [ ] Task: Create new directory `dj-design-system-figma` (alongside the main repo) and initialize a new git repository.
- [ ] Task: Create a comprehensive `justfile` mirroring the backend's developer experience (commands for setup, test, lint, build).
- [ ] Task: Initialize the Conductor environment (`conductor/index.md`, `product.md`, `tech-stack.md`, `workflow.md`).
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 2: Plugin Foundation & Tooling
Set up the React + TypeScript frontend architecture and testing environment.

- [ ] Task: Write Failing Tests (`Red Phase`)
  - [ ] Configure `Vitest` and write initial sanity check tests for the build environment.
- [ ] Task: Implement to Pass Tests (`Green Phase`)
  - [ ] Scaffold the Figma plugin structure using Vite, React, and TypeScript.
  - [ ] Configure `manifest.json`, the main thread script, and the UI iframe script.
  - [ ] Set up `ESLint` and `Prettier`.
- [ ] Task: Refactor and Verify Coverage
  - [ ] Ensure the base plugin builds correctly and passes all linting/testing gates.
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 3: Authentication & API Foundation
Implement secure communication with the Django backend API.

- [ ] Task: Write Failing Tests (`Red Phase`)
  - [ ] Write tests for the API client service (mocking fetch).
  - [ ] Write tests for token storage logic.
- [ ] Task: Implement to Pass Tests (`Green Phase`)
  - [ ] Create the API client wrapper in the plugin.
  - [ ] Implement the Settings UI for users to input the API Base URL and Token.
  - [ ] Implement secure credential storage using `figma.clientStorage`.
- [ ] Task: Refactor and Verify Coverage
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)

---

## Phase 4: Core Capabilities (Sync, Lint, Link, Preview)
Deliver the 4 primary benefits of the plugin architecture.

- [ ] Task: Write Failing Tests (`Red Phase`)
  - [ ] Write logic tests for comparing Figma properties to API component registries.
  - [ ] Write logic tests for mapping API design tokens to Figma variable structures.
- [ ] Task: Implement to Pass Tests (`Green Phase`)
  - [ ] **Token Synchronization:** Implement logic to fetch tokens from the API and create/update native Figma Variables.
  - [ ] **Hard Link & Preview:** Implement UI to select a component from the registry, link it to the selected Figma node, and render the live iframe preview.
  - [ ] **Prop Linting:** Implement background check to flag mismatches between Figma node properties and the Django API component definition.
- [ ] Task: Refactor and Verify Coverage
- [ ] Task: Phase Verification & Checkpoint (Refer to workflow.md)
