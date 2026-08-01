import pytest
from django.urls import resolve, reverse

from dj_design_system.api.views import ComponentRegistryView, ComponentRenderView

pytestmark = pytest.mark.django_db


class TestApiUrls:
    def test_registry_url_resolves(self):
        url = reverse("api-registry")
        match = resolve(url)
        assert match.func.view_class == ComponentRegistryView

    def test_render_url_resolves(self):
        url = reverse("api-render")
        match = resolve(url)
        assert match.func.view_class == ComponentRenderView
