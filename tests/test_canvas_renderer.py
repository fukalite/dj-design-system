import pytest
from django.test import override_settings

from dj_design_system.constants import BUILTIN_APP_LABEL, BUILTIN_GALLERY_CSS
from dj_design_system.data import ComponentMedia
from dj_design_system.services.canvas_renderer import (
    build_canvas_bg_styles,
    build_canvas_srcdoc,
    build_html_attrs,
    build_markdown_canvas_media,
    build_theme_app_media,
    render_canvas_block,
)
from dj_design_system.settings import get_backgrounds, get_theme
from dj_design_system.types import ColorScheme, DarkModeConfig, Theme


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

    def test_srcdoc_loads_global_js_before_component_js(self):
        with override_settings(
            DJ_DESIGN_SYSTEM={"GLOBAL_JS": ["https://cdn.example.com/global.js"]}
        ):
            srcdoc = build_canvas_srcdoc(
                "<p>Hi</p>",
                component_js='<script src="/static/component.js"></script>',
            )
        assert 'src="https://cdn.example.com/global.js"' in srcdoc
        assert srcdoc.index("global.js") < srcdoc.index("component.js")

    def test_srcdoc_styles_theme_background(self):
        """A theme's custom canvas background is styled in srcdoc canvases too."""
        theme = Theme(
            value="midnight",
            label="Midnight",
            canvas_background={"color": "#123456"},
        )
        srcdoc = build_canvas_srcdoc(
            rendered_html="<p>themed</p>",
            theme_dict=theme,
            bg_class="canvas-bg-theme-midnight",
        )
        assert ".canvas-bg-theme-midnight" in srcdoc
        assert "#123456" in srcdoc


class TestBuildCanvasBgStyles:
    def test_body_follows_wrapper_background(self):
        """The body is painted too, so space below a basic-mode wrapper matches (#111)."""
        styles = build_canvas_bg_styles()
        for bg in get_backgrounds():
            assert (
                f".canvas-bg-{bg['value']}, body:has(.canvas-bg-{bg['value']})"
                in styles
            )

    def test_theme_background_rule(self):
        theme = Theme(
            value="midnight",
            label="Midnight",
            canvas_background={"color": "#123456"},
        )
        styles = build_canvas_bg_styles(theme_dict=theme)
        assert (
            ".canvas-bg-theme-midnight, body:has(.canvas-bg-theme-midnight) "
            "{ background: #123456; }"
        ) in styles

    def test_nonce_is_escaped(self):
        styles = build_canvas_bg_styles(csp_nonce='abc"def')
        assert styles.startswith('<style nonce="abc&quot;def">')

    def test_no_nonce(self):
        assert build_canvas_bg_styles().startswith("<style>")


class TestBuildMarkdownCanvasMedia:
    def test_consumer_app_includes_merged_media_only(self):
        class MockRegistry:
            def get_merged_media(self):
                return ComponentMedia(
                    css=["app/component.css"], js=["app/component.js"]
                )

            def get_builtin_media(self):
                return ComponentMedia(
                    css=["builtin/button.css"], js=["builtin/button.js"]
                )

        css_tags, js_tags = build_markdown_canvas_media(
            app_label="my_app", registry=MockRegistry()
        )
        assert "app/component.css" in css_tags
        assert "app/component.js" in js_tags
        assert BUILTIN_GALLERY_CSS not in css_tags
        assert "builtin/button.css" not in css_tags
        assert "builtin/button.js" not in js_tags

    def test_builtin_app_includes_gallery_css_and_builtin_media(self):
        class MockRegistry:
            def get_merged_media(self):
                return ComponentMedia(
                    css=["app/component.css"], js=["app/component.js"]
                )

            def get_builtin_media(self):
                return ComponentMedia(
                    css=["builtin/button.css"], js=["builtin/button.js"]
                )

        css_tags, js_tags = build_markdown_canvas_media(
            app_label=BUILTIN_APP_LABEL, registry=MockRegistry()
        )
        assert BUILTIN_GALLERY_CSS in css_tags
        assert "builtin/button.css" in css_tags
        assert "builtin/button.js" in js_tags
        assert "app/component.css" in css_tags
        assert "app/component.js" in js_tags


