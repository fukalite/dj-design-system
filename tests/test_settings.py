"""Tests for typed configuration dataclasses and config service helpers."""

from __future__ import annotations

import dataclasses

from django.test import override_settings

from dj_design_system.config import (
    DDS_DEFAULT_CANVAS_BACKGROUNDS,
    DDS_DEFAULT_DOC_VARIANTS,
    AppSettings,
    CanvasBackground,
    CanvasSettings,
    DarkModeConfig,
    DesignSystemSettings,
    DocVariantConfig,
    GallerySettings,
    Theme,
)
from dj_design_system.services.config import (
    get_app_settings,
    get_backgrounds,
    get_default_background,
    get_default_background_slug,
    get_default_gallery_ui_theme,
    get_default_theme,
    get_doc_variant,
    get_doc_variants,
    get_gallery_ui_theme,
    get_gallery_ui_themes,
    get_theme,
    get_themes,
    resolve_doc_variants,
)
from dj_design_system.types import DocVariantStrategy


class TestGetDefaultBackground:
    def test_returns_matching_background(self):
        """Returns the CanvasBackground and slug for the configured default value."""
        bg = get_default_background()
        slug = get_default_background_slug()
        assert isinstance(bg, CanvasBackground)
        assert slug == "light-grey"
        assert bg == DDS_DEFAULT_CANVAS_BACKGROUNDS["light-grey"]
        assert "light-grey" in get_backgrounds()

    @override_settings(
        DJ_DESIGN_SYSTEM=DesignSystemSettings(
            canvas=CanvasSettings(
                backgrounds={
                    "warm": CanvasBackground(label="Warm", color="#fff1e0"),
                },
                default_background="nonexistent",
            )
        )
    )
    def test_fallback_to_first_when_default_not_found(self):
        """Falls back to first background when default value is not in the list."""
        bg = get_default_background()
        assert get_default_background_slug() == "warm"
        assert bg == CanvasBackground(label="Warm", color="#fff1e0")

    @override_settings(
        DJ_DESIGN_SYSTEM=DesignSystemSettings(
            canvas=CanvasSettings(
                backgrounds={},
                default_background="nonexistent",
            )
        )
    )
    def test_fallback_to_hardcoded_when_no_backgrounds(self):
        """Falls back to hard-coded light-grey when no backgrounds are configured."""
        bg = get_default_background()
        assert get_default_background_slug() == "light-grey"
        assert bg.color == "#f0f0f0"


class TestThemeSettings:
    def test_get_themes(self):
        themes = get_themes()
        assert len(themes) >= 1
        assert "default" in themes
        assert themes["default"].value == "default"

    @override_settings(
        DJ_DESIGN_SYSTEM=DesignSystemSettings(
            themes={
                "custom": Theme(
                    label="Custom",
                    html_attrs={"html": {"data-theme": "custom"}},
                    css="css/custom.css",
                    js="js/custom.js",
                )
            }
        )
    )
    def test_get_theme_and_coercion(self):
        theme = get_theme(identifier="custom")
        assert theme is not None
        assert theme.value == "custom"
        assert theme.label == "Custom"
        assert theme.css == ("css/custom.css",)
        assert theme.js == ("js/custom.js",)
        assert theme.html_attrs == {"html": {"data-theme": "custom"}}

        default_theme = get_default_theme()
        assert default_theme.value == "custom"

    @override_settings(
        DJ_DESIGN_SYSTEM=DesignSystemSettings(
            apps={
                "my_app": AppSettings(
                    css="my_app.css",
                    js=("my_app.js",),
                    canvas_html_attrs={"body": {"class": "my-app-body"}},
                )
            }
        )
    )
    def test_get_app_settings_static_and_attrs(self):
        resolved = get_app_settings(app_label="my_app")
        assert resolved.css == ("my_app.css",)
        assert resolved.js == ("my_app.js",)
        assert resolved.canvas_html_attrs == {"body": {"class": "my-app-body"}}


class TestGalleryUIThemeSettings:
    def test_default_gallery_ui_themes(self):
        ui_themes = get_gallery_ui_themes()
        assert "desert" in ui_themes
        assert "classic" in ui_themes

        desert = ui_themes["desert"]
        assert desert.supports_dark_mode is True

        classic = ui_themes["classic"]
        assert classic.supports_dark_mode is False

        default_theme = get_default_gallery_ui_theme()
        assert default_theme.value == "desert"

    @override_settings(
        DJ_DESIGN_SYSTEM=DesignSystemSettings(
            gallery=GallerySettings(
                ui_themes={
                    "nord": Theme(
                        label="Nordic Frost",
                        css="nord/theme.css",
                        js=("nord/theme.js",),
                        dark_mode=DarkModeConfig(
                            css=("nord/dark.css",),
                        ),
                    ),
                    "solarized": Theme(
                        label="Solarized Light",
                        css=("solarized/light.css",),
                    ),
                },
                default_ui_theme="nord",
            )
        )
    )
    def test_custom_gallery_ui_themes_override(self):
        themes = get_gallery_ui_themes()
        assert len(themes) == 2
        assert list(themes.keys()) == ["nord", "solarized"]

        nord_entry = themes["nord"]
        assert nord_entry.value == "nord"
        assert nord_entry.label == "Nordic Frost"
        assert nord_entry.css == ("nord/theme.css",)
        assert nord_entry.js == ("nord/theme.js",)
        assert nord_entry.supports_dark_mode is True
        assert nord_entry.dark_mode is not None
        assert nord_entry.dark_mode.css == ("nord/dark.css",)

        solarized_entry = themes["solarized"]
        assert solarized_entry.value == "solarized"
        assert solarized_entry.supports_dark_mode is False

        nord = get_gallery_ui_theme(identifier="nord")
        assert nord is not None
        assert nord.value == "nord"

        nonexistent = get_gallery_ui_theme(identifier="nonexistent")
        assert nonexistent is None

        default_ui = get_default_gallery_ui_theme()
        assert default_ui.value == "nord"


