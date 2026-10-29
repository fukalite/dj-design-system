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
        assert themes[0].value == "default"

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
        assert theme.label == "Custom"
        assert theme.css == ["css/custom.css"]
        assert theme.js == ["js/custom.js"]

        default_theme = get_default_theme()
        assert default_theme.value == "custom"

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


class TestGalleryUIThemeSettings:
    def test_default_gallery_ui_themes(self):
        from dj_design_system.settings import (
            get_default_gallery_ui_theme,
            get_gallery_ui_themes,
        )

        ui_themes = get_gallery_ui_themes()
        values = [t.value for t in ui_themes]
        assert "desert" in values
        assert "classic" in values

        desert = next(t for t in ui_themes if t.value == "desert")
        assert desert.supports_dark_mode is True

        classic = next(t for t in ui_themes if t.value == "classic")
        assert classic.supports_dark_mode is False

        default_theme = get_default_gallery_ui_theme()
        assert default_theme.value == "desert"

    @override_settings(
        DJ_DESIGN_SYSTEM={
            "GALLERY_UI_THEMES": {
                "nord": {
                    "label": "Nordic Frost",
                    "css": "nord/theme.css",
                    "js": ["nord/theme.js"],
                    "dark_mode": {
                        "css": ["nord/dark.css"],
                    },
                },
                "solarized": {
                    "label": "Solarized Light",
                    "css": ["solarized/light.css"],
                },
            },
            "GALLERY_DEFAULT_UI_THEME": "nord",
        }
    )
    def test_custom_gallery_ui_themes_override(self):
        from dj_design_system.settings import (
            get_default_gallery_ui_theme,
            get_gallery_ui_theme,
            get_gallery_ui_themes,
        )

        themes = get_gallery_ui_themes()
        assert len(themes) == 2
        assert themes[0].value == "nord"
        assert themes[0].label == "Nordic Frost"
        assert themes[0].css == ["nord/theme.css"]
        assert themes[0].js == ["nord/theme.js"]
        assert themes[0].supports_dark_mode is True
        assert themes[0].dark_mode.css == ["nord/dark.css"]

        assert themes[1].value == "solarized"
        assert themes[1].supports_dark_mode is False

        nord = get_gallery_ui_theme("nord")
        assert nord is not None
        assert nord.value == "nord"

        nonexistent = get_gallery_ui_theme("nonexistent")
        assert nonexistent is None

        default_ui = get_default_gallery_ui_theme()
        assert default_ui.value == "nord"


class TestGalleryDocVariantsSettings:
    """Tests for GALLERY_DOC_VARIANTS normalization and helpers."""

    def test_default_doc_variants(self):
        from dj_design_system.settings import get_doc_variant_by_key, get_doc_variants
        from dj_design_system.types import DocVariantStrategy

        variants = get_doc_variants()
        assert [v.key for v in variants] == [
            "minimal",
            "maximal",
            "defaults",
            "all_slots",
        ]
        min_v = get_doc_variant_by_key(key="minimal")
        assert min_v is not None
        assert min_v.name == "basic"
        assert min_v.label == "Minimal example"
        assert min_v.strategy == DocVariantStrategy.MINIMAL
        assert min_v.show_in_docs is True

        max_v = get_doc_variant_by_key(key="maximal")
        assert max_v is not None
        assert max_v.name == "maximal"
        assert max_v.label == "All parameters"
        assert max_v.strategy == DocVariantStrategy.MAXIMAL
        assert max_v.show_in_docs is True

        defaults_v = get_doc_variant_by_key(key="defaults")
        assert defaults_v is not None
        assert defaults_v.show_in_docs is False

        all_slots_v = get_doc_variant_by_key(key="all_slots")
        assert all_slots_v is not None
        assert all_slots_v.show_in_docs is False

        assert get_doc_variant_by_key(key="nonexistent") is None

    def test_dict_overrides_rename_disable_and_enable(self, settings):
        from dj_design_system.settings import get_doc_variant_by_key, get_doc_variants

        settings.DJ_DESIGN_SYSTEM = {
            "GALLERY_DOC_VARIANTS": {
                "minimal": {"name": "simple", "label": "Quick start"},
                "maximal": {"show_in_docs": False},
                "defaults": {"show_in_docs": True},
                "all_slots": True,
                "compact": {
                    "name": "compact",
                    "label": "Compact preview",
                    "kwargs": {"size": "sm"},
                },
            }
        }
        variants = get_doc_variants()
        min_v = get_doc_variant_by_key(key="minimal")
        assert min_v is not None
        assert min_v.name == "simple"
        assert min_v.label == "Quick start"
        assert min_v.show_in_docs is True

        max_v = get_doc_variant_by_key(key="maximal")
        assert max_v is not None
        assert max_v.show_in_docs is False

        def_v = get_doc_variant_by_key(key="defaults")
        assert def_v is not None
        assert def_v.show_in_docs is True

        slots_v = get_doc_variant_by_key(key="all_slots")
        assert slots_v is not None
        assert slots_v.show_in_docs is True

        compact_v = get_doc_variant_by_key(key="compact")
        assert compact_v is not None
        assert compact_v.name == "compact"
        assert compact_v.label == "Compact preview"
        assert compact_v.kwargs == {"size": "sm"}
        assert compact_v.show_in_docs is True
        assert len(variants) == 5

    def test_dict_disable_via_none_false_or_empty_dict(self, settings):
        from dj_design_system.settings import get_doc_variant_by_key

        settings.DJ_DESIGN_SYSTEM = {
            "GALLERY_DOC_VARIANTS": {
                "minimal": None,
                "maximal": {},
                "defaults": False,
            }
        }
        assert get_doc_variant_by_key(key="minimal").show_in_docs is False
        assert get_doc_variant_by_key(key="maximal").show_in_docs is False
        assert get_doc_variant_by_key(key="defaults").show_in_docs is False

    def test_sequence_format(self, settings):
        from dj_design_system.settings import get_doc_variants

        settings.DJ_DESIGN_SYSTEM = {
            "GALLERY_DOC_VARIANTS": ["basic", "defaults", "custom_doc"]
        }
        enabled = [v for v in get_doc_variants() if v.show_in_docs]
        assert [v.name for v in enabled] == ["basic", "defaults", "custom_doc"]
