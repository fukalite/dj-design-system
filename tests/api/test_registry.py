import json

import pytest
from django.test import RequestFactory

from dj_design_system.api.views import ComponentRegistryView


pytestmark = pytest.mark.django_db


class TestComponentRegistryView:
    def test_registry_returns_200_ok(self, registry_with_demo_components):
        factory = RequestFactory()
        request = factory.get("/api/registry/")
        view = ComponentRegistryView.as_view(registry=registry_with_demo_components)
        response = view(request)

        assert response.status_code == 200

        data = json.loads(response.content)
        # Check structure of the JSON payload
        assert isinstance(data, list)
        assert len(data) > 0

        # Verify the first item has the expected keys
        first_item = data[0]
        assert "name" in first_item
        assert "app_label" in first_item
        assert "relative_path" in first_item

    def test_custom_serializer_can_be_injected(self, registry_with_demo_components):
        """Test that consumers can subclass and provide their own serializer."""

        class CustomSerializer:
            def __init__(self, components):
                self.components = components

            def data(self):
                return [{"custom_key": c.name} for c in self.components]

        class CustomRegistryView(ComponentRegistryView):
            serializer_class = CustomSerializer

        factory = RequestFactory()
        request = factory.get("/api/registry/")
        view = CustomRegistryView.as_view(registry=registry_with_demo_components)
        response = view(request)

        assert response.status_code == 200

        data = json.loads(response.content)
        assert isinstance(data, list)
        assert len(data) > 0
        assert "custom_key" in data[0]
