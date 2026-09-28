"""Decorators for design system gallery views."""

from functools import wraps

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme

from dj_design_system.settings import dds_settings


GALLERY_PERMISSION = "dj_design_system.can_view_gallery"


def gallery_access_required(view_func):
    """Allow access if the gallery is public, otherwise require the permission."""

    @wraps(view_func)
    def wrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if dds_settings.GALLERY_IS_PUBLIC:
            return view_func(request, *args, **kwargs)

        if not request.user.is_authenticated:
            url = f"{settings.LOGIN_URL}?next={request.path}"
            if not url_has_allowed_host_and_scheme(url, allowed_hosts=None):
                url = "/"
            return redirect(url)

        if not request.user.has_perm(GALLERY_PERMISSION):
            raise PermissionDenied

        return view_func(request, *args, **kwargs)

    return wrapper
