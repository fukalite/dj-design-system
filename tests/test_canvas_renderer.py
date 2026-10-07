import pytest

from dj_design_system.services.canvas_renderer import (
    build_canvas_srcdoc,
    render_canvas_block,
)


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

    def test_resize_script_reports_wrapper_height_and_body_bg(self):
        """Basic-mode resize script reports wrapper height rather than documentElement.scrollHeight (#111)."""
        srcdoc = build_canvas_srcdoc(
            rendered_html="<p>basic mode</p>",
            mode_class="canvas-wrapper--basic",
        )
        assert "Math.max(w.scrollHeight,w.offsetHeight)" in srcdoc
        assert "document.documentElement.scrollHeight" not in srcdoc
        assert "body:has(.canvas-bg-" in srcdoc
