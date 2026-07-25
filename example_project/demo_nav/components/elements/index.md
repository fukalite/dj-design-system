# Elements

Atomic UI elements — the smallest building blocks of the design system.

These components have no dependencies on other components and can be used
anywhere in a page layout.

## Composition and HTML Embedding

The canvas rendering engine allows you to seamlessly mix native HTML with component tags to create rich examples and demonstrate layout composition:

```canvas
<div style="background: var(--surface-2, #f8f9fa); padding: 2rem; border-radius: 8px; border: 2px dashed #ccc; text-align: center;">
    <h3 style="margin-top: 0;">Complex Composition Example</h3>
    <p style="margin-bottom: 1.5rem;">
        You can wrap components in any HTML tags you need, or even place components side-by-side using Flexbox!
    </p>
    <div style="display: flex; gap: 1rem; justify-content: center; align-items: center;">
        <span>✔️</span>
        {% button "Confirm Action" %}
    </div>
</div>
```

## Relative Links

You can seamlessly link between documentation using standard relative links. For example, check out the [Icon Element](icon/index.md) or read its [Accessibility Guidelines](icon/accessibility.md).
