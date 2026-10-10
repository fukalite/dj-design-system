"""Gallery configuration and variants for the built-in dds__variant_view component."""

from dj_design_system import gallery


DEFAULT_DESCRIPTION_HTML = (
    "<p>Use the primary variant for the principal call-to-action on a surface.</p>"
)
DEFAULT_PREVIEW_URL = "/gallery/canvas/button/?variant=primary"
DEFAULT_CODE_SNIPPET = "{% dds__button 'Save changes' variant='primary' %}"

config = gallery.GalleryConfig(
    group="Domain",
    param_defaults={
        "variant_label": "Primary Action",
        "description_html": DEFAULT_DESCRIPTION_HTML,
        "preview_url": DEFAULT_PREVIEW_URL,
        "code": DEFAULT_CODE_SNIPPET,
    },
    variants=[
        gallery.Variant(
            name="basic",
            label="Full Variant View",
            description="Complete variant presentation with badge, heading, prose description, live preview stage, and usage code block.",
            kwargs={
                "variant_label": "Primary Action",
                "description_html": DEFAULT_DESCRIPTION_HTML,
                "preview_url": DEFAULT_PREVIEW_URL,
                "code": DEFAULT_CODE_SNIPPET,
            },
        ),
        gallery.Variant(
            name="code_only",
            label="Code-Only Variant View",
            description="Variant presentation without a preview iframe URL.",
            kwargs={
                "variant_label": "Destructive Action",
                "description_html": "<p>Use the danger variant for irreversible destructive operations.</p>",
                "code": "{% dds__button 'Delete account' variant='danger' %}",
                "badge_label": "Preset",
            },
        ),
        gallery.Variant(
            name="minimal",
            label="Minimal Heading Only",
            description="Minimal variant heading without optional description, preview, or code snippet.",
            kwargs={
                "variant_label": "Default State",
            },
        ),
    ],
)
