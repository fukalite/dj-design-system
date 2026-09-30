---
trigger: model_decision
description: When editing python code
---

# Python & Django Coding Rules

## Architecture & Structure
- **Service Layers**: Use service layers for all logic, to handle all mutations and side effects.
- **Imports**: Prefer global imports over local ones (except to avoid specific circular dependencies).
- **Decoupling**: Minimize dependencies and coupling. Wrap side-effect libraries in service layers to limit blast area.
- **Module Scope**: Only use `_` prefix for functions scoped to the current module. Never import `_` functions from elsewhere.

## Logic & Flow
- **Style**: 
    - Prefer guard clauses over if/else (minimize indentation).
    - Prefer small functions over multi-concern loops.
    - Always use keyword arguments (`kwargs`) when calling functions.
- **Data Handling**: 
    - Use **Data Classes** instead of raw dicts/lists for passing data.
    - Use **Constants** for any string referenced in more than one place. Collate constants.
- **Error Handling**: 
    - Raise custom exceptions early. Never fail silently without explicit instruction and clear test coverage.

## Typing & Documentation
- **Type Checking**: Use specific types everywhere. Collate custom types. Don't ever use duck typing. Add type hinting as you come across it.
- **Comments**: **Do not comment code or tests.** If code isn't understandable, refactor it.
    - **Docblocks** are encouraged.
    - Inline comments are a last resort for rare, unavoidable complexity.

## Testing & Tooling
- **Validation**: All code must be linted, formatted, and type-checked (use automated fixes where available).
- **Service Testing**: Test service layer functionality exhaustively (happy path and all edge cases).
- **Scope**: Do not test out-of-the-box (OOTB) functionality (e.g., built-in model/view methods).
- **Fixtures**: All test fixtures MUST be co-located in a `conftest.py` file. Do not define fixtures within individual test files.
- **Pytest Assertion Style**: Always use standard Python `assert` statements in tests (e.g. `assert a == b`, `assert x in y`). Do NOT use unittest-style assertion methods (such as `self.assertEqual`, `self.assertIn`, or `self.assertNotIn`) as they violate pytest best practices and Ruff rules (PT009).