class TestGalleryDocVariantsSettings:
    """Tests for GallerySettings.doc_variants and resolve_doc_variants."""

    def test_default_doc_variants(self):
        variants = get_doc_variants()
        assert [v.key for v in variants] == [
            "minimal",
            "maximal",
            "defaults",
            "all_slots",
        ]
        min_v = get_doc_variant(key="minimal")
        assert min_v is not None
        assert min_v.name == "basic"
        assert min_v.label == "Minimal example"
        assert min_v.strategy == DocVariantStrategy.MINIMAL
        assert min_v.show_in_docs is True

        max_v = get_doc_variant(key="maximal")
        assert max_v is not None
        assert max_v.name == "maximal"
        assert max_v.label == "All parameters"
        assert max_v.strategy == DocVariantStrategy.MAXIMAL
        assert max_v.show_in_docs is True

        defaults_v = get_doc_variant(key="defaults")
        assert defaults_v is not None
        assert defaults_v.show_in_docs is False

        all_slots_v = get_doc_variant(key="all_slots")
        assert all_slots_v is not None
        assert all_slots_v.show_in_docs is False

        assert get_doc_variant(key="nonexistent") is None

    def test_typed_overrides_rename_disable_and_enable(self, settings):
        settings.DJ_DESIGN_SYSTEM = DesignSystemSettings(
            gallery=GallerySettings(
                doc_variants={
                    **DDS_DEFAULT_DOC_VARIANTS,
                    "minimal": dataclasses.replace(
                        DDS_DEFAULT_DOC_VARIANTS["minimal"],
                        name="simple",
                        label="Quick start",
                    ),
                    "maximal": dataclasses.replace(
                        DDS_DEFAULT_DOC_VARIANTS["maximal"],
                        show_in_docs=False,
                    ),
                    "defaults": dataclasses.replace(
                        DDS_DEFAULT_DOC_VARIANTS["defaults"],
                        show_in_docs=True,
                    ),
                    "all_slots": dataclasses.replace(
                        DDS_DEFAULT_DOC_VARIANTS["all_slots"],
                        show_in_docs=True,
                    ),
                    "compact": DocVariantConfig(
                        key="compact",
                        name="compact",
                        label="Compact preview",
                        strategy=DocVariantStrategy.CUSTOM,
                        kwargs={"size": "sm"},
                    ),
                }
            )
        )
        variants = get_doc_variants()
        min_v = get_doc_variant(key="minimal")
        assert min_v is not None
        assert min_v.name == "simple"
        assert min_v.label == "Quick start"
        assert min_v.show_in_docs is True

        max_v = get_doc_variant(key="maximal")
        assert max_v is not None
        assert max_v.show_in_docs is False

        def_v = get_doc_variant(key="defaults")
        assert def_v is not None
        assert def_v.show_in_docs is True

        slots_v = get_doc_variant(key="all_slots")
        assert slots_v is not None
        assert slots_v.show_in_docs is True

        compact_v = get_doc_variant(key="compact")
        assert compact_v is not None
        assert compact_v.name == "compact"
        assert compact_v.label == "Compact preview"
        assert compact_v.kwargs == {"size": "sm"}
        assert compact_v.show_in_docs is True
        assert len(variants) == 5

    def test_resolve_doc_variants_disable_via_none_false_or_empty_dict(self):
        resolved = resolve_doc_variants(
            raw_setting={
                "minimal": None,
                "maximal": {},
                "defaults": False,
            }
        )
        by_key = {v.key: v for v in resolved}
        assert by_key["minimal"].show_in_docs is False
        assert by_key["maximal"].show_in_docs is False
        assert by_key["defaults"].show_in_docs is False

    def test_resolve_doc_variants_sequence_format(self):
        resolved = resolve_doc_variants(raw_setting=["basic", "defaults", "custom_doc"])
        enabled = [v for v in resolved if v.show_in_docs]
        assert [v.name for v in enabled] == ["basic", "defaults", "custom_doc"]
