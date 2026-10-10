"""Gallery configuration and variants for the built-in dds__params_form component."""

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

ERROR_PARAM_ROWS: tuple[dict[str, object], ...] = (
    {
        "name": "payload",
        "field_id": "id_payload",
        "spec": {
            "description": "Structured JSON payload passed to the component.",
            "required": True,
        },
        "field": safestring.SafeString(
            '<textarea id="id_payload" name="payload" rows="3">{invalid}</textarea>'
        ),
        "errors": ["Enter a valid JSON or Python literal."],
    },
)

config = gallery.GalleryConfig(
    group="Domain",
    param_defaults={
        "param_rows": list(SAMPLE_PARAM_ROWS),
        "action_url": "/design-system/components/button/",
        "active_theme": "light",
        "active_variant": "primary",
    },
    variants=[
        gallery.Variant(
            name="basic",
            label="Configurable Parameters Form",
            description="Live sandbox parameters form with text and select controls.",
            kwargs={
                "param_rows": list(SAMPLE_PARAM_ROWS),
                "action_url": "/design-system/components/button/",
                "active_theme": "light",
                "active_variant": "primary",
            },
        ),
        gallery.Variant(
            name="with_errors",
            label="Parameters Form with Validation Errors",
            description="Sandbox parameters form displaying field-level validation error alerts.",
            kwargs={
                "param_rows": list(ERROR_PARAM_ROWS),
                "action_url": "/design-system/components/button/",
                "active_theme": "dark",
            },
        ),
        gallery.Variant(
            name="empty",
            label="Empty Parameters State",
            description="Fallback message displayed when a component has no editable parameters.",
            kwargs={
                "param_rows": [],
                "empty_message": "This component has no configurable parameters.",
            },
        ),
    ],
)
