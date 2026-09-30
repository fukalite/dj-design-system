import pytest

from dj_design_system.gallery import GalleryConfig, Variant


class TestVariant:
    def test_default_values(self):
        v = Variant(name="primary")
        assert v.name == "primary"
        assert v.label == "Primary"
        assert v.description is None
        assert v.kwargs == {}
        assert v.positional_args == ()
        assert v.canvas_template is None
        assert v.extra_context == {}
        assert v.icon is None
        assert v.theme is None
        assert v.show_in_nav is True

    def test_default_variants_hidden_from_nav_by_default(self):
        v_basic = Variant(name="basic")
        assert v_basic.show_in_nav is False

        v_maximal = Variant(name="maximal")
        assert v_maximal.show_in_nav is False

    def test_explicit_show_in_nav_override(self):
        v_basic = Variant(name="basic", show_in_nav=True)
        assert v_basic.show_in_nav is True

        v_custom = Variant(name="custom", show_in_nav=False)
        assert v_custom.show_in_nav is False

    def test_label_customization(self):
        v = Variant(name="icon_only", label="Icon Only Button")
        assert v.label == "Icon Only Button"

    def test_label_slug_formatting(self):
        v1 = Variant(name="danger_action")
        assert v1.label == "Danger Action"

        v2 = Variant(name="dark-mode")
        assert v2.label == "Dark Mode"

    def test_positional_args_as_tuple(self):
        v = Variant(name="test", positional_args=["arg1", "arg2"])
        assert v.positional_args == ("arg1", "arg2")

    def test_equality_with_string_returns_false(self):
        v = Variant(name="primary")
        assert (v == "primary") is False
        assert (v != "primary") is True
        assert v.__eq__("primary") is NotImplemented
        assert v.__eq__(123) is NotImplemented

    def test_equality_with_variant(self):
        v1 = Variant(name="primary", label="Primary")
        v2 = Variant(name="primary", label="Primary")
        assert v1 == v2
        assert (v1 == Variant(name="secondary")) is False


class TestGalleryConfig:
    def test_default_values(self):
        cfg = GalleryConfig()
        assert cfg.hidden is False
        assert cfg.icon is None
        assert cfg.theme is None
        assert cfg.group is None
        assert cfg.order == 0
        assert cfg.canvas_template is None
        assert cfg.extra_context == {}
        assert cfg.param_defaults == {}
        assert cfg.variants == []

    def test_explicit_properties(self):
        cfg = GalleryConfig(
            hidden=True,
            icon="heroicons:sparkles",
            theme="dark",
            group="Elements",
            order=10,
            canvas_template="<div class='wrap'>{{ component }}</div>",
            extra_context={"key": "val"},
            param_defaults={"size": "large"},
        )
        assert cfg.hidden is True
        assert cfg.icon == "heroicons:sparkles"
        assert cfg.theme == "dark"
        assert cfg.group == "Elements"
        assert cfg.order == 10
        assert cfg.canvas_template == "<div class='wrap'>{{ component }}</div>"
        assert cfg.extra_context == {"key": "val"}
        assert cfg.param_defaults == {"size": "large"}

    def test_variants_initialization_with_instances(self):
        v1 = Variant(name="basic", kwargs={"label": "Click"})
        v2 = Variant(name="danger", kwargs={"label": "Delete", "variant": "danger"})
        cfg = GalleryConfig(variants=[v1, v2])

        assert len(cfg.variants) == 2
        assert cfg.variants[0] == v1
        assert cfg.variants[1] == v2
        assert cfg.get_variant("danger") == v2
        assert cfg.get_variant("unknown") is None

    def test_variants_direct_dict_initialization_raises_type_error(self):
        """GalleryConfig constructor strictly requires Variant instances and rejects dicts."""
        with pytest.raises(TypeError, match="must contain only Variant instances"):
            GalleryConfig(
                variants=[
                    {"name": "basic", "kwargs": {"label": "Click"}},
                ]
            )

        with pytest.raises(TypeError, match="must be a list of Variant instances"):
            GalleryConfig(
                variants={
                    "basic": {"kwargs": {"label": "Click"}},
                }
            )

    def test_duplicate_variant_names_raises_error(self):
        with pytest.raises(ValueError, match="Duplicate variant name"):
            GalleryConfig(
                variants=[
                    Variant(name="danger"),
                    Variant(name="danger"),
                ]
            )

    def test_variant_from_dict(self):
        """Variant.from_dict instantiates Variant with mapping and optional name."""
        v1 = Variant.from_dict(
            {"name": "outline", "label": "Outline Btn", "kwargs": {"outline": True}}
        )
        assert v1.name == "outline"
        assert v1.label == "Outline Btn"
        assert v1.kwargs == {"outline": True}

        v2 = Variant.from_dict({"kwargs": {"size": "sm"}}, name="small")
        assert v2.name == "small"
        assert v2.kwargs == {"size": "sm"}

    def test_gallery_config_from_dict(self):
        """GalleryConfig.from_dict unpacks dict with nested variant mappings and fields."""
        data = {
            "hidden": True,
            "order": 10,
            "icon": "mdi:palette",
            "theme": "dark",
            "param_defaults": {"size": "md"},
            "extra_context": {"doc_url": "https://example.com"},
            "variants": {
                "primary": {"kwargs": {"color": "blue"}},
                "secondary": {"kwargs": {"color": "gray"}, "label": "Secondary Option"},
            },
        }
        cfg = GalleryConfig.from_dict(data)
        assert cfg.hidden is True
        assert cfg.order == 10
        assert cfg.icon == "mdi:palette"
        assert cfg.theme == "dark"
        assert cfg.param_defaults == {"size": "md"}
        assert cfg.extra_context == {"doc_url": "https://example.com"}
        assert len(cfg.variants) == 2
        assert cfg.variants[0].name == "primary"
        assert cfg.variants[0].kwargs == {"color": "blue"}
        assert cfg.variants[1].name == "secondary"
        assert cfg.variants[1].label == "Secondary Option"

    def test_gallery_config_from_dict_list_variants(self):
        """GalleryConfig.from_dict handles variants as list of dicts."""
        data = {
            "variants": [
                {"name": "v1", "kwargs": {"a": 1}},
                Variant(name="v2", kwargs={"b": 2}),
            ]
        }
        cfg = GalleryConfig.from_dict(data)
        assert len(cfg.variants) == 2
        assert cfg.variants[0].name == "v1"
        assert cfg.variants[1].name == "v2"
