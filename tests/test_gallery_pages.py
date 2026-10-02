"""The gallery's shell and simple pages are built from built-in components.

The rendered pages don't change (``test_gallery_template_contract.py`` and
the visual baseline check that), so these check each template's source: it
uses the component tags, and the markup they replaced is gone. Where a
component renders something the legacy markup didn't (``Icon``'s classes),
the rendered page is checked too.
"""

import re
from pathlib import Path

import pytest
from django.template import Context, Template
from django.template.loader import render_to_string

import dj_design_system
from dj_design_system.components.navigation.nav_tree import NavTree
from tests.html_utils import render
from tests.test_navigation_components import CRUMBS
from tests.test_views import _collect_all_nodes, _get_nav_tree


TEMPLATES = Path(dj_design_system.__file__).parent / "templates" / "dj_design_system"


def source(name: str) -> str:
    return (TEMPLATES / "gallery" / name).read_text()


def _url(node_type: str) -> str:
    return next(
        n.url
        for n in _collect_all_nodes(_get_nav_tree())
        if n.node_type.value == node_type
    )


# ---------------------------------------------------------------------------
# base.html
# ---------------------------------------------------------------------------


class TestBase:
    @pytest.mark.parametrize(
        "tag",
        [
            "dds__layout__gallery_shell",
            "dds__layout__sidebar",
            "dds__navigation__search_box",
            "dds__navigation__nav_tree",
            "dds__layout__toolbar",
            "dds__navigation__theme_select",
        ],
    )
    def test_uses_component(self, tag):
        assert "{% " + tag in source("base.html")

    @pytest.mark.parametrize(
        "legacy",
        [
            'class="gallery"',
            'class="gallery-hamburger"',
            'class="gallery-sidebar"',
            'id="gallery-search-input"',
            "navtree.html",
            'class="gallery-toolbar"',
            'id="gallery-global-theme-select"',
            'class="gallery-content-area"',
        ],
    )
    def test_legacy_markup_is_gone(self, legacy):
        assert legacy not in source("base.html")

    def test_nav_icons_come_from_icon(self, client):
        page = client.get("/dds/").content.decode()
        nav = page[page.index('id="gallery-nav"') : page.index("</nav>")]
        assert "gallery-icon gallery-icon--mask" in nav

    def test_code_highlight_is_linked_again_last(self, client):
        # The built-ins load it before layout/page.css, whose .gallery-docs pre
        # rules would override it; linking it again keeps it last.
        page = client.get("/dds/").content.decode()
        highlight = "ui/primitives/code_highlight.css"
        assert page.count(highlight) == 2
        assert page.index("ui/layout/page.css") < page.rindex(highlight)

    def test_only_legacy_stylesheets_are_hard_coded(self):
        # gallery.css goes in phase 4, once its last rules have owners; the
        # second code_highlight.css link goes once built-in CSS order allows.
        links = re.findall(r"<link[^>]*>", source("base.html"), flags=re.S)
        assert len(links) == 2
        assert "dj_design_system/gallery.css" in links[0]
        assert "ui/primitives/code_highlight.css" in links[1]


# ---------------------------------------------------------------------------
# Simple pages
# ---------------------------------------------------------------------------


class TestIndex:
    def test_uses_page_and_snapshot_notice(self):
        index = source("index.html")
        assert "{% dds__layout__page" in index
        assert "{% dds__primitives__notice snapshot=True" in index
        assert 'class="gallery-page"' not in index
        assert 'id="static-snapshot-notice"' not in index


class TestFolder:
    def test_uses_page_listing_and_hint(self):
        folder = source("folder.html")
        assert "{% dds__layout__page" in folder
        assert "{% dds__navigation__folder_listing" in folder
        assert '{% dds__primitives__notice variant="hint"' in folder
        for legacy in [
            'class="gallery-page"',
            "gallery-folder-list",
            "gallery-debug-hint",
        ]:
            assert legacy not in folder
        assert "breadcrumb.html" not in folder

    def test_listing_icons_come_from_icon(self, client):
        page = client.get(_url("folder")).content.decode()
        listing = page[page.index('class="gallery-folder-list"') :]
        assert "gallery-icon gallery-icon--mask" in listing


class TestDocumentation:
    def test_uses_page_and_prose(self):
        doc = source("documentation.html")
        assert "{% dds__layout__page" in doc
        assert "{% dds__layout__prose" in doc
        for legacy in ['class="gallery-page"', 'class="gallery-markdown"']:
            assert legacy not in doc
        assert "breadcrumb.html" not in doc

    def test_renders(self, client):
        response = client.get(_url("document"))
        assert response.status_code == 200
        assert 'class="gallery-markdown"' in response.content.decode()


# ---------------------------------------------------------------------------
# Legacy partials become thin wrappers
# ---------------------------------------------------------------------------


class TestLegacyPartialWrappers:
    def test_breadcrumb_renders_the_component(self):
        assert "{% dds__navigation__breadcrumb" in source("breadcrumb.html")
        legacy = render_to_string(
            "dj_design_system/gallery/breadcrumb.html", {"breadcrumbs": CRUMBS}
        )
        assert legacy.strip() == render(
            "{% dds__navigation__breadcrumb crumbs %}", crumbs=CRUMBS
        )

    @pytest.mark.parametrize("active_path", ["", "demo_nav/elements/icon"])
    def test_navtree_renders_the_components_node(self, nav_tree, active_path):
        assert "gallery-nav__group" not in source("navtree.html")
        legacy = Template(
            "{% for app_node in nav_tree %}"
            '{% include "dj_design_system/gallery/navtree.html"'
            " with node=app_node depth=0 %}{% endfor %}"
        ).render(Context({"nav_tree": nav_tree, "active_path": active_path}))
        tree = NavTree(nodes=nav_tree, active_path=active_path).render()
        inner = tree[tree.index(">") + 1 : tree.rindex("</nav>")]
        assert "".join(legacy.split()) == "".join(inner.split())
