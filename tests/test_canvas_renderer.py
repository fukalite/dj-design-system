import pytest
from django.test import override_settings

from dj_design_system.services.canvas_renderer import (
    build_canvas_srcdoc,
    render_canvas_block,
)
from dj_design_system.settings import get_theme


@pytest.mark.django_db
class TestCanvasRenderer:
    def test_render_canvas_block_simple(self):
        source = '{% button "Click" %}'
        html = render_canvas_block(source)
        assert "btn" in html

    def test_render_canvas_block_nested(self):
        source = """
        <div class="test-wrapper">
            {% alert "warning" %}
                {% button "Click" %}
            {% endalert %}
        </div>
        """
        html = render_canvas_block(source)
        assert 'class="test-wrapper"' in html
        assert "alert-warning" in html
        assert "btn" in html

    def test_build_canvas_srcdoc(self):
        rendered_html = "<p>hello world</p>"
        srcdoc = build_canvas_srcdoc(
            rendered_html=rendered_html,
            component_css="<style>.foo { color: red; }</style>",
            component_js='<script>console.log("foo")</script>',
            mode_class="canvas-wrapper--basic",
        )
        assert "<!DOCTYPE html>" in srcdoc
        assert "<p>hello world</p>" in srcdoc
        assert ".foo { color: red; }" in srcdoc
        assert 'console.log("foo")' in srcdoc
        assert "canvas-wrapper--basic" in srcdoc
        assert "canvas-bg-" in srcdoc

    def test_basic_mode_injects_resizing_css(self):
        rendered_html = "<p>basic mode</p>"
        srcdoc = build_canvas_srcdoc(
            rendered_html=rendered_html,
            mode_class="canvas-wrapper--basic",
        )
        assert "<style>" in srcdoc
        assert "min-height: 0 !important" in srcdoc
        assert "height: auto !important" in srcdoc
        assert "overflow: hidden !important" in srcdoc

    def test_basic_mode_leaves_component_layout_alone(self):
        """The wrapper must not be a flex container (#156)."""
        srcdoc = build_canvas_srcdoc(
            rendered_html="<p>basic mode</p>",
            mode_class="canvas-wrapper--basic",
        )
        assert "display: flex" not in srcdoc
        assert "justify-content" not in srcdoc
        assert "align-items" not in srcdoc

    def test_srcdoc_preserves_external_urls(self):
        with override_settings(
            DJ_DESIGN_SYSTEM={
                "GLOBAL_CSS": ["https://fonts.googleapis.com/css2?family=Inter"],
                "GALLERY_THEMES": {
                    "default": {
                        "label": "Default",
                        "css": ["https://cdn.example.com/theme.css"],
                        "js": ["//cdn.example.com/theme.js"],
                    }
                },
                "APP_CSS": {
                    "demo_components": ["https://cdn.example.com/app.css?v=1&min=1"]
                },
            }
        ):
            srcdoc = build_canvas_srcdoc(
                "<p>Hi</p>",
                theme_dict=get_theme("default"),
                app_label="demo_components",
            )
        assert 'href="https://fonts.googleapis.com/css2?family=Inter"' in srcdoc
        assert 'href="https://cdn.example.com/theme.css"' in srcdoc
        assert 'src="//cdn.example.com/theme.js"' in srcdoc
        assert 'href="https://cdn.example.com/app.css?v=1&amp;min=1"' in srcdoc
