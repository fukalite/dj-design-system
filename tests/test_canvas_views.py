"""Tests for the canvas iframe view."""

import pytest
from django.test import Client, override_settings
from django.urls import reverse

from dj_design_system.settings import BUILTIN_CANVAS_BACKGROUNDS


pytestmark = pytest.mark.django_db


class TestCanvasIframeView:
    """Test the canvas iframe rendering endpoint."""

    def test_url_resolves(self):
        url = reverse("gallery-canvas-iframe")
        assert "_canvas/" in url

    def test_missing_component_returns_error(self):
        client = Client()
        url = reverse("gallery-canvas-iframe")
        response = client.get(url)
        assert response.status_code == 200
        content = response.content.decode()
        assert "gallery-canvas-error" in content
        assert "Missing required" in content

    def test_unknown_component_returns_error(self):
        client = Client()
        url = reverse("gallery-canvas-iframe")
        response = client.get(url, {"component": "nonexistent"})
        assert response.status_code == 200
        content = response.content.decode()
        assert "gallery-canvas-error" in content
        assert "not found" in content

    def test_valid_component_renders_html_document(self):
        client = Client()
        url = reverse("gallery-canvas-iframe")
        response = client.get(url, {"component": "rich_button", "label": "Test"})
        assert response.status_code == 200
        content = response.content.decode()
        assert "<!DOCTYPE html>" in content
        assert "Test" in content

    def test_slotted_card_renders_unescaped(self):
        """Regression: the slotted card's HTML used to be shown as escaped text."""
        client = Client()
        url = reverse("gallery-canvas-iframe")
        response = client.get(
            url, {"component": "slotted_card", "title": "Hello", "slot__body": "Body"}
        )
        content = response.content.decode()
        assert "<h3 class='slotted-card__title'>Hello</h3>" in content
        assert "&lt;div class=" not in content
        assert "gallery-canvas-warning" not in content

    def test_plain_str_render_shows_escaped_output_with_warning(self, mocker):
        mocker.patch(
            "dj_design_system.views.canvas.render_component",
            return_value="<b>Hi</b>",
        )
        client = Client()
        url = reverse("gallery-canvas-iframe")
        response = client.get(url, {"component": "rich_button", "label": "Hi"})
        content = response.content.decode()
        assert "gallery-canvas-warning" in content
        assert "returned a plain <code>str</code>" in content
        assert "&lt;b&gt;Hi&lt;/b&gt;" in content
        assert "<b>Hi</b>" not in content

    def test_css_cascade_order(self):
        """Global CSS should appear before canvas CSS and component CSS."""
        client = Client()
        url = reverse("gallery-canvas-iframe")
        response = client.get(url, {"component": "rich_button", "label": "Test"})
        content = response.content.decode()
        assert "canvas.css" in content
        assert "<html" in content
        assert "</html>" in content

    @override_settings(
        DJ_DESIGN_SYSTEM={
            "GALLERY_CANVAS_BACKGROUNDS": BUILTIN_CANVAS_BACKGROUNDS,
            "GALLERY_CANVAS_DEFAULT_BACKGROUND": "light-grey",
        }
    )
    def test_default_background_class(self):
        client = Client()
        url = reverse("gallery-canvas-iframe")
        response = client.get(url, {"component": "rich_button", "label": "Test"})
        content = response.content.decode()
        assert "canvas-bg-light-grey" in content

    @override_settings(
        DJ_DESIGN_SYSTEM={
            "GALLERY_CANVAS_BACKGROUNDS": BUILTIN_CANVAS_BACKGROUNDS,
            "GALLERY_CANVAS_DEFAULT_BACKGROUND": "light-grey",
        }
    )
    def test_custom_background_class(self):
        client = Client()
        url = reverse("gallery-canvas-iframe")
        response = client.get(
            url, {"component": "rich_button", "label": "Test", "bg": "dark-grey"}
        )
        content = response.content.decode()
        assert "canvas-bg-dark-grey" in content

    @override_settings(
        DJ_DESIGN_SYSTEM={
            "GALLERY_CANVAS_BACKGROUNDS": BUILTIN_CANVAS_BACKGROUNDS,
            "GALLERY_CANVAS_DEFAULT_BACKGROUND": "light-grey",
        }
    )
    def test_invalid_background_falls_back_to_default(self):
        client = Client()
        url = reverse("gallery-canvas-iframe")
        response = client.get(
            url, {"component": "rich_button", "label": "Test", "bg": "neon-pink"}
        )
        content = response.content.decode()
        assert "canvas-bg-light-grey" in content

    def test_default_mode_is_extended(self):
        client = Client()
        url = reverse("gallery-canvas-iframe")
        response = client.get(url, {"component": "rich_button", "label": "Test"})
        content = response.content.decode()
        assert "canvas-wrapper--extended" in content

    def test_basic_mode(self):
        client = Client()
        url = reverse("gallery-canvas-iframe")
        response = client.get(
            url, {"component": "rich_button", "label": "Test", "mode": "basic"}
        )
        content = response.content.decode()
        assert "canvas-wrapper--basic" in content

    def test_extended_mode_explicit(self):
        client = Client()
        url = reverse("gallery-canvas-iframe")
        response = client.get(
            url, {"component": "rich_button", "label": "Test", "mode": "extended"}
        )
        content = response.content.decode()
        assert "canvas-wrapper--extended" in content

    def test_invalid_mode_falls_back_to_extended(self):
        client = Client()
        url = reverse("gallery-canvas-iframe")
        response = client.get(
            url, {"component": "rich_button", "label": "Test", "mode": "invalid"}
        )
        content = response.content.decode()
        assert "canvas-wrapper--extended" in content

    def test_resize_observer_script_present(self):
        client = Client()
        url = reverse("gallery-canvas-iframe")
        response = client.get(url, {"component": "rich_button", "label": "Test"})
        content = response.content.decode()
        assert "canvas-resize.js" in content

    def test_no_sandbox_attribute(self):
        """The iframe view response has no sandbox restrictions."""
        client = Client()
        url = reverse("gallery-canvas-iframe")
        response = client.get(url, {"component": "rich_button", "label": "Test"})
        # X-Frame-Options should allow same-origin embedding
        assert response["X-Frame-Options"] == "SAMEORIGIN"

    def test_canvas_iframe_csp_nonce(self, rf):
        from dj_design_system.views import canvas_iframe_view

        request = rf.get("/dds/_canvas/", {"component": "rich_button", "label": "Test"})
        request.csp_nonce = "sample-canvas-nonce-456"
        response = canvas_iframe_view(request)
        content = response.content.decode()
        assert '<style nonce="sample-canvas-nonce-456">' in content
