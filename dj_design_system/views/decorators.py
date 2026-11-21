"""Decorators for design system gallery views."""

from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpRequest, HttpResponse

from dj_design_system.services import config as config_service


GALLERY_PERMISSION = "dj_design_system.can_view_gallery"


def gallery_access_required(view_func):
    """Enforce gallery enabled state and public/permission access rules."""

    @wraps(view_func)
    def wrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        gallery = config_service.get_gallery_settings()
        if not gallery.enabled:
            raise Http404("Gallery is disabled.")

        if gallery.is_public:
            return view_func(request, *args, **kwargs)

        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        if not request.user.has_perm(GALLERY_PERMISSION):
            raise PermissionDenied

        return view_func(request, *args, **kwargs)

    return wrapper
