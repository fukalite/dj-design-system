---
trigger: always_on
---

# General Coding Best Practices

## Naming Conventions
- **Outcome-Oriented**: Name variables, attributes, and functions based on their **outcome** or **intent**, not their internal representation.
- **Verb-Noun Pattern**: Prefer the `verb_noun` pattern for functions/methods (e.g., `get_user_profile`, `save_configuration`, `validate_email`).
- **Clarity over Brevity**: A descriptive name is always better than a cryptic one. Avoid abbreviations unless they are industry standard (e.g., `id`, `url`).

## Pattern Reuse & Consistency
- **Idiomatic Usage**: Always use the most idiomatic patterns for the project's base frameworks (e.g., React hooks, Pythonic list comprehensions).
- **Existing Patterns**: Research the codebase before implementing something new. If a pattern for your task already exists, reuse it to maintain consistency.
- **DRY (Don't Repeat Yourself)**: Extract common logic into reusable functions or components, but avoid over-abstraction.
- **YAGNI**: Don't over-build features until you know they're needed; a smaller surface area is better.

## Logic & Flow
- **Keep cognitive load low.**
- **Guard Clauses**: Use guard clauses to handle edge cases and errors early, reducing nested `if/else` blocks.
- **Function Responsibility**: Keep functions small and focused on a single concern. If a function does more than one thing, split it.

## Error Handling
- **Explicit Failure**: Raise exceptions early and clearly. Custom exceptions are preferred over generic ones.
- **Fail Silently?**: Only fail silently if explicitly instructed, and ensure the reason is documented and covered by tests.

## Documentation
- **Self-Documenting Code**: Write code that is easy to understand without comments. If it's not clear, refactor it. Make exceptions to this rule clear to the user.
- **Docblocks**: Use standard docblock formats for your language to describe function parameters, return values, and intended use.
- **Relative Links**: Always use relative file links (e.g., `[filename](../path/to/file)`) rather than absolute system paths (e.g., `file:///Users/...`) when referencing other files in code comments, markdown documents, plans, or codebase documentation.
