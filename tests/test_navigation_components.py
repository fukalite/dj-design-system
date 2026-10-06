"""Tests for the Breadcrumb, NavTree and FolderListing built-ins.

Each is checked for parity with the legacy gallery template it replaces:
both are rendered from the same data and compared after parsing, ignoring
whitespace. The only allowed difference is Icon's own classes (and the
aria-hidden it always adds to decorative icons).
"""

from html.parser import HTMLParser

import pytest
from django.template import Context, Template
from django.template.loader import render_to_string

from dj_design_system.data import NavNode
from dj_design_system.gallery import Variant
from dj_design_system.services.media import FOUNDATION_CSS
from dj_design_system.services.navigation import build_navigation
from dj_design_system.services.registry import component_registry
from dj_design_system.types import NodeType
from tests.html_utils import css_homes, render, root, tags


class _Events(HTMLParser):
    def __init__(self):
        super().__init__()
        self.events: list = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = [
            c
            for c in (attrs.pop("class", "") or "").split()
            if not c.startswith("gallery-icon")
        ]
        if any(c.endswith("__icon") for c in classes):
            attrs.pop("aria-hidden", None)
        if classes:
            attrs["class"] = " ".join(sorted(classes))
        self.events.append(("start", tag, tuple(sorted(attrs.items()))))

    def handle_endtag(self, tag):
        self.events.append(("end", tag))

    def handle_data(self, data):
        if data.strip():
            self.events.append(("text", " ".join(data.split())))


def structure(html: str) -> list:
    parser = _Events()
    parser.feed(html)
    return parser.events


# ---------------------------------------------------------------------------
# Breadcrumb
# ---------------------------------------------------------------------------

CRUMBS = [
    {"label": "Gallery", "url": "/dds/"},
    {"label": "Demo Nav", "url": "/dds/demo_nav/"},
    {"label": "Elements", "url": "/dds/demo_nav/elements/"},
    {"label": "Icons", "url": "/dds/demo_nav/elements/icons/"},
    {"label": "Icon"},
]


class TestBreadcrumb:
    @pytest.mark.parametrize("count", [1, 2, 3, 5])
    def test_matches_legacy_template(self, count):
        crumbs = CRUMBS[: count - 1] + [CRUMBS[-1]]
        legacy = render_to_string(
            "dj_design_system/gallery/breadcrumb.html", {"breadcrumbs": crumbs}
        )
        html = render("{% dds__navigation__breadcrumb crumbs %}", crumbs=crumbs)
        assert structure(html) == structure(legacy)

    def test_collapses_long_paths_with_a_flyout(self):
        html = render("{% dds__navigation__breadcrumb crumbs %}", crumbs=CRUMBS)
        assert (
            "input",
            {
                "type": "checkbox",
                "class": "gallery-breadcrumb__toggle",
                "id": "bc-toggle",
                "aria-hidden": "true",
            },
        ) in tags(html)
        assert ("div", {"class": "gallery-breadcrumb__flyout"}) in tags(html)

    def test_renders_nothing_without_crumbs(self):
        assert render("{% dds__navigation__breadcrumb crumbs %}", crumbs=[]) == ""

    def test_escapes_labels(self):
        html = render(
            "{% dds__navigation__breadcrumb crumbs %}",
            crumbs=[{"label": "<b>x</b>", "url": "/"}, {"label": "y"}],
        )
        assert "<b>" not in html


# ---------------------------------------------------------------------------
# NavTree
# ---------------------------------------------------------------------------


def _legacy_nav(nav_tree, active_path, active_variant=None) -> str:
    return Template(
        '{% for app_node in nav_tree %}{% include "dj_design_system/gallery/navtree.html" with node=app_node depth=0 active_path=active_path active_variant=active_variant %}{% endfor %}'
    ).render(
        Context(
            {
                "nav_tree": nav_tree,
                "active_path": active_path,
                "active_variant": active_variant,
            }
        )
    )


def _nav(nav_tree, active_path="", active_variant=None) -> str:
    return render(
        "{% dds__navigation__nav_tree nodes active_path=active_path active_variant=active_variant %}",
        nodes=nav_tree,
        active_path=active_path,
        active_variant=active_variant,
    )


