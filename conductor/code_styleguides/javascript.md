---
trigger: model_decision
description: When editing TypeScript or JavaScript code
---

# TypeScript & JavaScript Style Guide

This document defines the TypeScript and ES module standards for `dj-design-system`, based on the Google TypeScript / JavaScript Style Guide.

## 1. Source File Basics

-   **Language & Compilation:** Author all client-side component and gallery modules in strict TypeScript (`.ts`). Compiled `.js` sibling files are gitignored and emitted in place via `just build-ts` (`tsc -p tsconfig.json`).
-   **File Naming:** All lowercase, using underscores (`_`) for co-located component modules (`search_box.ts`) and dashes (`-`) for static page-level modules (`theme-manager.ts`).
-   **File Encoding:** UTF-8.
-   **Whitespace:** Use only ASCII horizontal spaces (`0x20`). Tabs (`\t`) and trailing whitespace are forbidden.

## 2. Source File Structure

-   **File Header:** Every `.ts` file must start with a `@fileoverview` JSDoc block.
-   **ES Modules:** All files are ES modules (`import`/`export`).
-   **Exports:** Use named exports (`export class DDSPopoutElement ...`). **Do not use default exports** in package source files.
-   **Imports:** Always include the `.js` extension in relative import paths (`import type { DDSCustomElement } from '../../types.js';`) so emitted ES2022 modules resolve natively in the browser without a bundler.

## 3. Formatting

-   **Braces:** Required for all control structures (`if`, `for`, `while`, etc.), even single-line blocks. Use K&R style ("Egyptian brackets").
-   **Indentation:** +2 spaces for each new block.
-   **Semicolons:** Every statement must be terminated with a semicolon.
-   **Column Limit:** 80 characters maximum per line (enforced by the test suite).
-   **Whitespace:** Use single blank lines between methods. No trailing whitespace.

## 4. Language Features

-   **Strict Typing:** Must compile cleanly under `strict: true`, `noImplicitAny: true`, `strictNullChecks: true`, `noUnusedLocals: true`, `noUnusedParameters: true`, and `noImplicitReturns: true`.
-   **Variable Declarations:** Use `const` by default, `let` if reassignment is needed. **`var` is forbidden.**
-   **Array & Object Literals:** Use trailing commas on multiline literals and shorthand properties where appropriate.
-   **Classes:** Avoid JavaScript getter/setter properties (`get name()`); provide ordinary methods instead (`isGalleryThemeDark()`, `selectValue(value)`).
-   **Functions:** Prefer arrow functions for callbacks and event listeners to preserve lexical `this`.
-   **String Literals:** Use single quotes (`'`) for string literals. Use template literals (`` ` ``) for interpolation or multi-line strings.
-   **Control Structures:** Prefer `for (const item of items)` loops.
-   **Equality Checks:** Always use strict identity operators (`===` / `!==`).

## 5. Disallowed Features

-   `with` keyword, `eval()`, or `Function(...string)`.
-   Automatic Semicolon Insertion.
-   Modifying built-in prototypes.
-   Shadow DOM (`attachShadow`) in `<dds-*>` custom elements.
-   Global side-effects (`localStorage`, `sessionStorage`, `document.cookie`, `window.location.href`) inside reusable element or composite custom elements (delegate to page-level managers via bubbling `dds:*` `CustomEvent`s).

## 6. Naming

-   **Classes & Interfaces:** `UpperCamelCase` (e.g. `DDSPopoutElement`, `ThemeManager`).
-   **Methods & Functions:** `lowerCamelCase`.
-   **Constants:** `CONSTANT_CASE`.
-   **Non-constant Fields & Variables:** `lowerCamelCase`.

## 7. JSDoc

-   Include JSDoc comments on all classes, fields, and methods.
-   Use `@fileoverview`, `@param`, `@return`.

## 8. Native Testing (`Vitest` + `happy-dom`)

-   Test all `<dds-*>` custom elements and static managers natively in `tests/ts/<name>.test.ts` using Vitest (`just test-ts` or `just test`).
-   Mount real DOM fixtures in `happy-dom`, trigger real events/methods, and assert on DOM state, ARIA attributes, custom event payloads, storage, and `AbortController` teardown.
-   Never test `.ts` source files via substring assertions in Python `pytest` suites.
