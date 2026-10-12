"""Gallery configuration and variants for the built-in dds__badge component."""

from dj_design_system import gallery


config = gallery.GalleryConfig(
    group="Elements",
    param_defaults={
        "label": "Optional",
        "variant": "neutral",
        "is_code": False,
    },
    variants=[
        gallery.Variant(
            name="basic",
            label="Neutral",
            description="Default neutral badge for general metadata and optional labels.",
            kwargs={"label": "Optional", "variant": "neutral"},
        ),
        gallery.Variant(
            name="info",
            label="Info",
            description="Informational badge for neutral status highlights.",
            kwargs={"label": "Beta", "variant": "info"},
        ),
        gallery.Variant(
            name="success",
            label="Success",
            description="Positive status badge for active or verified states.",
            kwargs={"label": "Active", "variant": "success"},
        ),
        gallery.Variant(
            name="warning",
            label="Warning",
            description="Caution badge for deprecated or attention-needed states.",
            kwargs={"label": "Deprecated", "variant": "warning"},
        ),
        gallery.Variant(
            name="error",
            label="Error",
            description="High-emphasis badge for required parameters or error states.",
            kwargs={"label": "Required", "variant": "error"},
        ),
        gallery.Variant(
            name="code",
            label="Code",
            description="Monospace badge for parameter types and technical identifiers.",
            kwargs={"label": "str", "is_code": True},
        ),
        gallery.Variant(
            name="maximal",
            label="Maximal",
            description="Status badge combined with technical monospace code formatting.",
            kwargs={"label": "DeprecatedType", "variant": "warning", "is_code": True},
        ),
    ],
)
