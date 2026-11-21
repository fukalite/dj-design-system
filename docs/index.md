# Django Design System

**A reusable Django app for building, documenting, and shipping component libraries.**

Write your UI components as Django-native classes that look and work like Models or Forms. Django Design System auto-discovers them, renders live interactive previews in sandboxed iframes, generates template tag usage examples from your parameter definitions, and builds a fully searchable navigation gallery — all from your existing code and docstrings, with zero configuration required.

---

## What a component looks like

A component is a Python class. Declare its parameters, its HTML template, and its docstring — that's it.

```python
# myapp/components/button.py
from dj_design_system.components import TagComponent
from dj_design_system.parameters import BoolParam, StrParam


class ButtonComponent(TagComponent):
    """A configurable button with size and variant modifiers."""

    label = StrParam("The button label.")
    variant = StrParam(
        "Visual variant.",
        css_class=True,
        required=False,
        default="primary",
        choices=["primary", "secondary", "danger"],
    )
    disabled = BoolParam(
        "Renders the button as disabled.",
        css_class=True,
        required=False,
    )

    template_format_str = "<button class='btn {classes}'>{label}</button>"

    class Meta:
        positional_args = ["label"]
```

Use it in any Django template — no manual registration, no YAML:

```htmldjango
{% load design_components %}
{% button "Save changes" %}
{% button "Delete" variant="danger" disabled=True %}
```

The gallery generates the template tag syntax automatically and shows a live preview:

![Gallery preview showing the button component with its live iframe preview and generated tag signature](https://github.com/fukalite/dj-design-system/raw/main/docs/assets/gallery-preview.png)

**[Browse the demo gallery →](https://fukalite.github.io/dj-design-system/demo/)**

---

## Key features

**Auto-discovery** — components are found and registered automatically when Django starts. No registration calls, no config files.

**Typed & devolved configuration** — configure project settings with `DesignSystemSettings(...)` in `settings.py` and devolve app-level defaults onto `AppConfig.design_system = AppSettings(...)`. See [Configuration](configuration.md).

**Co-located templates and media** — place `.html`, `.css`, and `.js` files next to a component module and they are automatically discovered and served. Use `template_format_str` for concise inline fragments.

**Rich parameter types** — `StrParam`, `BoolParam`, `IntParam`, `ModelParam`, `UserParam`, and CSS/attribute parameter classes feed directly into the gallery documentation and sandbox form.

**Block components & named slots** — use `BlockComponent` and `Meta.slots` for components that wrap arbitrary template content and named regions.

**Multi-app namespaces** — register components across multiple Django apps and disambiguate with double-underscore qualified tags such as `{% myapp__button "Click" %}` or custom prefixes via `AppSettings(prefix=...)`.

**Markdown documentation** — place `index.md` or standalone `.md` files alongside your components for narrative documentation with live fenced `canvas` blocks.

**Integration testing** — install testing extras (such as `[testing-all]`) to assert accessibility, HTML validity, and visual regression across every variant and theme.

---

## Where to go next

| I want to… | Go to |
| --- | --- |
| See components in action | [Demo gallery](https://fukalite.github.io/dj-design-system/demo/) |
| Install and create my first component | [Quick Start](quickstart.md) |
| Configure settings, apps, and navigation | [Configuration](configuration.md) |
| Learn all parameter types and slots | [Components](components.md) |
| Structure apps, folders, and prefixes | [Organising Apps & Folders](organisation.md) |
| Customise the gallery UI and variants | [Gallery](gallery.md) |
| Configure themes, dark mode, and CSS tokens | [Themes & Styling](themes.md) |
| Use components and asset tags in templates | [Template Tags](templatetags.md) |
| Understand discovery and lookup APIs | [Registry](registry.md) |
| Test components automatically | [Integration Testing](testing.md) |
| Browse the full API reference | [API Reference](api/index.md) |
| Contribute to the project | [Contributing](https://github.com/fukalite/dj-design-system/blob/main/CONTRIBUTING.md) |
