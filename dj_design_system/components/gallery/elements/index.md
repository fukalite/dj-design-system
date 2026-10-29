# Elements

The `elements` collection contains the foundational, domain-agnostic UI primitives of the design system. These components are completely decoupled from application logic, routing, or gallery internals, making them universally reusable across any Django project.

## Architectural Rules & Invariants

1. **Zero Domain Coupling**: Elements must never import or reference gallery models, services, or URL structures. They receive data strictly via typed parameters and slots.
2. **Strict Boundary Encapsulation**: Component root elements set `margin: 0` and never dictate external spacing. External layout is managed exclusively by composition primitives (`<l-stack>`, `<l-cluster>`, etc.).
3. **CUBE CSS & 3-Tier Token Hierarchy**: All styles are declared in `@layer blocks`. Component properties map via scoped Tier 3 variables (`--_<element>-*`) strictly to Tier 2 design tokens (`--dds-*`).
4. **Zero HTML in Python**: Component Python modules (`<name>.py`) prepare presentation context and must never import `mark_safe`, `format_html`, or construct raw HTML strings.
5. **Accessible Semantics**: Prefer native semantic HTML elements (`<button>`, `<nav>`, `<table>`). Interactive enhancements use Light DOM Custom Elements (`<dds-*>`) with scoped event dispatching and standard ARIA roles.
