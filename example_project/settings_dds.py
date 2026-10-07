"""Settings module for viewing the internal dds component gallery in isolation."""

from example_project.settings import *  # noqa: F403


DJ_DESIGN_SYSTEM = {
    **DJ_DESIGN_SYSTEM,  # noqa: F405
    "DESIGN_SYSTEM_NAME": "dj-design-system (dds Internal Gallery)",
    "GALLERY_SHOW_DDS_COMPONENTS": True,
    "GALLERY_EXCLUDE_APPS": [
        "demo_components",
        "demo_extra",
        "demo_nav",
        "demo_single",
        "broken_components",
    ],
}
