"""Gallery configuration and variants for the built-in dds__usage_example component."""

from dj_design_system import gallery


MINIMAL_CODE_SNIPPET = '{% dds__button "Save changes" %}'
MAXIMAL_CODE_SNIPPET = (
    "{% dds__button\n"
    '  "Save changes"\n'
    '  variant="primary"\n'
    '  size="md"\n'
    '  icon="check"\n'
    "%}"
)
DEFAULT_PREVIEW_URL = "/gallery/canvas/?component=dds__button"

config = gallery.GalleryConfig(
    group="Domain",
    param_defaults={
        "title": "Minimal example",
        "code": MINIMAL_CODE_SNIPPET,
    },
    variants=[
        gallery.Variant(
            name="basic",
            label="Minimal Usage Example",
            description="Usage example displaying a heading, stage preview iframe with sandbox button, and code block.",
            kwargs={
                "title": "Minimal example",
                "code": MINIMAL_CODE_SNIPPET,
                "preview_url": DEFAULT_PREVIEW_URL,
                "canvas_id": "minimal",
            },
        ),
        gallery.Variant(
            name="maximal",
            label="Maximal Usage Example",
            description="Multi-line template tag example with custom canvas identifier and sandbox anchor.",
            kwargs={
                "title": "Maximal example",
                "code": MAXIMAL_CODE_SNIPPET,
                "preview_url": DEFAULT_PREVIEW_URL,
                "canvas_id": "maximal",
                "sandbox_href": "#pane-sandbox",
            },
        ),
        gallery.Variant(
            name="code_only",
            label="Code-Only Example",
            description="Usage example rendering only the heading and template tag snippet without an iframe preview.",
            kwargs={
                "title": "Template snippet",
                "code": MINIMAL_CODE_SNIPPET,
                "preview_url": "",
            },
        ),
    ],
)
