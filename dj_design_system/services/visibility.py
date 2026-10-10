"""Which apps and components the gallery shows.

This module is the single place gallery visibility is decided. Hidden apps
are left out of the navigation tree (and so the search index and node URLs),
the index page's component count and the REST API listing. Visibility only
affects the gallery: hidden components still render as template tags.
"""

from dj_design_system.data import ComponentInfo
from dj_design_system.services import component as component_service
from dj_design_system.services import registry as registry_service
from dj_design_system.settings import dds_settings


def get_hidden_apps() -> set[str]:
    """Return the app labels hidden from the gallery.

    That is ``GALLERY_EXCLUDE_APPS``, plus ``dj_design_system`` unless
    ``GALLERY_SHOW_DDS_COMPONENTS`` is true.
    """
    hidden = set(dds_settings.GALLERY_EXCLUDE_APPS or [])
    if not dds_settings.GALLERY_SHOW_DDS_COMPONENTS:
        hidden.add(component_service.BUILTIN_APP_LABEL)
    return hidden


def is_app_visible(*, app_label: str) -> bool:
    """Return True if the gallery shows the given app."""
    return app_label not in get_hidden_apps()


def get_gallery_components(
    *,
    registry: registry_service.ComponentRegistry = registry_service.component_registry,
) -> list[ComponentInfo]:
    """Return the registered components the gallery shows."""
    hidden = get_hidden_apps()
    return [info for info in registry.list_all() if info.app_label not in hidden]
