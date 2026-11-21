"""Exhaustive tests for the 0.10.x legacy dict compatibility adapter, warnings, and checks."""

from __future__ import annotations

import warnings

import pytest
from django.core.checks import Error
from django.core.checks import Warning as CheckWarning
from django.core.exceptions import ImproperlyConfigured
from django.test import override_settings

from dj_design_system.checks import check_design_system_settings
from dj_design_system.config import (
    DDS_DEFAULT_CANVAS_BACKGROUNDS,
    DesignSystemSettings,
)
from dj_design_system.exceptions import (
    DjDesignSystemDeprecationWarning,
    RemovedInDjDS10Warning,
)
from dj_design_system.services import config as config_service
from dj_design_system.settings import dds_settings
from dj_design_system.types import FlattenStrategy, NodeType


class TestDeprecationWarningHierarchy:
    def test_warning_inheritance(self) -> None:
        assert issubclass(DjDesignSystemDeprecationWarning, DeprecationWarning)
        assert issubclass(RemovedInDjDS10Warning, DjDesignSystemDeprecationWarning)

    def test_emits_once_per_key_signature_and_resets_on_override(self) -> None:
        raw = {"DESIGN_SYSTEM_NAME": "Legacy"}
        with override_settings(DJ_DESIGN_SYSTEM=raw):
            config_service.clear_config_cache()
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                config_service.get_config()
                config_service.get_config()
                config_service.get_config()
            matching = [
                w for w in caught if issubclass(w.category, RemovedInDjDS10Warning)
            ]
            assert len(matching) == 1

        with override_settings(DJ_DESIGN_SYSTEM={"DESIGN_SYSTEM_NAME": "Again"}):
            with warnings.catch_warnings(record=True) as caught2:
                warnings.simplefilter("always")
                config_service.get_config()
            matching2 = [
                w for w in caught2 if issubclass(w.category, RemovedInDjDS10Warning)
            ]
            assert len(matching2) == 1

    def test_explicit_empty_dict_warns_but_omitted_does_not(self) -> None:
        with override_settings(DJ_DESIGN_SYSTEM={}):
            config_service.clear_config_cache()
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                config_service.get_config()
            assert any(issubclass(w.category, RemovedInDjDS10Warning) for w in caught)

        with override_settings(DJ_DESIGN_SYSTEM=None):
            config_service.clear_config_cache()
            with warnings.catch_warnings(record=True) as caught_none:
                warnings.simplefilter("always")
                config_service.get_config()
            assert not any(
                issubclass(w.category, RemovedInDjDS10Warning) for w in caught_none
            )


