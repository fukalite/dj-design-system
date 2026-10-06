---
trigger: model_decision
description: When editing python code
---

# Python Rules

Adapted from the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
to fit this project. [general.md](general.md) also applies. Formatting is
enforced by tooling and is not repeated here.

**BE CONSISTENT.** When editing code, match the existing style.

## Architecture & Structure
- **Layering**: Follow [layered-architecture.md](layered-architecture.md). Business logic holds rules and processes (including side effects); services read and change data for their own app.
- **Decoupling**: Minimise dependencies and coupling. Wrap side-effect libraries in services to limit the blast radius.
- **Global State**: Avoid mutable global state.
- **Scripts**: Executable files keep their logic in a `main()` function, called from an `if __name__ == "__main__":` block.

## Imports
- Use `import x` for packages and modules. Use `from x import y` only when `y` is a submodule.
- Prefer module-level imports over local ones, except to avoid a specific circular dependency.
- Never import `_`-prefixed names from another module.

## Language
- **Keyword Arguments**: Always use keyword arguments when calling functions.
- **Data Handling**: Use dataclasses instead of raw dicts or lists for passing data.
- **Constants**: Use a constant for any string referenced in more than one place, and collate constants.
- **Default Arguments**: Never use mutable objects (`[]`, `{}`) as default values.
- **Comprehensions**: Use for simple cases. Prefer a full loop when the logic is complex.
- **True/False Evaluations**: Use implicit false (`if not my_list:`). Use `if foo is None:` to check for `None`.
- **Exceptions**: Never use a bare `except:`.
- **Strings**: Use f-strings for formatting.
- **Nested Functions**: Do not define functions inside other functions. Use a module-level function (with `functools.partial` to bind arguments) or a method. The exception is a standard pattern that needs a closure, such as a decorator's wrapper.

## Naming
- `snake_case` for modules, functions, methods and variables.
- `PascalCase` for classes.
- `ALL_CAPS_WITH_UNDERSCORES` for module-level constants.
- A single leading underscore (`_internal`) marks a member used only within its module or class.

## Typing & Documentation
- **Type Checking**: Use specific types everywhere. Collate custom types. Never rely on duck typing. Add type hints as you come across missing ones.
- **Docstrings**: Use `"""triple double quotes"""`. Start with a one-line summary, then `Args:`, `Returns:` and `Raises:` sections where relevant. Public modules, functions, classes and methods should have one.
- **Comments**: Do not comment code or tests. If code isn't understandable, refactor it. Inline comments are a last resort for rare, unavoidable complexity.
- **`TODO` Comments**: Use the `TODO(username): Fix this.` format.

## Testing & Tooling
- **Validation**: All code must be linted, formatted and type-checked (use automated fixes where available).
- **Service Testing**: Test services exhaustively (happy path and all edge cases).
- **Scope**: Do not test out-of-the-box (OOTB) functionality (e.g. built-in model/view methods).
- **Fixtures**: All test fixtures MUST be co-located in a `conftest.py` file. Do not define fixtures within individual test files.
- **Pytest Assertion Style**: Always use standard Python `assert` statements in tests (e.g. `assert a == b`, `assert x in y`). Do NOT use unittest-style assertion methods (such as `self.assertEqual`, `self.assertIn`, or `self.assertNotIn`) as they violate pytest best practices and Ruff rules (PT009).
