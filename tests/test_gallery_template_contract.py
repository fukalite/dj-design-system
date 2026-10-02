"""The gallery templates' public contract, pinned before track 5 rewrites them.

Consumers extend ``gallery/base.html`` and override its blocks, include the
legacy partials, and script against element IDs. The rewrite into built-in
components must keep all three working:

- **Blocks:** every block keeps its name and its place in the page.
- **Element IDs:** each kind of page keeps the IDs it renders today.
- **Legacy partials:** ``breadcrumb.html``, ``navtree.html``, ``toolbar.html``
  and ``canvas_widget.html`` keep rendering what they render today. Their
  output is compared, after parsing, with snapshots taken from the legacy
  templates in ``tests/legacy_partials/``. The allowed differences are the
  ones the built-in components bring: ``Icon``'s classes and its
  ``aria-hidden``/``focusable``.

Set ``UPDATE_LEGACY_PARTIALS=1`` to rewrite the snapshots. That is only for
recording them; the point of the tests is that they don't change.
"""

import os
import re
from html.parser import HTMLParser
from pathlib import Path

import pytest
from django.template import Context, Template
from django.template.loader import render_to_string
from django.test import RequestFactory, override_settings

from dj_design_system.gallery import Variant
from dj_design_system.services.navigation import build_navigation
from dj_design_system.views import get_base_context
from tests.test_canvas_docs_components import widget_context
from tests.test_navigation_components import CRUMBS
from tests.test_sandbox_toolbar_components import ACTIVE_BG, BACKGROUNDS
from tests.test_views import _collect_all_nodes, _get_nav_tree


SNAPSHOTS = Path(__file__).parent / "legacy_partials"


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
        if tag == "svg" or any(c.endswith("__icon") for c in classes):
            attrs.pop("aria-hidden", None)
            attrs.pop("focusable", None)
        if classes:
            attrs["class"] = " ".join(sorted(classes))
        self.events.append(("start", tag, tuple(sorted(attrs.items()))))

    def handle_endtag(self, tag):
        self.events.append(("end", tag))

    def handle_data(self, data):
        if data.strip():
            self.events.append(("text", " ".join(data.split())))


def structure(markup: str) -> list:
    parser = _Events()
    parser.feed(markup)
    return parser.events


def _matches_snapshot(name: str, markup: str) -> None:
    path = SNAPSHOTS / f"{name}.html"
    if os.environ.get("UPDATE_LEGACY_PARTIALS"):
        path.parent.mkdir(exist_ok=True)
        path.write_text(markup.strip() + "\n")
    assert structure(markup) == structure(path.read_text()), name


# ---------------------------------------------------------------------------
# Template blocks
# ---------------------------------------------------------------------------

# Marks every block's content, in page order.
BLOCKS = ["title", "extra_css", "breadcrumb", "toolbar_actions", "content", "extra_js"]


def _extend_base(overrides: dict[str, str]) -> str:
    request = RequestFactory().get("/dds/")
    source = '{% extends "dj_design_system/gallery/base.html" %}' + "".join(
        f"{{% block {name} %}}{body}{{% endblock %}}"
        for name, body in overrides.items()
    )
    return Template(source).render(Context(get_base_context(request)))


class TestBaseBlocks:
    def test_blocks_render_in_place(self):
        page = _extend_base({name: f"@{name}@" for name in BLOCKS})
        positions = [page.index(f"@{name}@") for name in BLOCKS]
        assert positions == sorted(positions)
        head, body = page.split("</head>")
        assert re.search(r"<title>@title@</title>", head)
        assert "@extra_css@" in head
        assert body.index('class="gallery-toolbar"') < body.index("@breadcrumb@")
        assert body.index("@toolbar_actions@") < body.index("@content@")
        # extra_js comes after the gallery's own scripts, at the end of <body>.
        assert body.rindex("<script") < body.index("@extra_js@")
        assert body.index("@extra_js@") < body.index("</body>")

    def test_content_sits_in_the_content_area(self):
        page = _extend_base({"content": "@content@"})
        area = page.index('class="gallery-content-area"')
        assert area < page.index("@content@") < page.index("</main>")

    def test_toolbar_block_replaces_the_whole_toolbar(self):
        page = _extend_base({"toolbar": "@toolbar@", "breadcrumb": "@breadcrumb@"})
        assert "@toolbar@" in page
        assert "@breadcrumb@" not in page
        assert 'class="gallery-toolbar"' not in page


# ---------------------------------------------------------------------------
# Element IDs
# ---------------------------------------------------------------------------

SHELL_IDS = {
    "gallery-nav",
    "gallery-search-index",
    "gallery-search-input",
    "gallery-search-results",
    "gallery-sidebar-toggle",
}
PAGE_IDS = {
    "index": SHELL_IDS | {"static-snapshot-notice"},
    "app": SHELL_IDS | {"bc-toggle"},
    "folder": SHELL_IDS | {"bc-toggle"},
    "document": SHELL_IDS | {"bc-toggle"},
    "component": SHELL_IDS
    | {
        "bc-toggle",
        "gallery-tab-docs",
        "gallery-tab-sandbox",
        "pane-docs",
        "pane-sandbox",
        "gallery-bg-panel",
        "gallery-viewport-panel",
        "gallery-zoom-panel",
        "mc-preview-sandbox",
        "mc-code-sandbox",
        "mc-html-sandbox",
    },
}


