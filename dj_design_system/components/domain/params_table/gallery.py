"""Gallery configuration and variants for the built-in dds__params_table component."""

from dj_design_system import gallery


SAMPLE_PARAMS: tuple[dict[str, object], ...] = (
    {
        "name": "label",
        "type_name": "str",
        "required": True,
        "default": None,
        "choices": [],
        "description": "Primary visible text label for the component.",
    },
    {
        "name": "variant",
        "type_name": "str",
        "required": False,
        "default": "primary",
        "choices": ["primary", "secondary", "ghost", "danger"],
        "description": "Visual treatment applied to the control.",
    },
    {
        "name": "disabled",
        "type_name": "bool",
        "required": False,
        "default": False,
        "choices": [True, False],
        "description": "Whether user interaction is disabled.",
    },
)

SAMPLE_SLOTS: tuple[dict[str, object], ...] = (
    {
        "name": "head",
        "required": False,
        "default": "",
        "description": "Optional header rows (<tr> with <th> cells).",
    },
    {
        "name": "body",
        "required": True,
        "default": "",
        "description": "Primary body rows (<tr> with <td> cells).",
    },
)

config = gallery.GalleryConfig(
    group="Domain",
    param_defaults={
        "params": list(SAMPLE_PARAMS),
        "title": "Parameters",
    },
    variants=[
        gallery.Variant(
            name="basic",
            label="Component Parameters",
            description="Parameters table displaying required, optional, default, and choice metadata.",
            kwargs={
                "params": list(SAMPLE_PARAMS),
                "title": "Parameters",
            },
        ),
        gallery.Variant(
            name="with_slots",
            label="Parameters and Slots",
            description="Parameters table accompanied by a secondary named slots table.",
            kwargs={
                "params": list(SAMPLE_PARAMS),
                "slots_list": list(SAMPLE_SLOTS),
                "title": "Parameters",
            },
        ),
        gallery.Variant(
            name="empty",
            label="Empty Parameters State",
            description="Fallback message displayed when a component defines no parameters.",
            kwargs={
                "params": [],
                "title": "Parameters",
                "empty_message": "This component has no parameters.",
            },
        ),
    ],
)
