# Icon (`dds__icon`)

The `dds__icon` primitive renders an inline 24x24 stroke-based SVG icon with semantic sizing and built-in accessibility attributes.

## Usage

### Decorative Icon (Default)

When `label` is omitted, the icon is rendered with `aria-hidden="true"` so assistive technologies ignore it:

```canvas
{% dds__icon "component" %}
```

### Accessible Icon

Provide `label` when the icon conveys meaning without accompanying visible text. This sets `role="img"` and `aria-label` on the root `<svg>`:

```canvas
{% dds__icon "search" size="lg" label="Search components" %}
```

## Semantic Sizes

| Size | Token Mapping |
| :--- | :--- |
| `xs` | `--dds-space-sm` |
| `sm` | `--dds-space-md` |
| `md` | `--dds-space-lg` (default) |
| `lg` | `--dds-space-xl` |
