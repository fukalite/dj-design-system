"""Tests for settings helpers."""

from django.test import override_settings

from dj_design_system.settings import get_default_background


class TestGetDefaultBackground:
    def test_returns_matching_background(self):
        """Returns the dict for the configured default value."""
        bg = get_default_background()
        assert "value" in bg
        assert "label" in bg
        assert "color" in bg

    @override_settings(
        DJ_DESIGN_SYSTEM={
            "GALLERY_CANVAS_BACKGROUNDS": {
                "warm": {"label": "Warm", "color": "#fff1e0"}
            },
            "GALLERY_CANVAS_DEFAULT_BACKGROUND": "nonexistent",
        }
    )
    def test_fallback_to_first_when_default_not_found(self):
        """Falls back to first background when default value is not in the list."""
        bg = get_default_background()
        assert bg["value"] == "warm"

    @override_settings(
        DJ_DESIGN_SYSTEM={
            "GALLERY_CANVAS_BACKGROUNDS": {},
            "GALLERY_CANVAS_EXTRA_BACKGROUNDS": {},
            "GALLERY_CANVAS_DEFAULT_BACKGROUND": "nonexistent",
        }
    )
    def test_fallback_to_hardcoded_when_no_backgrounds(self):
        """Falls back to hard-coded light-grey when no backgrounds are configured."""
        bg = get_default_background()
        assert bg["value"] == "light-grey"
        assert bg["color"] == "#f0f0f0"


class TestThemeSettings:
    def test_get_themes(self):
        from dj_design_system.settings import get_themes

        themes = get_themes()
        assert len(themes) >= 1
        assert themes[0]["value"] == "default"

    @override_settings(
        DJ_DESIGN_SYSTEM={
            "GALLERY_THEMES": {
                "custom": {
                    "label": "Custom",
                    "html_attrs": {"html": {"data-theme": "custom"}},
                    "css": "css/custom.css",
                    "js": "js/custom.js",
                }
            }
        }
    )
    def test_get_theme_and_coercion(self):
        from dj_design_system.settings import get_default_theme, get_theme

        theme = get_theme("custom")
        assert theme is not None
        assert theme["label"] == "Custom"
        assert theme["css"] == ["css/custom.css"]
        assert theme["js"] == ["js/custom.js"]

        default_theme = get_default_theme()
        assert default_theme["value"] == "custom"

    @override_settings(
        DJ_DESIGN_SYSTEM={
            "APP_CSS": {"my_app": "my_app.css"},
            "APP_JS": {"my_app": ["my_app.js"]},
            "APP_CANVAS_HTML_ATTRS": {"my_app": {"body": {"class": "my-app-body"}}},
        }
    )
    def test_get_app_static_and_attrs(self):
        from dj_design_system.settings import get_app_html_attrs, get_app_static

        css, js = get_app_static("my_app")
        assert css == ["my_app.css"]
        assert js == ["my_app.js"]

        attrs = get_app_html_attrs("my_app")
        assert attrs == {"body": {"class": "my-app-body"}}
