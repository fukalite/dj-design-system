"""Gallery configuration and variants for the built-in dds__canvas_widget component."""

from dj_design_system import gallery


SAMPLE_SOURCE_CODE = "{% dds__button 'Save changes' variant='primary' %}"
SAMPLE_RENDERED_HTML = (
    '<button type="button" class="dds-button" '
    'data-variant="primary">Save changes</button>'
)
SAMPLE_SRCDOC = (
    "<!doctype html><html><head><meta charset='utf-8'></head>"
    "<body><button type='button'>Save changes</button></body></html>"
)


config = gallery.GalleryConfig(
    group="Domain",
    param_defaults={
        "canvas_id": "gallery-canvas",
        "iframe_srcdoc": SAMPLE_SRCDOC,
        "source_code": SAMPLE_SOURCE_CODE,
        "rendered_html": SAMPLE_RENDERED_HTML,
        "mode": "preview",
        "viewport": "responsive",
        "background": "white",
        "zoom": "100",
    },
    variants=[
        gallery.Variant(
            name="basic",
            label="Default Preview Canvas",
            description=(
                "Standard canvas widget in preview mode with template source "
                "and rendered HTML mode toggles."
            ),
            kwargs={
                "canvas_id": "basic-canvas",
                "iframe_srcdoc": SAMPLE_SRCDOC,
                "source_code": SAMPLE_SOURCE_CODE,
                "rendered_html": SAMPLE_RENDERED_HTML,
                "mode": "preview",
                "viewport": "responsive",
                "background": "white",
                "zoom": "100",
            },
        ),
        gallery.Variant(
            name="code_mode",
            label="Template Source Mode",
            description=(
                "Canvas widget opened directly to the template source code "
                "drawer."
            ),
            kwargs={
                "canvas_id": "code-canvas",
                "iframe_srcdoc": SAMPLE_SRCDOC,
                "source_code": SAMPLE_SOURCE_CODE,
                "rendered_html": SAMPLE_RENDERED_HTML,
                "mode": "code",
            },
        ),
        gallery.Variant(
            name="dark_tablet_stage",
            label="Dark Stage & Tablet Viewport",
            description=(
                "Canvas widget configured with a dark stage background, 768px "
                "tablet viewport preset, and 125% zoom."
            ),
            kwargs={
                "canvas_id": "tablet-canvas",
                "iframe_srcdoc": SAMPLE_SRCDOC,
                "source_code": SAMPLE_SOURCE_CODE,
                "rendered_html": SAMPLE_RENDERED_HTML,
                "mode": "preview",
                "viewport": "768",
                "background": "dark",
                "zoom": "125",
            },
        ),
    ],
)