class TestNavTree:
    @pytest.mark.parametrize("active_path", ["", "cards", "elements/icon"])
    def test_matches_legacy_template(self, nav_tree, active_path):
        html = _nav(nav_tree, active_path)
        assert root(html) == ("nav", {"class": "gallery-nav", "id": "gallery-nav"})
        inner = html[html.index(">") + 1 : html.rindex("</nav>")]
        assert structure(inner) == structure(_legacy_nav(nav_tree, active_path))

    @pytest.mark.parametrize(
        "active_path, active_variant",
        [
            ("", None),
            ("alert", None),
            # A folder or document page's ?variant= string.
            ("alert", "critical"),
            # A component page passes the Variant itself.
            ("alert", Variant(name="critical")),
        ],
    )
    def test_matches_legacy_template_with_variants(self, active_path, active_variant):
        nav_tree = build_navigation()
        html = _nav(nav_tree, active_path, active_variant)
        inner = html[html.index(">") + 1 : html.rindex("</nav>")]
        legacy = _legacy_nav(nav_tree, active_path, active_variant)
        assert "gallery-nav__link--variant" in legacy
        assert structure(inner) == structure(legacy)

    def test_custom_icons_match_legacy_template(self):
        nodes = [
            {
                "type": "app",
                "label": "App",
                "url": "/app/",
                "children": [
                    {
                        "type": "component",
                        "label": "Svg",
                        "url": "/a/",
                        "icon": "<svg viewBox='0 0 10 10'></svg>",
                    },
                    {
                        "type": "component",
                        "label": "Url",
                        "url": "/b/",
                        "icon": "/static/i.svg",
                    },
                    {
                        "type": "document",
                        "label": "Class",
                        "url": "/c/",
                        "icon": "fa fa-book",
                    },
                ],
            }
        ]
        legacy_nodes = [
            NavNode(
                label="App",
                slug="app",
                node_type=NodeType.APP,
                url="/app/",
                children=[
                    NavNode(
                        label="Class",
                        slug="c",
                        node_type=NodeType.FOLDER,
                        url="/c/",
                        icon=icon,
                    )
                    for icon in (
                        "<svg viewBox='0 0 10 10'></svg>",
                        "/static/i.svg",
                        "fa fa-book",
                    )
                ],
            )
        ]
        html = _nav(nodes)
        legacy = _legacy_nav(legacy_nodes, "")

        def custom_icons(markup):
            # Attribute values are compared ignoring whitespace (the legacy
            # template wraps its style attribute).
            return [
                {k: " ".join(v.split()) for k, v in a.items()}
                for t, a in tags(markup)
                if "gallery-nav__icon--custom" in a.get("class", "")
            ]

        assert custom_icons(html) == custom_icons(legacy)
        assert "<svg viewBox='0 0 10 10'></svg>" in html

    def test_uses_icon_component(self, nav_tree):
        html = _nav(nav_tree)
        icon_classes = [
            a["class"]
            for t, a in tags(html)
            if "gallery-nav__icon" in a.get("class", "")
        ]
        assert icon_classes
        assert all("gallery-icon gallery-icon--mask" in c for c in icon_classes)

    def test_accepts_plain_dicts(self):
        nodes = [
            {
                "type": "app",
                "label": "Demo",
                "url": "/dds/demo/",
                "children": [
                    {
                        "type": "folder",
                        "label": "Cards",
                        "url": "/dds/demo/cards/",
                        "active_path": "cards",
                        "children": [
                            {
                                "type": "component",
                                "label": "Hero",
                                "url": "/dds/demo/cards/hero/",
                                "active_path": "cards/hero",
                            },
                        ],
                    },
                    {
                        "type": "document",
                        "label": "Guide",
                        "url": "/dds/demo/guide/",
                        "active_path": "guide",
                    },
                ],
            }
        ]
        html = _nav(nodes, "cards/hero")
        assert ("details", {"class": "gallery-nav__folder", "open": None}) in tags(html)
        assert "Guide </a>" in " ".join(html.split())
        active = [
            a
            for t, a in tags(html)
            if "gallery-nav__link--active" in a.get("class", "")
        ]
        assert [a["href"] for a in active] == ["/dds/demo/cards/hero/"]

    def test_handles_a_deep_tree(self):
        leaf = {
            "type": "component",
            "label": "Leaf",
            "url": "/leaf/",
            "active_path": "x",
        }
        node = leaf
        for depth in range(30):
            node = {
                "type": "folder",
                "label": f"F{depth}",
                "url": f"/f{depth}/",
                "active_path": f"f{depth}",
                "children": [node],
            }
        html = _nav([{"type": "app", "label": "App", "url": "/", "children": [node]}])
        assert html.count("<details") == 30
        depths = [int(a["data-depth"]) for t, a in tags(html) if "data-depth" in a]
        assert depths == list(range(1, 32))


