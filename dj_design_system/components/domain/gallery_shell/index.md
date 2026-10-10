# Gallery Shell (`dds__gallery_shell`)

The `dds__gallery_shell` domain component renders the top-level application shell (`<dds-gallery-shell class="dds-gallery-shell">`) for the design system gallery. It composes `{% dds__toolbar %}` in `[data-shell-topbar]`, an Every Layout `.l-sidebar` body (`[data-shell-body]`) housing the mobile scrim (`[data-shell-backdrop]`), `{% dds__sidebar %}` drawer (`[data-shell-sidebar]`), and the primary `<main class="dds-gallery-shell-main" data-surface="docs" data-shell-main>` content landmark.

## When to Use

- Wrapping gallery documentation, folder listing, and component variant views in a unified responsive shell.
- Providing responsive mobile navigation drawer toggling (`dds:drawer-toggle`) and live theme synchronisation (`dds:theme-change`).
- Overriding the topbar or sidebar landmarks via named `topbar` and `sidebar` slots while preserving the shell layout and `<main>` surface.

## Parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `brand_name` | `str` | `"Design System"` | Design system name passed to `dds__toolbar` and `dds__sidebar`. |
| `brand_url` | `str` | `"/"` | Root gallery URL passed to `dds__toolbar` and `dds__sidebar`. |
| `nodes` | `list` | `None` | Navigation tree nodes passed to `dds__sidebar`. |
| `active_path` | `str` | `""` | Active route path passed to `dds__sidebar`. |
| `active_variant` | `str` | `""` | Active variant slug or `Variant` instance passed to `dds__sidebar`. |
| `breadcrumbs` | `list` | `None` | Breadcrumb trail items passed to `dds__toolbar`. |
| `themes` | `list` | `None` | Available gallery themes passed to `dds__toolbar`. |
| `active_theme` | `str` | `"light"` | Active gallery theme identifier (`data-theme`). |
| `search_index` | `list` | `None` | Client-side search index entries passed to `dds__toolbar`. |

## Slots

| Slot | Required | Description |
| :--- | :--- | :--- |
| `topbar` | `False` | Optional custom topbar override replacing `{% dds__toolbar %}` inside `[data-shell-topbar]`. |
| `sidebar` | `False` | Optional custom sidebar override replacing `{% dds__sidebar %}` inside `[data-shell-sidebar]`. |
| `toolbar_actions` | `False` | Optional extra actions injected into the default `{% dds__toolbar %}` `actions` slot. |
| `main` | `False` | Optional main content slot rendered inside `[data-shell-main]` (falls back to block `content` when instantiated in Python). |

## Client-Side Custom Element (`<dds-gallery-shell>`)

- **Drawer Toggle:** Clicking any `[data-action="toggle-drawer"]` or `[data-drawer-toggle]` control within `<dds-gallery-shell>` toggles `data-drawer-state` between `"open"` and `"closed"`, updates `aria-expanded` on triggers, toggles `hidden` on `[data-shell-backdrop]`, and dispatches a bubbling `dds:drawer-toggle` `CustomEvent` (`detail: { open }`).
- **Dismissal:** Clicking `[data-shell-backdrop]` or pressing `Escape` while `data-drawer-state="open"` closes the drawer.
- **Theme Synchronisation:** Listening for bubbling `dds:theme-change` events updates `data-theme` and toggles `.gallery-theme-dark` / `.gallery-theme-light` on `<dds-gallery-shell>` and `document.documentElement`.

## Template Usage

```django
{% load design_components %}

{% dds__gallery_shell brand_name="Design System" brand_url="/gallery/" nodes=nodes active_path=active_path breadcrumbs=breadcrumbs themes=themes active_theme=active_theme search_index=search_index %}
  {% slot "toolbar_actions" %}
    {% dds__button "GitHub" variant="ghost" size="sm" href="https://example.com" %}
  {% endslot %}
  {% slot "main" %}
    <h1>Getting Started</h1>
  {% endslot %}
{% enddds__gallery_shell %}
```
