"""Gallery configuration for the built-in dds__tooltip component."""

from django.utils.safestring import mark_safe

from dj_design_system import gallery


TRIGGER_BUTTON_HTML = mark_safe(
    '<button type="button" class="dds-button" data-variant="neutral" data-size="sm">'
    "<span>Trigger button</span></button>"
)

config = gallery.GalleryConfig(
    group="Elements",
    param_defaults={
        "text": "Helpful contextual hint",
        "placement": "top",
        "align": "center",
        "content": TRIGGER_BUTTON_HTML,
    },
)
