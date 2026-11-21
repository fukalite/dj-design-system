"""Settings module for viewing the internal dds component gallery in isolation."""

from example_project.settings import *  # noqa: F401, F403


DJ_DESIGN_SYSTEM = DJ_DESIGN_SYSTEM.replace(  # noqa: F405
    name="dj-design-system (dds Built-in Gallery)",
    gallery=DJ_DESIGN_SYSTEM.gallery.replace(  # noqa: F405
        include_apps=("dj_design_system",),
    ),
)
