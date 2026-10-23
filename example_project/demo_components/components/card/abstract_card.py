"""Abstract base card component for example_project.demo_components."""

from dj_design_system import components


class AbstractCardComponent(components.TagComponent):
    """Abstract base for all card components.

    Demonstrates ``Meta.abstract = True`` — this class is excluded from
    autodiscovery and will not appear in the gallery.
    """

    class Meta:
        abstract = True
