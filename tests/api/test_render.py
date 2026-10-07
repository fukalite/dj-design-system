import json
from unittest.mock import patch

import pytest
from django.templatetags.static import static
from django.test import RequestFactory, override_settings

from dj_design_system.api.views import ComponentRenderView
from dj_design_system.data import ComponentMedia


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
        assert "Allow" in response
        assert "POST" in response["Allow"]

    def test_render_400_bad_request_params_not_dict(
        self, registry_with_demo_components
    ):
        factory = RequestFactory()
        payload = {"name": "demo_components__alert", "params": "not-a-dict"}
        request = factory.post(
            "/api/render/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        view = ComponentRenderView.as_view(registry=registry_with_demo_components)
        response = view(request)
        assert response.status_code == 400
        data = json.loads(response.content)
        assert "params" in data["errors"]

    def test_render_400_bad_request_positional_args_not_list(
        self, registry_with_demo_components
    ):
        factory = RequestFactory()
        payload = {"name": "demo_components__alert", "positional_args": "not-a-list"}
        request = factory.post(
            "/api/render/",
            data=json.dumps(payload),
            content_type="application/json",
        )
        view = ComponentRenderView.as_view(registry=registry_with_demo_components)
        response = view(request)
        assert response.status_code == 400
        data = json.loads(response.content)
        assert "positional_args" in data["errors"]

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
                "Failed to render component. Please check your parameters and template syntax."
                in data["error"]
            )

    def test_render_external_asset_urls(self, registry_with_demo_components):
        """External asset URLs are returned as-is; local paths become absolute (#166)."""
        media = ComponentMedia(
            css=["https://cdn.example.com/component.css", "myapp/component.css"],
            js=["//cdn.example.com/component.js"],
        )
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
        with (
            override_settings(
                DJ_DESIGN_SYSTEM={
                    "GLOBAL_CSS": ["https://fonts.googleapis.com/css2?family=Inter"],
                    "GLOBAL_JS": ["HTTPS://cdn.example.com/vendor.js"],
                }
            ),
            patch("dj_design_system.api.views.get_component_media", return_value=media),
        ):
            response = view(request)

        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["css"] == [
            "https://cdn.example.com/component.css",
            f"http://testserver{static('myapp/component.css')}",
        ]
        # Protocol-relative URLs take the request's scheme.
        assert data["js"] == ["http://cdn.example.com/component.js"]
        assert data["global_css"] == ["https://fonts.googleapis.com/css2?family=Inter"]
        assert data["global_js"] == ["HTTPS://cdn.example.com/vendor.js"]
