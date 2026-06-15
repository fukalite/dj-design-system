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
