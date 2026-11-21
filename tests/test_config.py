"""Unit tests for dj_design_system.config typed settings dataclasses."""

from __future__ import annotations

import copy
import dataclasses
import pickle

import pytest

from dj_design_system.config import (
    DDS_DEFAULT_CANVAS_BACKGROUNDS,
    DDS_DEFAULT_DOC_VARIANTS,
    DDS_DEFAULT_NAV_ORDER,
    DDS_DEFAULT_THEMES,
    DDS_DEFAULT_UI_THEMES,
    UNSET,
    AppSettings,
    CanvasBackground,
    CanvasSettings,
    DarkModeConfig,
    DesignSystemSettings,
    DirectorySettings,
    DocVariantConfig,
    FrozenMapping,
    GallerySettings,
    Theme,
)
from dj_design_system.types import DocVariantStrategy, FlattenStrategy, NodeType


class TestFrozenMappingAndUnset:
    def test_frozen_mapping_is_immutable_and_dict_equal(self) -> None:
        mapping = FrozenMapping({"a": 1, "b": {"nested": 2}})
        assert mapping["a"] == 1
        assert len(mapping) == 2
        assert list(mapping) == ["a", "b"]
        assert mapping == {"a": 1, "b": {"nested": 2}}
        assert mapping == FrozenMapping({"a": 1, "b": {"nested": 2}})
        with pytest.raises(TypeError):
            mapping["a"] = 99  # type: ignore[index]

    def test_frozen_mapping_supports_deepcopy_pickle_and_asdict(self) -> None:
        cfg = DesignSystemSettings(
            canvas=CanvasSettings(html_attrs={"body": {"class": "x"}}),
            apps={"demo": AppSettings(prefix="ui")},
        )
        copied = copy.deepcopy(cfg)
        assert copied == cfg
        unpickled = pickle.loads(pickle.dumps(cfg))
        assert unpickled == cfg
        as_dict = dataclasses.asdict(cfg)
        assert as_dict["name"] == "Django Design System"
        assert as_dict["canvas"]["html_attrs"] == {"body": {"class": "x"}}

    def test_unset_sentinel_semantics(self) -> None:
        assert bool(UNSET) is False
        assert repr(UNSET) == "UNSET"


class TestValueObjects:
    def test_canvas_background_allows_colour_only(self) -> None:
        bg = CanvasBackground(color="#123456")
        assert bg.color == "#123456"
        assert bg.label == ""

    def test_theme_and_dark_mode_coercion_and_immutability(self) -> None:
        dark = DarkModeConfig(
            html_attrs={"html": {"data-scheme": "dark"}},
            css="dark.css",
            js="dark.js",
            canvas_background={"color": "#111111"},
        )
        assert dark.css == ("dark.css",)
        assert dark.js == ("dark.js",)
        assert dark.canvas_background == CanvasBackground(color="#111111")

        theme = Theme(
            label="Brand",
            css="brand.css",
            js=["a.js", "b.js"],
            html_attrs={"body": {"class": "brand"}},
            canvas_background={"label": "Cream", "color": "#fff8e7"},
            dark_mode=dark,
        )
        assert theme.css == ("brand.css",)
        assert theme.js == ("a.js", "b.js")
        assert theme.canvas_background == CanvasBackground(
            label="Cream", color="#fff8e7"
        )
        assert theme.supports_dark_mode is True
        assert theme.has_dark_mode_assets is True
        assert theme.has_external_assets is True
        with pytest.raises(dataclasses.FrozenInstanceError):
            theme.label = "Changed"  # type: ignore[misc]

    def test_doc_variant_config_freezes_kwargs(self) -> None:
        dv = DocVariantConfig(
            key="compact",
            name="compact",
            label="Compact",
            strategy=DocVariantStrategy.CUSTOM,
            kwargs={"size": "sm"},
        )
        assert isinstance(dv.kwargs, FrozenMapping)
        assert dv.kwargs == {"size": "sm"}


