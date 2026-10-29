All semantic sizes and parent colour inheritance modes are showcased side by side below.

```canvas
<l-cluster gap="var(--dds-space-md)" align="center" style="color: var(--dds-text-default-color);">
  {% dds__icon name="component" size="xs" %}
  {% dds__icon name="component" size="sm" %}
  {% dds__icon name="component" size="md" %}
  {% dds__icon name="component" size="lg" %}
</l-cluster>
```

## Accessibility

### Decorative Icon (Default)

When `label` is omitted, the icon is rendered with `aria-hidden="true"` so assistive technologies ignore it.

### Accessible Icon

Provide `label` when the icon conveys meaning without accompanying visible text. This sets `role="img"` and `aria-label` on the root `<svg>`.

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

The complete built-in icon set is showcased below with every icon rendered next to its identifier.

```canvas
<style>
  .icon-catalogue-heading {
    color: var(--dds-text-muted-color);
    font-size: var(--dds-text-caption-size);
    font-weight: var(--dds-text-caption-weight, 600);
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  .icon-card {
    background-color: var(--dds-surface-bg-color);
    border: 1px solid var(--dds-control-border-color);
    border-radius: var(--dds-control-border-radius);
    color: var(--dds-text-default-color);
  }
  .icon-card code {
    background-color: var(--dds-surface-code-bg-color);
    color: var(--dds-surface-code-text-default-color);
    border: 1px solid var(--dds-surface-code-border-color);
    border-radius: var(--dds-control-border-radius);
    font-family: var(--dds-text-code-font);
    font-size: var(--dds-text-code-size);
    padding: 2px 6px;
  }
</style>
<l-stack style="--space: var(--dds-space-lg);">
  <l-stack style="--space: var(--dds-space-xs);">
    <strong class="icon-catalogue-heading">Navigation &amp; UI</strong>
    <l-grid style="--min: 160px; --space: var(--dds-space-xs);">
      <l-box class="icon-card" style="--space: var(--dds-space-xs);"><l-cluster style="--space: var(--dds-space-xs);" align="center">{% dds__icon name="chevron-down" %} <code>chevron-down</code></l-cluster></l-box>
      <l-box class="icon-card" style="--space: var(--dds-space-xs);"><l-cluster style="--space: var(--dds-space-xs);" align="center">{% dds__icon name="chevron-right" %} <code>chevron-right</code></l-cluster></l-box>
      <l-box class="icon-card" style="--space: var(--dds-space-xs);"><l-cluster style="--space: var(--dds-space-xs);" align="center">{% dds__icon name="menu" %} <code>menu</code></l-cluster></l-box>
      <l-box class="icon-card" style="--space: var(--dds-space-xs);"><l-cluster style="--space: var(--dds-space-xs);" align="center">{% dds__icon name="close" %} <code>close</code></l-cluster></l-box>
      <l-box class="icon-card" style="--space: var(--dds-space-xs);"><l-cluster style="--space: var(--dds-space-xs);" align="center">{% dds__icon name="external-link" %} <code>external-link</code></l-cluster></l-box>
    </l-grid>
  </l-stack>

  <l-stack style="--space: var(--dds-space-xs);">
    <strong class="icon-catalogue-heading">Status &amp; Feedback</strong>
    <l-grid style="--min: 160px; --space: var(--dds-space-xs);">
      <l-box class="icon-card" style="--space: var(--dds-space-xs);"><l-cluster style="--space: var(--dds-space-xs);" align="center">{% dds__icon name="check" %} <code>check</code></l-cluster></l-box>
      <l-box class="icon-card" style="--space: var(--dds-space-xs);"><l-cluster style="--space: var(--dds-space-xs);" align="center">{% dds__icon name="info" %} <code>info</code></l-cluster></l-box>
      <l-box class="icon-card" style="--space: var(--dds-space-xs);"><l-cluster style="--space: var(--dds-space-xs);" align="center">{% dds__icon name="success" %} <code>success</code></l-cluster></l-box>
      <l-box class="icon-card" style="--space: var(--dds-space-xs);"><l-cluster style="--space: var(--dds-space-xs);" align="center">{% dds__icon name="warning" %} <code>warning</code></l-cluster></l-box>
      <l-box class="icon-card" style="--space: var(--dds-space-xs);"><l-cluster style="--space: var(--dds-space-xs);" align="center">{% dds__icon name="error" %} <code>error</code></l-cluster></l-box>
    </l-grid>
  </l-stack>

  <l-stack style="--space: var(--dds-space-xs);">
    <strong class="icon-catalogue-heading">Content &amp; Files</strong>
    <l-grid style="--min: 160px; --space: var(--dds-space-xs);">
      <l-box class="icon-card" style="--space: var(--dds-space-xs);"><l-cluster style="--space: var(--dds-space-xs);" align="center">{% dds__icon name="doc" %} <code>doc</code></l-cluster></l-box>
      <l-box class="icon-card" style="--space: var(--dds-space-xs);"><l-cluster style="--space: var(--dds-space-xs);" align="center">{% dds__icon name="folder" %} <code>folder</code></l-cluster></l-box>
      <l-box class="icon-card" style="--space: var(--dds-space-xs);"><l-cluster style="--space: var(--dds-space-xs);" align="center">{% dds__icon name="folder-open" %} <code>folder-open</code></l-cluster></l-box>
      <l-box class="icon-card" style="--space: var(--dds-space-xs);"><l-cluster style="--space: var(--dds-space-xs);" align="center">{% dds__icon name="code" %} <code>code</code></l-cluster></l-box>
      <l-box class="icon-card" style="--space: var(--dds-space-xs);"><l-cluster style="--space: var(--dds-space-xs);" align="center">{% dds__icon name="file-code" %} <code>file-code</code></l-cluster></l-box>
    </l-grid>
  </l-stack>

  <l-stack style="--space: var(--dds-space-xs);">
    <strong class="icon-catalogue-heading">Actions</strong>
    <l-grid style="--min: 160px; --space: var(--dds-space-xs);">
      <l-box class="icon-card" style="--space: var(--dds-space-xs);"><l-cluster style="--space: var(--dds-space-xs);" align="center">{% dds__icon name="search" %} <code>search</code></l-cluster></l-box>
      <l-box class="icon-card" style="--space: var(--dds-space-xs);"><l-cluster style="--space: var(--dds-space-xs);" align="center">{% dds__icon name="copy" %} <code>copy</code></l-cluster></l-box>
      <l-box class="icon-card" style="--space: var(--dds-space-xs);"><l-cluster style="--space: var(--dds-space-xs);" align="center">{% dds__icon name="reset" %} <code>reset</code></l-cluster></l-box>
      <l-box class="icon-card" style="--space: var(--dds-space-xs);"><l-cluster style="--space: var(--dds-space-xs);" align="center">{% dds__icon name="eye" %} <code>eye</code></l-cluster></l-box>
    </l-grid>
  </l-stack>

  <l-stack style="--space: var(--dds-space-xs);">
    <strong class="icon-catalogue-heading">Theme &amp; Display</strong>
    <l-grid style="--min: 160px; --space: var(--dds-space-xs);">
      <l-box class="icon-card" style="--space: var(--dds-space-xs);"><l-cluster style="--space: var(--dds-space-xs);" align="center">{% dds__icon name="sun" %} <code>sun</code></l-cluster></l-box>
      <l-box class="icon-card" style="--space: var(--dds-space-xs);"><l-cluster style="--space: var(--dds-space-xs);" align="center">{% dds__icon name="moon" %} <code>moon</code></l-cluster></l-box>
      <l-box class="icon-card" style="--space: var(--dds-space-xs);"><l-cluster style="--space: var(--dds-space-xs);" align="center">{% dds__icon name="monitor" %} <code>monitor</code></l-cluster></l-box>
      <l-box class="icon-card" style="--space: var(--dds-space-xs);"><l-cluster style="--space: var(--dds-space-xs);" align="center">{% dds__icon name="rtl" %} <code>rtl</code></l-cluster></l-box>
      <l-box class="icon-card" style="--space: var(--dds-space-xs);"><l-cluster style="--space: var(--dds-space-xs);" align="center">{% dds__icon name="box-model" %} <code>box-model</code></l-cluster></l-box>
      <l-box class="icon-card" style="--space: var(--dds-space-xs);"><l-cluster style="--space: var(--dds-space-xs);" align="center">{% dds__icon name="ruler" %} <code>ruler</code></l-cluster></l-box>
      <l-box class="icon-card" style="--space: var(--dds-space-xs);"><l-cluster style="--space: var(--dds-space-xs);" align="center">{% dds__icon name="component" %} <code>component</code></l-cluster></l-box>
      <l-box class="icon-card" style="--space: var(--dds-space-xs);"><l-cluster style="--space: var(--dds-space-xs);" align="center">{% dds__icon name="component-variants" %} <code>component-variants</code></l-cluster></l-box>
      <l-box class="icon-card" style="--space: var(--dds-space-xs);"><l-cluster style="--space: var(--dds-space-xs);" align="center">{% dds__icon name="variant" %} <code>variant</code></l-cluster></l-box>
    </l-grid>
  </l-stack>
</l-stack>
```

