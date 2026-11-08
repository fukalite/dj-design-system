"""Tests for the canvas template tag."""

import pytest
from django.template import Context, Template

from dj_design_system.settings import get_default_theme


pytestmark = pytest.mark.django_db


class TestCanvasTemplateTag:
    """Test the {% canvas %}...{% endcanvas %} block tag."""

    def test_renders_iframe_element(self):
        """The canvas tag should output an <iframe> element."""
        template = Template(
            "{% load dj_design_system_gallery %}{% canvas %}<p>Hello</p>{% endcanvas %}"
        )
        result = template.render(Context())
        assert "<iframe" in result
        assert "srcdoc=" in result
        assert 'class="gallery-canvas"' in result

    def test_inner_content_appears_in_srcdoc(self):
        """The rendered inner content should appear inside the srcdoc attribute."""
        template = Template(
            "{% load dj_design_system_gallery %}"
            "{% canvas %}<p>Test content</p>{% endcanvas %}"
        )
        result = template.render(Context())
        # Content is HTML-escaped inside srcdoc attribute
        assert "Test content" in result

    def test_srcdoc_contains_html_document(self):
        """The srcdoc should contain a full HTML document structure."""
        template = Template(
            "{% load dj_design_system_gallery %}"
            "{% canvas %}<span>X</span>{% endcanvas %}"
        )
        result = template.render(Context())
        # The srcdoc value is HTML-escaped, so check for escaped versions
        assert "&lt;!DOCTYPE html&gt;" in result or "DOCTYPE" in result

    def test_canvas_wrapper_has_background_class(self):
        """The canvas wrapper inside srcdoc should have a background class."""
        template = Template(
            "{% load dj_design_system_gallery %}"
            "{% canvas %}<span>X</span>{% endcanvas %}"
        )
        result = template.render(Context())
        assert "canvas-bg-" in result

    def test_no_sandbox_attribute(self):
        """The iframe should not have a sandbox attribute (trusted components)."""
        template = Template(
            "{% load dj_design_system_gallery %}"
            "{% canvas %}<span>X</span>{% endcanvas %}"
        )
        result = template.render(Context())
        assert "sandbox" not in result

    def test_canvas_css_included(self):
        """The canvas.css stylesheet should be referenced in the srcdoc."""
        template = Template(
            "{% load dj_design_system_gallery %}"
            "{% canvas %}<span>X</span>{% endcanvas %}"
        )
        result = template.render(Context())
        assert "canvas.css" in result

    def test_assigns_sequential_data_canvas_id_for_auto_resizing(self):
        """Each {% canvas %} iframe gets a unique data-canvas-id matching its srcdoc wrapper."""
        template = Template(
            template_string=(
                "{% load dj_design_system_gallery %}"
                "{% canvas %}<span>First</span>{% endcanvas %}"
                "{% canvas %}<span>Second</span>{% endcanvas %}"
            )
        )
        result = template.render(context=Context())
        assert 'data-canvas-id="canvas-tag-1"' in result
        assert 'data-canvas-id="canvas-tag-2"' in result
        assert "data-canvas-id=&quot;canvas-tag-1&quot;" in result
        assert "data-canvas-id=&quot;canvas-tag-2&quot;" in result

    def test_resolves_theme_from_request_and_explicit_canvas_id(self, rf):
        """Canvas tag resolves theme from request query params and honours explicit _canvas_id."""
        request = rf.get("/", {"_dds_theme": "default"})
        request.csp_nonce = "nonce-123"
        template = Template(
            template_string=(
                "{% load dj_design_system_gallery %}"
                "{% canvas %}<span>Themed</span>{% endcanvas %}"
            )
        )
        result = template.render(
            context=Context({"request": request, "_canvas_id": "custom-id"})
        )
        assert 'data-canvas-id="custom-id"' in result
        assert "nonce=&quot;nonce-123&quot;" in result

    def test_gallery_theme_and_extra_stylesheet_tags(self, rf):
        """Gallery helper tags handle empty, light, and dark theme contexts."""
        request = rf.get("/")
        request.csp_nonce = "nonce-abc"
        theme = get_default_theme()
        template = Template(
            template_string=(
                "{% load dj_design_system_gallery %}"
                "{% builtin_component_stylesheets %}"
                "{% gallery_extra_stylesheets %}"
                "{% gallery_ui_theme_stylesheets %}"
                "{% gallery_ui_theme_scripts %}"
                "{% builtin_component_scripts %}"
            )
        )
        empty_out = template.render(context=Context())
        assert "<script" in empty_out

        themed_out = template.render(
            context=Context(
                {
                    "request": request,
                    "active_ui_theme": theme,
                    "gallery_theme": "dark",
                }
            )
        )
        assert 'nonce="nonce-abc"' in themed_out
