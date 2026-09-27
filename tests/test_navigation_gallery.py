"""Unit tests for GalleryConfig navigation integration.

Tests hidden filtering, icon propagation, order sorting, group sub-folders,
and variant child nodes in the navigation tree.
"""

from dj_design_system.data import ComponentInfo
from dj_design_system.gallery import GalleryConfig, Variant
from dj_design_system.services.navigation import (
    NodeType,
    _build_navigation,
    build_search_index,
)
from tests.conftest import make_info


def make_info_with_config(
    name: str,
    config: GalleryConfig,
    app_label: str = "test_app",
    relative_path: str = "",
) -> ComponentInfo:
    """Helper to create a ComponentInfo with an attached GalleryConfig."""
    info = make_info(name, app_label=app_label, relative_path=relative_path)
    # Assign to __dict__ to bypass or populate the cached_property
    info.__dict__["gallery_config"] = config
    return info


class TestNavigationHidden:
    """Tests for hidden components in navigation."""

    def test_hidden_component_is_excluded_from_navigation(self):
        visible = make_info_with_config("visible_btn", GalleryConfig())
        hidden = make_info_with_config("hidden_btn", GalleryConfig(hidden=True))

        tree = _build_navigation([visible, hidden])
        assert len(tree) == 1
        app_node = tree[0]
        child_slugs = [c.slug for c in app_node.children]
        assert "visible_btn" in child_slugs
        assert "hidden_btn" not in child_slugs

    def test_all_hidden_app_omits_app_node(self):
        hidden = make_info_with_config("secret_btn", GalleryConfig(hidden=True))
        tree = _build_navigation([hidden])
        assert len(tree) == 0

    def test_hidden_component_not_in_search_index(self):
        visible = make_info_with_config("visible_btn", GalleryConfig())
        hidden = make_info_with_config("hidden_btn", GalleryConfig(hidden=True))

        tree = _build_navigation([visible, hidden])
        index = build_search_index(tree)
        labels = [entry["label"] for entry in index]
        assert "Visible btn" in labels
        assert "Hidden btn" not in labels


class TestNavigationIcon:
    """Tests for icon propagation to NavNode."""

    def test_icon_propagated_to_nav_node(self):
        info = make_info_with_config(
            "button",
            GalleryConfig(icon="mdi:button"),
        )
        tree = _build_navigation([info])
        app_node = tree[0]
        btn_node = app_node.children[0]
        assert btn_node.icon == "mdi:button"

    def test_default_icon_is_none(self):
        info = make_info_with_config("button", GalleryConfig())
        tree = _build_navigation([info])
        btn_node = tree[0].children[0]
        assert btn_node.icon is None

    def test_icon_preserved_on_collapsed_folder_upgrade(self):
        # Component with relative_path="button", collapsing with folder "button"
        info = make_info_with_config(
            "button",
            GalleryConfig(icon="package-icon"),
            relative_path="button",
        )
        tree = _build_navigation([info])
        btn_node = tree[0].children[0]
        assert btn_node.is_component
        assert btn_node.icon == "package-icon"


class TestNavigationOrder:
    """Tests for explicit ordering in navigation."""

    def test_order_sorts_components(self):
        # beta has order -5, gamma has order 0, alpha has order 10
        alpha = make_info_with_config("alpha", GalleryConfig(order=10))
        beta = make_info_with_config("beta", GalleryConfig(order=-5))
        gamma = make_info_with_config("gamma", GalleryConfig(order=0))

        tree = _build_navigation([alpha, beta, gamma])
        app_node = tree[0]
        child_slugs = [c.slug for c in app_node.children]
        assert child_slugs == ["beta", "gamma", "alpha"]

    def test_order_ties_broken_alphabetically(self):
        c1 = make_info_with_config("zebra", GalleryConfig(order=1))
        c2 = make_info_with_config("aardvark", GalleryConfig(order=1))
        c3 = make_info_with_config("bear", GalleryConfig(order=1))

        tree = _build_navigation([c1, c2, c3])
        app_node = tree[0]
        child_slugs = [c.slug for c in app_node.children]
        assert child_slugs == ["aardvark", "bear", "zebra"]