class TestLegacyAdapterAll29Keys:
    def test_adapts_all_29_legacy_keys(self) -> None:
        legacy = {
            "DESIGN_SYSTEM_NAME": "Legacy DS",
            "ENABLE_GALLERY": False,
            "GALLERY_IS_PUBLIC": False,
            "GALLERY_NAV_ORDER": [NodeType.COMPONENT, NodeType.FOLDER],
            "GLOBAL_CSS": "global.css",
            "GLOBAL_JS": ["global.js"],
            "GLOBAL_CSS_BUNDLES": [("main",)],
            "GLOBAL_JS_BUNDLES": [("app", "ALT")],
            "GALLERY_CANVAS_BACKGROUNDS": {
                "paper": {"label": "Paper", "color": "#faf8f5"},
            },
            "GALLERY_CANVAS_EXTRA_BACKGROUNDS": {
                "ink": {"label": "Ink", "color": "#111111"},
            },
            "GALLERY_CANVAS_DEFAULT_BACKGROUND": "ink",
            "GALLERY_CANVAS_HTML_ATTRS": {"html": {"lang": "en-GB"}},
            "GALLERY_CODEHILITE_STYLE": "",
            "GALLERY_THEMES": {
                "brand": {
                    "label": "Brand",
                    "css": ["brand.css"],
                    "canvas_background": "paper",
                    "dark_mode": {"html_attrs": {"html": {"data-mode": "dark"}}},
                }
            },
            "GALLERY_DEFAULT_THEME": "brand",
            "GALLERY_UI_THEMES": {
                "custom_ui": {"label": "Custom UI"},
            },
            "GALLERY_DEFAULT_UI_THEME": "custom_ui",
            "GALLERY_INCLUDE_APPS": ["demo_components"],
            "GALLERY_EXCLUDE_APPS": ["broken_components"],
            "GALLERY_EXTRA_CSS": "gallery-extra.css",
            "GALLERY_DOC_VARIANTS": {"minimal": True, "maximal": False},
            "APP_THEMES": {
                "app_all": None,
                "app_none": [],
                "app_one": "brand",
                "app_list": ["brand"],
            },
            "APP_CSS": {"app_one": "one.css"},
            "APP_JS": {"app_one": ["one.js"]},
            "APP_CSS_BUNDLES": {"app_one": [("one_css",)]},
            "APP_JS_BUNDLES": {"app_one": [("one_js", "CUSTOM")]},
            "APP_CANVAS_HTML_ATTRS": {"app_one": {"body": {"class": "one-body"}}},
            "COMPONENT_DIRECTORIES": {
                "app_one": {
                    "": {"prefix": "one", "flatten": "all", "label": "App One"},
                    "cards": {
                        "prefix": "one_cards",
                        "flatten": FlattenStrategy.LEAF,
                        "promote_to_app": True,
                        "label": "One Cards",
                    },
                }
            },
            "COMPONENT_NAMESPACES": {
                "app_one": {"": "ignored_because_dirs_present"},
                "app_fallback": {"": "fb", "sub": "fb_sub"},
            },
        }

        with override_settings(DJ_DESIGN_SYSTEM=legacy):
            cfg = config_service.get_config()
            assert cfg.name == "Legacy DS"
            assert cfg.gallery.enabled is False
            assert cfg.gallery.is_public is False
            assert cfg.gallery.nav_order == (NodeType.COMPONENT, NodeType.FOLDER)
            assert cfg.css == ("global.css",)
            assert cfg.js == ("global.js",)
            assert cfg.css_bundles == (("main",),)
            assert cfg.js_bundles == (("app", "ALT"),)
            assert set(cfg.canvas.backgrounds.keys()) == {"paper", "ink"}
            assert cfg.canvas.default_background == "ink"
            assert cfg.canvas.html_attrs["html"]["lang"] == "en-GB"
            assert cfg.gallery.codehilite_style == ""
            assert dds_settings.GALLERY_CODEHILITE_STYLE == ""
            assert "brand" in cfg.themes
            assert cfg.default_theme == "brand"
            assert "custom_ui" in cfg.gallery.ui_themes
            assert cfg.gallery.default_ui_theme == "custom_ui"
            assert cfg.gallery.include_apps == ("demo_components",)
            assert cfg.gallery.exclude_apps == ("broken_components",)
            assert cfg.gallery.extra_css == ("gallery-extra.css",)
            assert cfg.gallery.doc_variants["minimal"].show_in_docs is True
            assert cfg.gallery.doc_variants["maximal"].show_in_docs is False
            assert "defaults" in cfg.gallery.doc_variants
            assert cfg.gallery.doc_variants["defaults"].show_in_docs is False

            assert config_service.get_app_settings(app_label="app_all").themes is None
            assert config_service.get_app_settings(app_label="app_none").themes == ()
            assert config_service.get_app_settings(app_label="app_one").themes == (
                "brand",
            )
            assert config_service.get_app_settings(app_label="app_list").themes == (
                "brand",
            )

            app_one = config_service.get_app_settings(app_label="app_one")
            assert app_one.prefix == "one"
            assert app_one.flatten is FlattenStrategy.ALL
            assert app_one.label == "App One"
            assert app_one.css == ("one.css",)
            assert app_one.js == ("one.js",)
            assert app_one.css_bundles == (("one_css",),)
            assert app_one.js_bundles == (("one_js", "CUSTOM"),)
            assert app_one.canvas_html_attrs == {"body": {"class": "one-body"}}
            assert app_one.directories["cards"].prefix == "one_cards"
            assert app_one.directories["cards"].promote_to_app is True

            app_fb = config_service.get_app_settings(app_label="app_fallback")
            assert app_fb.prefix == "fb"
            assert app_fb.directories["sub"].prefix == "fb_sub"

    def test_none_mappings_and_canvas_background_combinations(self) -> None:
        with override_settings(
            DJ_DESIGN_SYSTEM={
                "COMPONENT_NAMESPACES": None,
                "APP_CSS": None,
                "APP_THEMES": None,
                "GALLERY_CANVAS_BACKGROUNDS": {},
                "GALLERY_NAV_ORDER": "alphabetical",
            }
        ):
            cfg = config_service.get_config()
            assert dict(cfg.canvas.backgrounds) == {}
            assert cfg.gallery.nav_order == "alphabetical"

        with override_settings(
            DJ_DESIGN_SYSTEM={
                "GALLERY_CANVAS_EXTRA_BACKGROUNDS": {
                    "brand": {"label": "Brand", "color": "#112233"}
                }
            }
        ):
            cfg2 = config_service.get_config()
            assert "brand" in cfg2.canvas.backgrounds
            for slug in DDS_DEFAULT_CANVAS_BACKGROUNDS:
                assert slug in cfg2.canvas.backgrounds

    def test_new_style_keys_in_legacy_dict_raise_improperly_configured(self) -> None:
        with override_settings(DJ_DESIGN_SYSTEM={"name": "Oops", "gallery": {}}):
            with pytest.raises(ImproperlyConfigured, match="DesignSystemSettings"):
                config_service.get_config()


class TestLegacyDeprecationChecks:
    def test_e020_new_style_keys_in_dict(self) -> None:
        with override_settings(DJ_DESIGN_SYSTEM={"name": "Oops", "apps": {}}):
            messages = check_design_system_settings()
        errors = [m for m in messages if isinstance(m, Error)]
        assert any(m.id == "dj_design_system.E020" for m in errors)

    def test_w010_legacy_dict_warning_including_empty_dict(self) -> None:
        with override_settings(DJ_DESIGN_SYSTEM={}):
            messages = check_design_system_settings()
        warnings_list = [m for m in messages if isinstance(m, CheckWarning)]
        assert any(m.id == "dj_design_system.W010" for m in warnings_list)

        with override_settings(DJ_DESIGN_SYSTEM=DesignSystemSettings()):
            typed_messages = check_design_system_settings()
        assert not any(m.id == "dj_design_system.W010" for m in typed_messages)

    def test_w011_component_namespaces_warning(self) -> None:
        with override_settings(
            DJ_DESIGN_SYSTEM={"COMPONENT_NAMESPACES": {"demo_components": {"": "ui"}}}
        ):
            messages = check_design_system_settings()
        assert any(m.id == "dj_design_system.W011" for m in messages)

    def test_w012_unknown_legacy_key_with_difflib_hint(self) -> None:
        with override_settings(DJ_DESIGN_SYSTEM={"GALERY_IS_PUBLIC": False}):
            messages = check_design_system_settings()
        w012 = [m for m in messages if m.id == "dj_design_system.W012"]
        assert len(w012) == 1
        assert "GALLERY_IS_PUBLIC" in (w012[0].hint or "")
