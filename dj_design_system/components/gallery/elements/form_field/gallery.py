"""Gallery configuration and variants for the built-in dds__form_field component."""

from dj_design_system import gallery


DEFAULT_CONTROL_HTML = '<input id="dds-email" type="email" value="ada@example.com">'
SELECT_CONTROL_HTML = (
    '<select id="dds-role">'
    '<option value="admin">Administrator</option>'
    '<option value="editor">Editor</option>'
    "</select>"
)
CHECKBOX_CONTROL_HTML = '<input id="dds-opt-in" type="checkbox" checked>'

config = gallery.GalleryConfig(
    param_defaults={
        "label": "Email address",
        "field_id": "dds-email",
        "content": DEFAULT_CONTROL_HTML,
    },
    variants=[
        gallery.Variant(
            name="basic",
            label="Stacked Input Field",
            description="Default stacked form field with a label and text input control.",
            kwargs={
                "label": "Email address",
                "field_id": "dds-email",
                "content": DEFAULT_CONTROL_HTML,
            },
        ),
        gallery.Variant(
            name="inline",
            label="Inline Field",
            description="Horizontal cluster layout pairing label and control side by side.",
            kwargs={
                "label": "Enable notifications",
                "field_id": "dds-opt-in",
                "description": "Receive weekly digest summaries.",
                "layout": "inline",
                "content": CHECKBOX_CONTROL_HTML,
            },
        ),
    ],
)
