"""Gallery configuration and variants for the built-in dds__sandbox_params component."""

from django.utils import safestring

from dj_design_system import gallery


SAMPLE_PARAM_ROWS: tuple[dict[str, object], ...] = (
    {
        "name": "label",
        "field_id": "id_label",
        "spec": {
            "description": "Primary text displayed inside the button.",
            "required": True,
        },
        "field": safestring.SafeString(
            '<input type="text" id="id_label" name="label" value="Save changes">'
        ),
    },
    {
        "name": "variant",
        "field_id": "id_variant",
        "spec": {
            "description": "Visual style variant applied to the control.",
            "required": False,
        },
        "field": safestring.SafeString(
            '<select id="id_variant" name="variant">'
            '<option value="primary" selected>primary</option>'
            '<option value="secondary">secondary</option>'
            '<option value="ghost">ghost</option>'
            "</select>"
        ),
    },
)

config = gallery.GalleryConfig(
    group="Composites",
    param_defaults={
        "param_rows": list(SAMPLE_PARAM_ROWS),
        "action_url": "/design-system/components/button/",
    },
)
