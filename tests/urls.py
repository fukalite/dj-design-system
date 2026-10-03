from django.http import HttpResponse
from django.urls import include, path

from dj_design_system import urls


def _dummy_login_view(request):
    return HttpResponse("login")


auth_patterns = ([path("signin/", _dummy_login_view, name="signin")], "googleauth")

urlpatterns = [
    path("dds/", include(urls)),
    path("login/", _dummy_login_view, name="login"),
    path("auth/", include(auth_patterns, namespace="googleauth")),
]
