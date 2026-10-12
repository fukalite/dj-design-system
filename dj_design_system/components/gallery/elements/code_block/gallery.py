"""Gallery configuration and variants for the built-in dds__code_block component."""

from dj_design_system import gallery


DJANGO_SNIPPET = """{% load design_components %}
{% dds__button "Save changes" variant="primary" icon="check" %}"""

PYTHON_SNIPPET = """from dj_design_system import components, parameters


class Greeting(components.TagComponent):
    name = parameters.StrParam("Recipient name.", default="World")"""


config = gallery.GalleryConfig(
    group="Elements",
    param_defaults={
        "code": DJANGO_SNIPPET,
    },
    variants=[
        gallery.Variant(
            name="basic",
            label="Default Code Block",
            description="Code block with filename header, language badge, and copy button.",
            kwargs={
                "code": PYTHON_SNIPPET,
                "language": "python",
                "title": "components/greeting.py",
                "copyable": True,
            },
        ),
        gallery.Variant(
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