class TestCanvasRendererColorScheme:
    def test_build_html_attrs_light_mode(self):
        theme = Theme(
            value="dds",
            label="DDS",
            html_attrs={
                "html": {"class": "gallery-theme-light", "lang": "en"},
                "body": {"class": "dds-body"},
            },
            dark_mode=DarkModeConfig(
                html_attrs={
                    "html": {"class": "gallery-theme-dark"},
                    "body": {"class": "dds-body-dark"},
                },
            ),
        )
        html_attrs, body_attrs = build_html_attrs(
            theme_dict=theme, color_scheme=ColorScheme.LIGHT
        )
        assert 'class="gallery-theme-light"' in html_attrs
        assert 'lang="en"' in html_attrs
        assert 'class="dds-body"' in body_attrs

    def test_build_html_attrs_dark_mode_overrides(self):
        theme = Theme(
            value="dds",
            label="DDS",
            html_attrs={
                "html": {"class": "gallery-theme-light", "lang": "en"},
                "body": {"class": "dds-body"},
            },
            dark_mode=DarkModeConfig(
                html_attrs={
                    "html": {"class": "gallery-theme-dark"},
                    "body": {"class": "dds-body-dark"},
                },
            ),
        )
        html_attrs, body_attrs = build_html_attrs(
            theme_dict=theme, color_scheme=ColorScheme.DARK
        )
        assert 'class="gallery-theme-dark"' in html_attrs
        assert "gallery-theme-light" not in html_attrs
        assert 'lang="en"' in html_attrs
        assert 'class="dds-body-dark"' in body_attrs

    def test_build_html_attrs_dark_mode_ignored_if_not_configured(self):
        theme = Theme(
            value="basic",
            label="Basic",
            html_attrs={"html": {"class": "theme-basic"}},
        )
        html_attrs, body_attrs = build_html_attrs(
            theme_dict=theme, color_scheme=ColorScheme.DARK
        )
        assert 'class="theme-basic"' in html_attrs

    def test_build_theme_app_media_dark_mode(self):
        theme = Theme(
            value="dds",
            label="DDS",
            css=["base.css"],
            js=["base.js"],
            dark_mode=DarkModeConfig(
                css=["dark.css"],
                js=["dark.js"],
            ),
        )
        css_tags, js_tags = build_theme_app_media(
            theme, None, color_scheme=ColorScheme.DARK
        )
        assert "base.css" in css_tags
        assert "dark.css" in css_tags
        assert "base.js" in js_tags
        assert "dark.js" in js_tags

    def test_build_canvas_bg_styles_dark_mode_custom(self):
        theme = Theme(
            value="brand",
            label="Brand",
            canvas_background={"color": "#ffffff"},
            dark_mode=DarkModeConfig(
                canvas_background={"color": "#111111"},
            ),
        )
        styles = build_canvas_bg_styles(theme_dict=theme)
        assert ".canvas-bg-theme-brand" in styles
        assert "#ffffff" in styles
        assert ".canvas-bg-theme-brand-dark" in styles
        assert "#111111" in styles

    def test_build_canvas_srcdoc_resolves_dark_mode_background(self):
        theme = Theme(
            value="brand",
            label="Brand",
            canvas_background="white",
            dark_mode=DarkModeConfig(
                canvas_background="dark",
            ),
        )
        srcdoc_dark = build_canvas_srcdoc(
            rendered_html="<p>dark</p>",
            theme_dict=theme,
            color_scheme=ColorScheme.DARK,
        )
        assert "canvas-bg-dark" in srcdoc_dark

        srcdoc_light = build_canvas_srcdoc(
            rendered_html="<p>light</p>",
            theme_dict=theme,
            color_scheme=ColorScheme.LIGHT,
        )
        assert "canvas-bg-white" in srcdoc_light
