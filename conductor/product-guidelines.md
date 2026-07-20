# Product Guidelines

## Brand & Voice
- **Tone:** Professional, clear, and helpful.
- **Audience:** Fellow developers. Communication should be technically accurate without being unnecessarily academic.

## Core UX & Architectural Principles
- **Highly Customisable:** The framework should adapt to the user's needs, providing hooks and configuration overrides wherever possible.
- **Opinionated Python, Unopinionated Structure:** The tool is strict and opinionated about how components are implemented in Python (to ensure consistency and safety), but it intentionally leaves the directory structure, file organisation, and categorisation of the design system entirely up to the user.
- **Predictability:** The gallery should feel native to Django developers. Use standard Django terminology (e.g., apps, templates, templatetags).
- **Transparency:** Error messages (like component resolution failures) should be explicit and guide the user toward a solution.
- **Accessibility:** Ensure the interactive gallery and generated documentation are readable and usable.

## Code & Docs Style
- **Documentation:** Provide clear examples for every component.
- **Pythonic:** Follow standard Python and Django conventions for naming and structure.
