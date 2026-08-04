import json
from unittest.mock import patch

import pytest
from django.test import RequestFactory

from dj_design_system.api.views import ComponentRenderView


pytestmark = pytest.mark.django_db


class TestComponentRenderView:
    def test_render_returns_200_ok_and_html(self, registry_with_demo_components):
        factory = RequestFactory()
        payload = {
            "name": "demo_components__alert",
            "positional_args": ["warning"],
            "params": {"content": "Warning message"},
        }
        request = factory.post(
            "/api/render/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        view = ComponentRenderView.as_view(registry=registry_with_demo_components)
        response = view(request)

        assert response.status_code == 200
        data = json.loads(response.content)

        assert "html" in data
        assert "Warning message" in data["html"]
        assert "alert-warning" in data["html"]
        assert "css" in data
        assert "js" in data
        assert "global_css" in data
        assert "global_js" in data
        assert "canvas_url" in data
        assert data["canvas_url"].startswith("http")

    def test_render_400_bad_request_invalid_json(self):
        factory = RequestFactory()
        request = factory.post(
            "/api/render/", data="not json", content_type="application/json"
        )
        view = ComponentRenderView.as_view()
        response = view(request)
        assert response.status_code == 400
        data = json.loads(response.content)
        assert "error" in data

    def test_render_400_bad_request_missing_component(self):
        factory = RequestFactory()
        payload = {"params": {}}
        request = factory.post(
            "/api/render/", data=json.dumps(payload), content_type="application/json"
        )
        view = ComponentRenderView.as_view()
        response = view(request)
        assert response.status_code == 400
        data = json.loads(response.content)
        assert "error" in data
        assert "name" in data["error"].lower()

    def test_render_404_not_found_invalid_component(
        self, registry_with_demo_components
    ):
        factory = RequestFactory()
        payload = {"name": "nonexistent_component", "params": {}}
        request = factory.post(
            "/api/render/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        view = ComponentRenderView.as_view(registry=registry_with_demo_components)
        response = view(request)

        assert response.status_code == 404
        data = json.loads(response.content)
        assert "error" in data

    def test_render_400_bad_request_invalid_method(self):
        factory = RequestFactory()
        request = factory.get("/api/render/")
        view = ComponentRenderView.as_view()
        response = view(request)
        assert response.status_code == 405

    def test_render_400_on_component_render_error(self, registry_with_demo_components):
        """Test that if the component itself fails to render (e.g. missing args), it returns 400."""
        with patch("dj_design_system.api.views.render_component") as mock_render:
            mock_render.side_effect = TypeError(
                "missing 1 required positional argument: 'content'"
            )

            factory = RequestFactory()
            payload = {"name": "demo_components__alert", "params": {}}
            request = factory.post(
                "/api/render/",
                data=json.dumps(payload),
                content_type="application/json",
            )
            view = ComponentRenderView.as_view(registry=registry_with_demo_components)
            response = view(request)

            assert response.status_code == 400
            data = json.loads(response.content)
            assert "error" in data
            assert (
                "Failed to render component: missing 1 required positional argument: 'content'. Please check your parameters."
                in data["error"]
            )
