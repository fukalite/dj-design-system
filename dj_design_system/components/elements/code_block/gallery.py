"""Gallery configuration and variants for the built-in dds__code_block component."""

from dj_design_system.gallery import GalleryConfig, Variant


DJANGO_SNIPPET = """{% load design_components %}
{% dds__button "Save changes" variant="primary" icon="check" %}"""

PYTHON_SNIPPET = """from dj_design_system.components import TagComponent
from dj_design_system.parameters import StrParam


class Greeting(TagComponent):
    name = StrParam("Recipient name.", default="World")"""


config = GalleryConfig(
    group="Elements",
    param_defaults={
        "code": DJANGO_SNIPPET,
    },
    variants=[
        Variant(
            name="basic",
            label="Default Django Snippet",
            description="Code block with default language header label and copy trigger.",
            kwargs={
                "code": DJANGO_SNIPPET,
            },
        ),
        Variant(
            name="titled",
            label="With Filename Title",
            description="Python snippet displaying an explicit filename in the header.",
            kwargs={
                "code": PYTHON_SNIPPET,
                "language": "python",
                "title": "components/greeting.py",
            },
        ),
        Variant(
            name="non_copyable",
            label="Without Copy Button",
            description="Read-only code block with copy button hidden and header label visible.",
            kwargs={
                "code": DJANGO_SNIPPET,
                "language": "django",
                "title": "template.html",
                "copyable": False,
            },
        ),
        Variant(
            name="minimal",
            label="Headerless Minimal",
            description="Code block with empty language, no title, and copyable disabled.",
            kwargs={
                "code": "just test",
                "language": "",
                "title": "",
                "copyable": False,
            },
        ),
    ],
)
