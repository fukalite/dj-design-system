"""Settings module for viewing the internal dds component gallery in isolation."""

from example_project.settings import *  # noqa: F401, F403


DJ_DESIGN_SYSTEM = {
    **DJ_DESIGN_SYSTEM,  # noqa: F405
    "DESIGN_SYSTEM_NAME": "dj-design-system (dds Built-in Gallery)",
    "GALLERY_INCLUDE_APPS": ["dj_design_system"],
}
