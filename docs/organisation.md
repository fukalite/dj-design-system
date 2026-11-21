# Organising Apps & Folders

Django Design System places very few constraints on how you structure your component library. Discovery follows Python's own module system: components live inside an app's `components` module (a single file or a package), and sub-packages must contain an `__init__.py` to be traversed.

---

## Start as simple as you can

The simplest valid setup is a single file:

```text
myapp/
    components.py   # all your components live here
```

The [`demo_single`](https://github.com/fukalite/dj-design-system/tree/main/example_project/demo_single) app in the example project defines both `PillComponent` and `ChipComponent` in one `components.py`. Both appear automatically under `demo_single` in the gallery.

---

## Grow into folders naturally

When a single file becomes unwieldy, split into a package. Each sub-package becomes a folder in the gallery navigation automatically:

```text
myapp/
    components/
        __init__.py
        button.py          -> gallery: myapp / Button
        badge.py           -> gallery: myapp / Badge
        card/
            __init__.py
            info_card.py   -> gallery: myapp / Card / Info card
            hero_card.py   -> gallery: myapp / Card / Hero card
```

---

## Leaf-folder collapsing

When the deepest folder name matches the component name inside it, the folder collapses so the component appears directly under its parent rather than inside a redundant nested node:

```text
components/
    icon/
        __init__.py
        icon.py   # defines IconComponent -> gallery: Icon (not Icon -> Icon)
```

This keeps co-located templates, styles, scripts, and `gallery.py` files tidy without deepening navigation.

---

## Abstract bases share structure without cluttering the gallery

Declare `Meta.abstract = True` on shared base classes to exclude them from discovery:

```python
class AbstractCardComponent(TagComponent):
    """Abstract base for all card components."""

    class Meta:
        abstract = True
```

Concrete subclasses inherit parameters and behaviour normally while the abstract base stays hidden.

---

## Multi-app libraries & tag prefixes

Every installed Django app is treated equally. When two apps define a component with the same short name (`button`), disambiguate in templates using the double-underscore qualified syntax:

```htmldjango
{% load design_components %}
{% demo_components__button "Primary action" %}
{% demo_extra__button "Secondary action" %}
```

### App-level defaults (`AppConfig.design_system`)

Each app can declare its own tag prefix, flattening strategy, folder rules, gallery labels, and navigation order on its `AppConfig` subclass using `AppSettings` and `DirectorySettings`:

```python
# myapp/apps.py
from django.apps import AppConfig
from dj_design_system.config import (
    AppSettings,
    DirectorySettings,
    FlattenStrategy,
    NodeType,
)


class MyAppConfig(AppConfig):
    name = "myapp"
    verbose_name = "My Design System"
    design_system = AppSettings(
        prefix="ui",
        flatten=FlattenStrategy.LEAF,
        nav_order=("overview", NodeType.FOLDER, NodeType.COMPONENT, NodeType.DOCUMENT),
        directories={
            "card": DirectorySettings(
                prefix="cards",
                flatten=FlattenStrategy.NONE,
                label="Cards",
                order=1,
            ),
            "foundations": DirectorySettings(
                promote_to_app=True,
                label="Foundations",
                order=0,
            ),
        },
    )
```

- **`prefix` & `flatten`**: control qualified tag names (e.g. `FlattenStrategy.NONE` preserves subfolders, `FlattenStrategy.LEAF` strips a matching leaf folder, `FlattenStrategy.ALL` flattens all subfolders under the prefix).
- **`short_names=False`**: registers only qualified tags (recommended for reusable and contrib apps so they never shadow host project short tags).
- **`promote_to_app=True`**: elevates a subfolder to a top-level section in the gallery sidebar. A `DirectorySettings` with `prefix=None` and `flatten=None` is presentation-only and inherits its parent directory or app prefix.
- **`nav_order` & `order`**: control sorting within the app or a specific folder.

Host projects can override any app setting in `DJ_DESIGN_SYSTEM = DesignSystemSettings(apps={"myapp": AppSettings(...)})`. See [Configuration](configuration.md) for the full 4-tier precedence stack.

---

## Markdown documentation lives with the code

Place `.md` files anywhere inside `components/`:

- `index.md` — attaches to its parent folder or component as its documentation page.
- Any other `.md` file — appears as a standalone document node in the navigation tree.

```text
demo_nav/components/
    design_guidelines.md      # standalone doc at app root
    elements/
        index.md              # attached to Elements folder
        icon/
            accessibility.md  # standalone doc inside icon folder
```

---

## Co-locate CSS, JS, and HTML templates

Place `.css`, `.js`, and `.html` files next to the component module using the same base name:

```text
myapp/components/button/
    __init__.py
    button.py      # defines ButtonComponent
    button.html    # full Django template
    button.css     # served via ComponentsStaticFinder
    button.js      # served via ComponentsStaticFinder
```

Declare extra non-co-located assets via a standard Django inner `Media` class; both sources are merged automatically. See [Components: Templates](components.md#templates) for template precedence details.

---

## Summary

| Pattern | When to use |
| --- | --- |
| Single `components.py` | Small apps, prototyping, simple component sets |
| Flat `components/` package | Medium libraries with no sub-grouping needed |
| Nested sub-packages | Large libraries grouped by domain (forms, navigation, cards…) |
| `AppConfig.design_system` | App-owned prefixes, flattening, labels, `nav_order`, and assets |
| `DirectorySettings(promote_to_app=True)` | Elevating key sections (such as Foundations) to the sidebar root |
| Abstract base classes | Shared parameters and templates across related components |
| Co-located `.html` / `.css` / `.js` | Self-contained components with zero external wiring |
| Markdown files in `components/` | Narrative docs, guidelines, and live `canvas` demos |