# ---------------------------------------------------------------------------
# FolderListing
# ---------------------------------------------------------------------------


def _children(nav_tree) -> list[NavNode]:
    app = nav_tree[0]
    return app.children


class TestFolderListing:
    def test_matches_legacy_markup(self, nav_tree):
        children = _children(nav_tree)
        legacy = render_to_string(
            "dj_design_system/gallery/folder.html",
            {"children": children, "folder_label": "X"},
        )
        legacy = legacy[legacy.index('<div class="gallery-folder-contents">') :]
        legacy = legacy[: legacy.index("</ul>") + len("</ul>")] + "</div>"
        html = render("{% dds__navigation__folder_listing items %}", items=children)
        assert structure(html) == structure(legacy)

    def test_icons_by_type(self):
        items = [
            {
                "type": "folder",
                "label": "F",
                "url": "/f/",
                "children": [{"type": "component"}],
            },
            {"type": "component", "label": "C", "url": "/c/"},
            {"type": "document", "label": "D", "url": "/d/"},
        ]
        html = render("{% dds__navigation__folder_listing items %}", items=items)
        classes = [a["class"] for t, a in tags(html) if t == "span"]
        assert [c.split()[-1] for c in classes] == [
            "gallery-folder-list__icon--folder",
            "gallery-folder-list__icon--component",
            "gallery-folder-list__icon--doc",
        ]

    def test_unknown_type_has_no_icon(self):
        html = render(
            "{% dds__navigation__folder_listing items %}",
            items=[{"type": "app", "label": "A", "url": "/a/"}],
        )
        assert [t for t, _ in tags(html) if t == "span"] == []

    def test_empty(self):
        html = render("{% dds__navigation__folder_listing items %}", items=[])
        assert tags(html) == [("p", {})]
        assert "This folder is empty." in html


class TestRegistrationAndCss:
    @pytest.mark.parametrize("name", ["breadcrumb", "nav_tree", "folder_listing"])
    def test_internal_with_dds_name(self, name):
        info = component_registry.get_by_name(name, app_label="dj_design_system")
        assert info.is_internal
        assert info.qualified_name == f"dds__navigation__{name}"
        assert info.media.css[0] == FOUNDATION_CSS

    @pytest.mark.parametrize("name", ["nav_tree", "folder_listing"])
    def test_icon_css_loads_first(self, name):
        css = component_registry.get_by_name(
            name, app_label="dj_design_system"
        ).media.css
        assert css.index("dj_design_system/ui/primitives/icon.css") < css.index(
            f"dj_design_system/ui/navigation/{name}.css"
        )

    @pytest.mark.parametrize(
        ("selector", "owner"),
        [
            (".gallery-breadcrumb__flyout {", "breadcrumb.css"),
            (".gallery-breadcrumb__ellipsis {", "breadcrumb.css"),
            (".gallery-nav {", "nav_tree.css"),
            (".gallery-nav__link {", "nav_tree.css"),
            (".gallery-nav__icon {", "nav_tree.css"),
            ('.gallery-nav__link[data-depth="3"] {', "nav_tree.css"),
            (".gallery-folder-list {", "folder_listing.css"),
            (".gallery-folder-list__icon {", "folder_listing.css"),
            (":where(.gallery-folder-contents) h2 {", "folder_listing.css"),
        ],
    )
    def test_rule_lives_only_in_owner(self, selector, owner):
        assert css_homes(selector) == [f"ui/navigation/{owner}"]