class TestNavigationGroup:
    """Tests for group sub-folders in navigation."""

    def test_group_creates_subfolder(self):
        info = make_info_with_config(
            "button",
            GalleryConfig(group="Actions"),
        )
        tree = _build_navigation([info])
        app_node = tree[0]
        assert len(app_node.children) == 1
        folder_node = app_node.children[0]
        assert folder_node.node_type == NodeType.FOLDER
        assert folder_node.slug == "actions"
        assert folder_node.label == "Actions"
        assert len(folder_node.children) == 1
        assert folder_node.children[0].slug == "button"

    def test_multiple_components_share_same_group(self):
        btn = make_info_with_config("button", GalleryConfig(group="Actions"))
        link = make_info_with_config("link", GalleryConfig(group="Actions"))
        input_box = make_info_with_config("input", GalleryConfig(group="Forms"))

        tree = _build_navigation([btn, link, input_box])
        app_node = tree[0]
        folder_slugs = [c.slug for c in app_node.children]
        assert folder_slugs == ["actions", "forms"]

        actions_folder = app_node.children[0]
        assert [c.slug for c in actions_folder.children] == ["button", "link"]

        forms_folder = app_node.children[1]
        assert [c.slug for c in forms_folder.children] == ["input"]

    def test_nested_group_creates_nested_folders(self):
        info = make_info_with_config(
            "text_input",
            GalleryConfig(group="Forms/Inputs"),
        )
        tree = _build_navigation([info])
        app_node = tree[0]
        forms_folder = app_node.children[0]
        assert forms_folder.slug == "forms"
        assert forms_folder.label == "Forms"

        inputs_folder = forms_folder.children[0]
        assert inputs_folder.slug == "inputs"
        assert inputs_folder.label == "Inputs"
        assert inputs_folder.children[0].slug == "text_input"


class TestNavigationVariants:
    """Tests for variant child nodes in navigation."""

    def test_custom_variants_appear_as_child_nodes(self):
        config = GalleryConfig(
            variants=[
                Variant(name="primary", label="Primary Button"),
                Variant(name="danger", label="Danger Button", icon="alert-icon"),
            ]
        )
        info = make_info_with_config("button", config)

        tree = _build_navigation([info])
        app_node = tree[0]
        btn_node = app_node.children[0]
        assert btn_node.is_component
        assert btn_node.has_children

        variant_nodes = btn_node.children
        assert len(variant_nodes) == 2

        primary_node = variant_nodes[0]
        assert primary_node.node_type == NodeType.VARIANT
        assert primary_node.is_variant
        assert primary_node.slug == "primary"
        assert primary_node.label == "Primary Button"
        assert primary_node.variant.name == "primary"

        danger_node = variant_nodes[1]
        assert danger_node.node_type == NodeType.VARIANT
        assert danger_node.slug == "danger"
        assert danger_node.label == "Danger Button"
        assert danger_node.icon == "alert-icon"

    def test_default_variants_hidden_by_default(self):
        config = GalleryConfig(
            variants=[
                Variant(name="basic"),
                Variant(name="maximal"),
                Variant(name="custom"),
            ]
        )
        info = make_info_with_config("button", config)

        tree = _build_navigation([info])
        btn_node = tree[0].children[0]
        # Only "custom" should be in nav because basic/maximal have show_in_nav=False
        assert len(btn_node.children) == 1
        assert btn_node.children[0].slug == "custom"

    def test_default_variant_included_if_show_in_nav_explicitly_true(self):
        config = GalleryConfig(
            variants=[
                Variant(name="basic", show_in_nav=True),
            ]
        )
        info = make_info_with_config("button", config)

        tree = _build_navigation([info])
        btn_node = tree[0].children[0]
        assert len(btn_node.children) == 1
        assert btn_node.children[0].slug == "basic"

    def test_variant_node_url_contains_query_param(self):
        config = GalleryConfig(
            variants=[
                Variant(name="primary"),
            ]
        )
        info = make_info_with_config("button", config)

        tree = _build_navigation([info])
        btn_node = tree[0].children[0]
        variant_node = btn_node.children[0]

        assert variant_node.url.endswith("?variant=primary")
        assert "/test_app/button/" in variant_node.url

    def test_variant_nodes_indexed_in_search(self):
        config = GalleryConfig(
            variants=[
                Variant(
                    name="danger",
                    label="Danger Action",
                    description="Use for destructive operations.",
                ),
            ]
        )
        info = make_info_with_config("button", config)

        tree = _build_navigation([info])
        index = build_search_index(tree)

        variant_entries = [e for e in index if e["type"] == "variant"]
        assert len(variant_entries) == 1
        entry = variant_entries[0]
        assert entry["label"] == "Danger Action"
        assert "destructive" in entry["content"]
        assert "?variant=danger" in entry["url"]
        assert "Test app / Button" in entry["breadcrumb"]


