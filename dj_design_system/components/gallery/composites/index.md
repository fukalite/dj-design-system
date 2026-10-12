# Composite Components

The `composites` collection contains the specialized, gallery-specific components that compose the interactive design system workbench, navigation shell, inspection tools, and preview stage.

Unlike the domain-agnostic `elements`, composite components encapsulate "the way the gallery displays and inspects components". They consume structured framework dataclasses and orchestrate rich interactions across the gallery shell.

## Architectural Rules & Invariants

1. **Composition Over Duplication**: Composite components must never reimplement primitive UI patterns. They compose `elements` primitives (`{% dds__button %}`, `{% dds__icon %}`, `{% dds__popout %}`, `{% dds__form_field %}`) via template tags and slots.
2. **Structured Dataclass Consumption**: Presentation logic in composite components accepts high-level dataclasses (`NavNode`, `ComponentInfo`, `GalleryConfig`, `Theme`) and decomposes them in `get_context()` into declarative parameters for child elements.
3. **Light DOM Web Components**: Client-side interactivity is implemented via Light DOM Custom Elements (`<dds-*>`) with strict lifecycle management (`connectedCallback`, `disconnectedCallback`, `AbortController`).
4. **Decoupled Custom Events**: Inter-component communication across the gallery workbench occurs via bubbling custom events (`dds:canvas-mode-change`, `dds:canvas-resize`, `dds:theme-change`, `dds:split-resize`) rather than direct DOM references.
5. **CUBE CSS Layering & Token Mapping**: Styles live in `@layer blocks`, using local Tier 3 tokens (`--_<component>-*`) mapping exclusively to Tier 2 design tokens (`--dds-*`).
