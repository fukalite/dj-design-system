# Quick Start

Full documentation lives at [fukalite.github.io/dj-design-system/](https://fukalite.github.io/dj-design-system/).

`dj-design-system` requires no configuration to get started: `DjangoDesignSystemConfig.ready()` automatically registers `ComponentsTemplateLoader` and `ComponentsStaticFinder` when you use Django's default `TEMPLATES` and `STATICFILES_FINDERS`. (If you declare custom loaders or static finders explicitly, see [Manual Template Loader & Static Finder Setup](configuration.md#manual-template-loader-static-finder-setup).)

## 1. Add `dj_design_system` to `INSTALLED_APPS`

```python
# settings.py
INSTALLED_APPS = [
    ...
    "dj_design_system",
    ...
]
```

## 2. Mount the Gallery URLs

Include the gallery URLs in your project's `urls.py`:

```python
# urls.py
from django.urls import include, path

urlpatterns = [
    path("design-system/", include("dj_design_system.urls")),
]
```

By default the gallery is public; to restrict access to users with the `dj_design_system.can_view_gallery` permission or disable it in production, configure `DJ_DESIGN_SYSTEM = DesignSystemSettings(...)` as described in [Configuration](configuration.md).

## 3. Create Your First Component

### Tag Component (co-located HTML template)

Place a `.py` file and matching `.html` file inside any installed app's `components/` directory:

```text
myapp/components/
    __init__.py
    badge.py
    badge.html
```

```python
# myapp/components/badge.py
from dj_design_system.components import TagComponent
from dj_design_system.parameters import BoolCSSClassParam, StrParam


class BadgeComponent(TagComponent):
    """A status badge."""

    label = StrParam("The badge text.")
    bold = BoolCSSClassParam(required=False, default=False)

    class Meta:
        positional_args = ["label"]
```

```htmldjango
{# myapp/components/badge.html #}
<span class="badge {{ classes }}">{{ label }}</span>
```

For tiny fragments you can omit the `.html` file and set `template_format_str = "<span class='badge {classes}'>{label}</span>"` on the class instead.

Render it in any Django template:

```htmldjango
{% load design_components %}
{% badge "New" %}
{% badge "Active" bold=True %}
```

### Block Component

Block components wrap nested template content, exposed automatically as `content`:

```python
# myapp/components/card.py
from dj_design_system.components import BlockComponent
from dj_design_system.parameters import StrParam


class CardComponent(BlockComponent):
    """A content card."""

    title = StrParam("Card heading.")

    class Meta:
        positional_args = ["title"]
```

```htmldjango
{# myapp/components/card.html #}
<div class="card {{ classes }}">
  <h3>{{ title }}</h3>
  {{ content }}
</div>
```

```htmldjango
{% load design_components %}
{% card "My Title" %}
  <p>This is the card body.</p>
{% endcard %}
```

## Customising Gallery Previews & Variants

The gallery synthesises minimal and maximal examples automatically. Add a side-car `gallery.py` (or `<component_name>_gallery.py`) next to your component to declare custom metadata and variants:

```python
# myapp/components/card_gallery.py
from dj_design_system.gallery import GalleryConfig, Variant

config = GalleryConfig(
    icon="ph:cards",
    order=1,
    variants=[
        Variant(name="basic", kwargs={"title": "Simple Card"}),
        Variant(
            name="featured",
            label="Featured Card",
            description="Card highlighted with custom gradient styling.",
            kwargs={"title": "Featured Story", "content": "Exclusive report."},
            show_in_nav=True,
        ),
    ],
)
```

See the [Gallery Guide](gallery.md) and [Gallery Side-Car Config API](api/gallery.md) for all options.

## Loading Template Tags

Load all discovered components across every app with the central library:

```htmldjango
{% load design_components %}
```

Or expose a per-app library by creating `myapp/templatetags/components.py`:

```python
from django import template
from dj_design_system import component_registry

register = template.Library()
component_registry.register_templatetags(register, app_label="myapp")
```

And load it in templates with `{% load components %}`.

## Component Discovery Rules

`DjangoDesignSystemConfig.ready()` discovers components automatically at startup:

- Inspects `{app}.components` (single module) or `{app}/components/` (package) for every installed app.
- Recursively walks sub-packages that contain an `__init__.py`.
- Registers concrete `TagComponent` and `BlockComponent` subclasses defined in each module.
- Skips classes with `Meta.abstract = True` and classes imported from other modules.
- Watches co-located templates with Django's autoreloader during development (adding a brand-new co-located `.html` file requires a restart).

Next: configure global assets, themes, and per-app defaults in [Configuration](configuration.md).
