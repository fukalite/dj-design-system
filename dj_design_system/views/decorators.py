"""Decorators for design system gallery views."""

from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse

from dj_design_system.settings import dds_settings


GALLERY_PERMISSION = "dj_design_system.can_view_gallery"


def gallery_access_required(view_func):
    """Allow access if the gallery is public, otherwise require the permission."""

    @wraps(view_func)
    def wrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if dds_settings.GALLERY_IS_PUBLIC:
            return view_func(request, *args, **kwargs)

        if not request.user.is_authenticated:
            # redirect_to_login resolves settings.LOGIN_URL (supporting paths,
            # named URL patterns, and namespaced patterns).
            return redirect_to_login(request.get_full_path())

        if not request.user.has_perm(GALLERY_PERMISSION):
            raise PermissionDenied

        return view_func(request, *args, **kwargs)

    return wrapper
