"""Gallery configuration and variants for the built-in dds__badge component."""

from dj_design_system.gallery import GalleryConfig, Variant


config = GalleryConfig(
    group="Elements",
    variants=[
        Variant(
            name="basic",
            label="Neutral",
            description="Default neutral badge for general metadata and optional labels.",
            kwargs={"label": "Optional", "variant": "neutral"},
        ),
        Variant(
            name="info",
            label="Info",
            description="Informational badge for neutral status highlights.",
            kwargs={"label": "Beta", "variant": "info"},
        ),
        Variant(
            name="success",
            label="Success",
            description="Positive status badge for active or verified states.",
            kwargs={"label": "Active", "variant": "success"},
        ),
        Variant(
            name="warning",
            label="Warning",
            description="Caution badge for deprecated or attention-needed states.",
            kwargs={"label": "Deprecated", "variant": "warning"},
        ),
        Variant(
            name="error",
            label="Error",
            description="High-emphasis badge for required parameters or error states.",
            kwargs={"label": "Required", "variant": "error"},
        ),
        Variant(
            name="code",
            label="Code",
            description="Monospace badge for parameter types and technical identifiers.",
            kwargs={"label": "str", "variant": "code"},
        ),
        Variant(
            name="maximal",
            label="Maximal",
            description="Badge with explicit semantic variant.",
            kwargs={"label": "Required", "variant": "error"},
        ),
    ],
)
