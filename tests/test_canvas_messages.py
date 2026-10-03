"""The canvas's error and warning messages, rendered from shared templates."""

import pytest
from django.utils.html import format_html
from django.utils.safestring import SafeData

from dj_design_system.services.canvas_messages import canvas_error, plain_str_warning


class TestCanvasError:
    def test_matches_the_legacy_markup(self):
        assert canvas_error("Missing component.") == (
            '<p class="gallery-canvas-error">Canvas error: Missing component.</p>'
        )

    def test_label(self):
        assert canvas_error("boom", label="Could not render") == (
            '<p class="gallery-canvas-error">Could not render: boom</p>'
        )

    def test_escapes_the_message(self):
        markup = canvas_error("<b>x</b> & 'y'")
        assert "&lt;b&gt;x&lt;/b&gt; &amp; &#x27;y&#x27;" in markup
        assert "<b>" not in markup

    def test_shows_the_source_when_given(self):
        assert canvas_error("boom", source="{% x <y> %}") == (
            '<p class="gallery-canvas-error">Canvas error: boom</p>'
            "<pre><code>{% x &lt;y&gt; %}</code></pre>"
        )

    def test_is_safe(self):
        assert isinstance(canvas_error("boom"), SafeData)


class TestPlainStrWarning:
    def test_matches_the_legacy_markup(self):
        legacy = format_html(
            '<div class="gallery-canvas-warning">'
            '<p class="gallery-canvas-warning__message">'
            "<code>{}.render()</code> returned a plain <code>str</code>, so its "
            "HTML is shown escaped. Return <code>format_html(...)</code> or "
            "<code>mark_safe(...)</code> from <code>render()</code> to render it."
            "</p>"
            '<pre class="gallery-canvas-warning__output">{}</pre>'
            "</div>",
            "Card",
            "<b>x</b>",
        )
        assert plain_str_warning("Card", "<b>x</b>") == legacy

    def test_escapes_the_output(self):
        assert "&lt;script&gt;" in plain_str_warning("Card", "<script>")


@pytest.mark.parametrize(
    "path",
    [
        "dj_design_system/views/canvas.py",
        "dj_design_system/services/canvas.py",
        "dj_design_system/services/markdown_canvas.py",
    ],
)
def test_no_hand_written_message_markup(path):
    from pathlib import Path

    source = Path(path).read_text()
    assert "gallery-canvas-error" not in source
    assert "gallery-canvas-warning" not in source