class TestNavTreeTemplate:
    """Tests for HTML rendering of the sidebar tree via navtree.html."""

    def test_custom_svg_icon_renders(self):
        from django.template.loader import render_to_string

        svg_icon = '<svg viewBox="0 0 24 24"><path d="M0 0h24v24H0z"/></svg>'
        info = make_info_with_config("button", GalleryConfig(icon=svg_icon))
        tree = _build_navigation([info])

        html = render_to_string(
            "dj_design_system/gallery/navtree.html",
            {"node": tree[0], "depth": 0, "active_path": "", "active_variant": ""},
        )
        assert 'class="gallery-nav__icon gallery-nav__icon--custom"' in html
        assert svg_icon in html

    def test_custom_class_icon_renders(self):
        from django.template.loader import render_to_string

        info = make_info_with_config("button", GalleryConfig(icon="mdi-star"))
        tree = _build_navigation([info])

        html = render_to_string(
            "dj_design_system/gallery/navtree.html",
            {"node": tree[0], "depth": 0, "active_path": "", "active_variant": ""},
        )
        assert "gallery-nav__icon--custom mdi-star" in html

    def test_custom_mask_icon_renders(self):
        from django.template.loader import render_to_string

        info = make_info_with_config(
            "button", GalleryConfig(icon="/static/icons/btn.svg")
        )
        tree = _build_navigation([info])

        html = render_to_string(
            "dj_design_system/gallery/navtree.html",
            {"node": tree[0], "depth": 0, "active_path": "", "active_variant": ""},
        )
        assert "url('/static/icons/btn.svg')" in html

    def test_variant_child_links_render(self):
        from django.template.loader import render_to_string

        config = GalleryConfig(
            variants=[
                Variant(name="primary", label="Primary Button"),
                Variant(name="danger", label="Danger Button"),
            ]
        )
        info = make_info_with_config("button", config)
        tree = _build_navigation([info])

        html = render_to_string(
            "dj_design_system/gallery/navtree.html",
            {"node": tree[0], "depth": 0, "active_path": "", "active_variant": ""},
        )
        assert "gallery-nav__link--variant" in html
        assert "?variant=primary" in html
        assert "?variant=danger" in html
        assert "Primary Button" in html
        assert "Danger Button" in html

    def test_variant_active_state(self):
        from django.template.loader import render_to_string

        config = GalleryConfig(
            variants=[
                Variant(name="primary", label="Primary Button"),
                Variant(name="danger", label="Danger Button"),
            ]
        )
        info = make_info_with_config("button", config)
        tree = _build_navigation([info])

        # Active variant is "danger"
        html = render_to_string(
            "dj_design_system/gallery/navtree.html",
            {
                "node": tree[0],
                "depth": 0,
                "active_path": "test_app/button",
                "active_variant": "danger",
            },
        )
        # Danger variant should have active class
        assert (
            'class="gallery-nav__link gallery-nav__link--variant gallery-nav__link--active"'
            in html
            or "gallery-nav__link--active" in html
        )
        # Parent details should be open
        assert "<details class=\"gallery-nav__folder\"\n             open>" in html or "<details class=\"gallery-nav__folder\" open>" in html or " open>" in html