def _ids(markup: str) -> set[str]:
    return set(re.findall(r'\sid="([^"]+)"', markup))


def _page_urls() -> dict[str, str]:
    urls = {"index": "/dds/"}
    for node in _collect_all_nodes(_get_nav_tree()):
        urls.setdefault(node.node_type.value, node.url)
    return urls


class TestElementIds:
    @pytest.mark.parametrize("kind", list(PAGE_IDS))
    def test_page_keeps_its_ids(self, client, kind):
        response = client.get(_page_urls()[kind])
        assert response.status_code == 200
        assert PAGE_IDS[kind] <= _ids(response.content.decode())

    def test_variant_page_keeps_its_ids(self, client):
        response = client.get("/dds/demo_components/alert/?variant=critical")
        assert response.status_code == 200
        ids = _ids(response.content.decode())
        assert PAGE_IDS["component"] | {"gallery-variant-select"} <= ids

    def test_sandbox_fragment_keeps_its_ids(self, client):
        response = client.get(_page_urls()["component"], HTTP_HX_REQUEST="true")
        ids = _ids(response.content.decode())
        assert {
            "gallery-bg-panel",
            "gallery-viewport-panel",
            "gallery-zoom-panel",
            "mc-preview-sandbox",
            "mc-code-sandbox",
            "mc-html-sandbox",
        } <= ids
        assert "gallery-nav" not in ids

    def test_theme_select_id_with_several_themes(self, client):
        themes = {
            "default": {"label": "Default"},
            "dark": {"label": "Dark"},
        }
        with override_settings(DJ_DESIGN_SYSTEM={"GALLERY_THEMES": themes}):
            response = client.get("/dds/")
        assert "gallery-global-theme-select" in _ids(response.content.decode())


# ---------------------------------------------------------------------------
# Legacy partials
# ---------------------------------------------------------------------------


class TestLegacyPartials:
    @pytest.mark.parametrize("context", [{}, {"breadcrumbs": []}])
    def test_breadcrumb_without_crumbs_renders_nothing(self, context):
        markup = render_to_string("dj_design_system/gallery/breadcrumb.html", context)
        assert markup.strip() == ""

    @pytest.mark.parametrize("count", [1, 2, 3, 5])
    def test_breadcrumb(self, count):
        crumbs = CRUMBS[: count - 1] + [CRUMBS[-1]]
        markup = render_to_string(
            "dj_design_system/gallery/breadcrumb.html", {"breadcrumbs": crumbs}
        )
        _matches_snapshot(f"breadcrumb-{count}", markup)

    @pytest.mark.parametrize(
        "active_path", ["", "demo_nav/cards", "demo_nav/elements/icon"]
    )
    def test_navtree(self, nav_tree, active_path):
        markup = Template(
            "{% for app_node in nav_tree %}"
            '{% include "dj_design_system/gallery/navtree.html"'
            " with node=app_node depth=0 %}{% endfor %}"
        ).render(Context({"nav_tree": nav_tree, "active_path": active_path}))
        _matches_snapshot(f"navtree-{active_path.replace('/', '-') or 'root'}", markup)

    @pytest.mark.parametrize(
        ("active_path", "active_variant"),
        [
            ("demo_components/alert", None),
            ("demo_components/alert", "critical"),
            ("demo_components/alert", Variant(name="critical")),
        ],
        ids=["component", "variant-name", "variant-object"],
    )
    def test_navtree_with_variants(self, request, active_path, active_variant):
        markup = Template(
            "{% for app_node in nav_tree %}"
            '{% include "dj_design_system/gallery/navtree.html"'
            " with node=app_node depth=0 active_path=active_path"
            " active_variant=active_variant %}{% endfor %}"
        ).render(
            Context(
                {
                    "nav_tree": build_navigation(),
                    "active_path": active_path,
                    "active_variant": active_variant,
                }
            )
        )
        name = request.node.callspec.id
        _matches_snapshot(f"navtree-variants-{name}", markup)

    def test_toolbar(self):
        markup = render_to_string(
            "dj_design_system/gallery/toolbar.html",
            {"canvas_backgrounds": BACKGROUNDS, "active_bg_value": ACTIVE_BG},
        )
        _matches_snapshot("toolbar", markup)

    def test_toolbar_with_variant_presets(self):
        markup = render_to_string(
            "dj_design_system/gallery/toolbar.html",
            {
                "canvas_backgrounds": BACKGROUNDS,
                "active_bg_value": ACTIVE_BG,
                "gallery_variants": [Variant(name="basic"), Variant(name="critical")],
                "active_variant": Variant(name="critical"),
                "component_base_url": "/dds/demo_components/alert/",
                "active_theme": "dark",
            },
        )
        _matches_snapshot("toolbar-variants", markup)

    def test_canvas_widget_for_the_sandbox(self):
        markup = render_to_string(
            "dj_design_system/canvas_widget.html",
            widget_context(
                iframe_src="/dds/_canvas/?component=x",
                iframe_class="gallery-sandbox__iframe",
                extra_classes="gallery-sandbox__widget",
            ),
        )
        _matches_snapshot("canvas_widget-sandbox", markup)

    def test_canvas_widget_for_markdown(self):
        markup = render_to_string(
            "dj_design_system/canvas_widget.html",
            widget_context(
                unique_id="md-1",
                iframe_srcdoc="<p>Hi & bye</p>",
                sandbox_attrs="allow-scripts",
            ),
        )
        _matches_snapshot("canvas_widget-markdown", markup)
