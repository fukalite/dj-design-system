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

## Color Inheritance

Icons use `stroke="currentColor"` and default `--_icon-color` to `currentColor`. They automatically match the text colour of their container (such as inside a `.dds-button`, `.dds-notice`, or custom heading). To colour an icon independently, set `color` on the parent or override `--_icon-color`.

## Semantic Sizes

| Size | Token Mapping | Rendered Size |
| :--- | :--- | :--- |
| `xs` | `--dds-space-sm` | 8px (0.5rem) |
| `sm` | `--dds-space-md` | 12px (0.75rem) |
| `md` | `--dds-space-lg` (default) | 16px (1.0rem) |
| `lg` | `--dds-space-xl` | 24px (1.5rem) |

## Supported Icon Catalogue

| Category | Identifiers |
| :--- | :--- |
| **Navigation & UI** | `chevron-down`, `chevron-right`, `menu`, `close`, `external-link` |
| **Status & Feedback** | `check`, `info`, `success`, `warning`, `error` |
| **Content & Files** | `doc`, `folder`, `folder-open`, `code`, `file-code` |
| **Actions** | `search`, `copy`, `reset`, `eye` |
| **Theme & Display** | `sun`, `moon`, `monitor`, `rtl`, `box-model`, `ruler`, `component` |
