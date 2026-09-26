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

    def test_variants_initialization_with_dicts(self):
        cfg = GalleryConfig(
            variants=[
                {"name": "basic", "kwargs": {"label": "Click"}},
                {
                    "name": "danger",
                    "label": "Destructive",
                    "kwargs": {"variant": "danger"},
                },
            ]
        )
        assert len(cfg.variants) == 2
        assert isinstance(cfg.variants[0], Variant)
        assert cfg.variants[0].name == "basic"
        assert cfg.variants[0].label == "Basic"
        assert cfg.variants[1].name == "danger"
        assert cfg.variants[1].label == "Destructive"
        assert cfg.variants[1].kwargs == {"variant": "danger"}

    def test_variants_dict_mapping_initialization(self):
        cfg = GalleryConfig(
            variants={
                "basic": {"kwargs": {"label": "Click"}},
                "danger": {"kwargs": {"variant": "danger"}, "label": "Danger Action"},
            }
        )
        assert len(cfg.variants) == 2
        assert cfg.variants[0].name == "basic"
        assert cfg.variants[1].name == "danger"
        assert cfg.variants[1].label == "Danger Action"

    def test_duplicate_variant_names_raises_error(self):
        with pytest.raises(ValueError, match="Duplicate variant name"):
            GalleryConfig(
                variants=[
                    Variant(name="danger"),
                    Variant(name="danger"),
                ]
            )

    def test_invalid_order_raises_error(self):
        with pytest.raises(TypeError, match="order must be an integer"):
            GalleryConfig(order="10")  # type: ignore

    def test_invalid_hidden_raises_error(self):
        with pytest.raises(TypeError, match="hidden must be a boolean"):
            GalleryConfig(hidden="true")  # type: ignore
