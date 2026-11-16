"""Admin sites that opt in to the design system's admin partials."""

from __future__ import annotations

from typing import Any

from django.contrib import admin


class DesignSystemAdminSiteMixin:
    """Mix into an ``AdminSite`` to render shared partials with components.

    Only sites with this mixin change. Any other site, including Django's
    default ``admin.site``, keeps the stock templates, so you can run both
    side by side and compare.
    """

    dds_enabled = True


class DesignSystemAdminSite(DesignSystemAdminSiteMixin, admin.AdminSite):
    """An ``AdminSite`` that renders shared partials with DjDS components.

    ::

        # urls.py
        from dj_design_system.contrib.django_admin.sites import DesignSystemAdminSite

        site = DesignSystemAdminSite(name="dds_admin")
        site.register(Book)

        urlpatterns = [path("admin/", site.urls)]
    """


def uses_design_system(site: Any) -> bool:
    """Return True if ``site`` opted in to the design system partials."""
    return bool(getattr(site, "dds_enabled", False))
