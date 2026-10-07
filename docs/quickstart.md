# Quickstart

Full documentation lives at [fukalite.github.io/dj-design-system/](https://fukalite.github.io/dj-design-system/).

## 1. Configure settings.py

All setup for Django Design System starts in your `settings.py`.

### INSTALLED_APPS

Add `dj_design_system` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    "dj_design_system",
    ...
]
```

### STATICFILES_FINDERS

To serve co-located `.css` and `.js` files through Django's static files system, add `ComponentsStaticFinder` to `STATICFILES_FINDERS`:

```python
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "dj_design_system.finders.ComponentsStaticFinder",
]
```

This serves `.css` and `.js` files from each installed app's `components/` directory under the URL namespace `{app_label}/components/...`. Python files, HTML templates, and all other file types are never exposed as static assets.

### TEMPLATES

To use co-located `.html` templates for components, add `ComponentsTemplateLoader` to your `TEMPLATES` loader list. Because Django does not support mixing `APP_DIRS: True` with a custom `loaders` list, you must switch to an explicit loader configuration — wrapped in `django.template.loaders.cached.Loader` so Django keeps compiled templates in memory just as the default configuration does:

```python
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": False,  # must be False when loaders is set
        "OPTIONS": {
            "loaders": [
                (
                    "django.template.loaders.cached.Loader",
                    [
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                        "dj_design_system.loaders.ComponentsTemplateLoader",
                    ],
                ),
            ],
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
```

When running the development server, edits to existing component templates are picked up without a restart: `ComponentsTemplateLoader` reports each app's `components/` directory to Django's autoreloader, which clears the template cache when a file there changes.

Component auto-discovery happens automatically when Django starts up (via `AppConfig.ready()`). Templates are matched to components at that point, so **adding** a new co-located `.html` file to an existing component needs a server restart before the component uses it.

### DJ_DESIGN_SYSTEM Configuration

Configure the design system by adding a `DJ_DESIGN_SYSTEM` dictionary. This is where you configure the gallery, global assets, themes, and more.
A full list of settings is available in the [Settings API Reference](api/settings.md).

```python
DJ_DESIGN_SYSTEM = {
    # The name displayed in the gallery navbar and page titles
    "DESIGN_SYSTEM_NAME": "Django Design System",
    # Enable the gallery UI
    "ENABLE_GALLERY": True,
    # If False, requires staff permissions (is_staff=True) to view the gallery
    "GALLERY_IS_PUBLIC": False,
    # Global styles and scripts loaded in the gallery canvas and when using tags
    "GLOBAL_CSS": [],
    "GLOBAL_JS": [],
}
```

## 2. Configure urls.py

Include the gallery URLs in your project's main `urls.py` to make the gallery UI accessible. In production you might want to restrict this to an admin-only URL.

```python
from django.urls import include, path

urlpatterns = [
    path("design-system/", include("dj_design_system.urls")),
]
```

## Creating a Tag Component

Tag components render a single HTML fragment. Create a file in your app's `components/` directory.

### Using a co-located HTML template (recommended)

Place a `.html` file next to the `.py` file with the same base name. Django's full template language is available — `{% if %}`, `{% for %}`, `{% load %}`, etc.:

```
myapp/components/
    badge.py
    badge.html
```

```python
# myapp/components/badge.py
from dj_design_system.components import TagComponent
from dj_design_system.parameters import StrParam, BoolCSSClassParam


class BadgeComponent(TagComponent):
    """A status badge."""

    label = StrParam("The badge text.")
    bold = BoolCSSClassParam(required=False, default=False)
```

```htmldjango
{# myapp/components/badge.html #}
<span class="badge {{ classes }}">{{ label }}</span>
```

### Using an inline format string

For simple components you can skip the HTML file and use `template_format_str` directly on the class. This uses Python's `format_html` rather than the Django template engine, so template tags are not available:

```python
class BadgeComponent(TagComponent):
    """A status badge."""

    template_format_str = "<span class='badge {classes}'>{label}</span>"
    label = StrParam("The badge text.")
    bold = BoolCSSClassParam(required=False, default=False)
```

Use it in a template:

```htmldjango
{% load design_components %}
{% badge label="New" %}
{% badge label="Active" bold=True %}
```

### Positional Arguments

Declare `Meta.positional_args` to allow positional syntax in the template tag:

```python
class BadgeComponent(TagComponent):
    label = StrParam("The badge text.")

    class Meta:
        positional_args = ["label"]
```

Now you can write:

```html
{% badge "New" %}
```

Instead of:

```html
{% badge label="New" %}
```

## Creating a Block Component

Block components wrap nested template content. The block body is automatically available as `content` in the template context — you do NOT need to declare it as a parameter.

```
myapp/components/
    card.py
    card.html
```

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

Use it in a template:

```htmldjango
{% load design_components %}
{% card "My Title" %}
  <p>This is the card body.</p>
{% endcard %}
```

## Configuring Gallery Previews & Variants

By default, the gallery synthesizes minimal and maximal examples automatically. To provide custom metadata, named variants, themes, and canvas layouts, create a `gallery.py` (or `<component_name>_gallery.py`) file in the same directory as your component:

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

The gallery will automatically discover `config`, display your custom variants in the navigation sidebar, and provide deep links (`?variant=featured`) with dedicated variant documentation. For complete configuration options, see the [Gallery Guide](gallery.md) and [Gallery API Reference](api/gallery.md).

## Loading Template Tags

There are two ways to load component template tags:

### Central library (all components from all apps)

```html
{% load design_components %}
```

### Per-app library

Create a `templatetags/components.py` in your app:

```python
from django import template
from dj_design_system import component_registry

register = template.Library()
component_registry.register_templatetags(register, app_label="myapp")
```

Then in templates:

```html
{% load design_components %}
```

## Component Discovery

Components are automatically discovered in any installed app that has a `components` module or package. The discovery rules are:

- Looks for `{app}.components` (a single file) or `{app}/components/` (a package)
- Recursively walks sub-packages within `components/`
- Registers any concrete `BaseComponent` subclass (via `TagComponent` or `BlockComponent`)
- Skips classes with `class Meta: abstract = True`
- Skips classes imported from other modules (only registers classes defined in that file)