class TestSettingsDataclasses:
    def test_directory_settings_defaults_and_replace(self) -> None:
        directory = DirectorySettings()
        assert directory.prefix is None
        assert directory.flatten is None
        assert directory.label is None
        assert directory.promote_to_app is False
        assert directory.order is None
        assert directory.nav_order is None

        updated = directory.replace(
            prefix="cards",
            flatten=FlattenStrategy.ALL,
            label="Cards",
            promote_to_app=True,
            order=2,
            nav_order=["hero", NodeType.COMPONENT],
        )
        assert updated.prefix == "cards"
        assert updated.flatten is FlattenStrategy.ALL
        assert updated.order == 2
        assert updated.nav_order == ("hero", NodeType.COMPONENT)

    def test_app_settings_defaults_to_unset_and_validates_fields(self) -> None:
        empty = AppSettings()
        for field in dataclasses.fields(AppSettings):
            assert getattr(empty, field.name) is UNSET

        configured = AppSettings(
            label="Demo",
            order=1,
            nav_order=("overview", NodeType.FOLDER, NodeType.COMPONENT),
            prefix="demo",
            flatten=FlattenStrategy.ALL,
            short_names=False,
            themes=("default", "dark"),
            css="app.css",
            extra_css="override.css",
            js=["a.js"],
            extra_js=["b.js"],
            css_bundles=("main", ("extra", "ALT")),
            js_bundles=("main",),
            canvas_html_attrs={"body": {"class": "demo-body", "data-old": None}},
            directories={"cards": DirectorySettings(prefix="c")},
        )
        assert configured.css == ("app.css",)
        assert configured.extra_css == ("override.css",)
        assert configured.js == ("a.js",)
        assert configured.extra_js == ("b.js",)
        assert configured.themes == ("default", "dark")
        assert configured.nav_order == ("overview", NodeType.FOLDER, NodeType.COMPONENT)
        assert configured.replace(prefix="v2").prefix == "v2"

    def test_app_settings_rejects_empty_directory_key_and_bare_strings(self) -> None:
        with pytest.raises(ValueError, match="directories"):
            AppSettings(directories={"": DirectorySettings(prefix="ui")})
        with pytest.raises(TypeError, match="themes"):
            AppSettings(themes="dark")  # type: ignore[arg-type]
        with pytest.raises(TypeError, match="css_bundles"):
            AppSettings(css_bundles="main")  # type: ignore[arg-type]
        with pytest.raises(TypeError, match="js_bundles"):
            AppSettings(js_bundles="main")  # type: ignore[arg-type]

    def test_gallery_settings_defaults_and_nav_order_modes(self) -> None:
        gallery = GallerySettings()
        assert gallery.enabled is True
        assert gallery.is_public is True
        assert gallery.app_order == ()
        assert gallery.nav_order == DDS_DEFAULT_NAV_ORDER
        assert gallery.ui_themes == DDS_DEFAULT_UI_THEMES
        assert gallery.doc_variants == DDS_DEFAULT_DOC_VARIANTS

        alpha = gallery.replace(
            enabled=False,
            app_order=["foundations", "demo_components"],
            nav_order="alphabetical",
            extra_css="custom.css",
        )
        assert alpha.enabled is False
        assert alpha.app_order == ("foundations", "demo_components")
        assert alpha.nav_order == "alphabetical"
        assert alpha.extra_css == ("custom.css",)

    def test_design_system_settings_hydrates_theme_values_and_supports_replace(
        self,
    ) -> None:
        cfg = DesignSystemSettings(
            name="Acme",
            css="base.css",
            themes={
                "brand": Theme(label="Brand Theme"),
                "plain": Theme(),
            },
        )
        assert cfg.css == ("base.css",)
        assert cfg.themes["brand"].value == "brand"
        assert cfg.themes["brand"].label == "Brand Theme"
        assert cfg.themes["plain"].value == "plain"
        assert cfg.themes["plain"].label == "Plain"

        overridden = cfg.replace(
            name="Acme Prod",
            gallery=cfg.gallery.replace(enabled=False, is_public=False),
        )
        assert overridden.name == "Acme Prod"
        assert overridden.gallery.enabled is False
        assert overridden.gallery.is_public is False
        assert overridden.themes == cfg.themes

    def test_dds_default_constants_are_immutable(self) -> None:
        assert "default" in DDS_DEFAULT_THEMES
        assert "desert" in DDS_DEFAULT_UI_THEMES
        assert "light-grey" in DDS_DEFAULT_CANVAS_BACKGROUNDS
        assert "minimal" in DDS_DEFAULT_DOC_VARIANTS
        assert DDS_DEFAULT_NAV_ORDER == (
            NodeType.FOLDER,
            NodeType.COMPONENT,
            NodeType.DOCUMENT,
        )
        with pytest.raises(TypeError):
            DDS_DEFAULT_CANVAS_BACKGROUNDS["x"] = CanvasBackground(color="#000")  # type: ignore[index]
