"""Tests for the gallery layout built-ins: shell, sidebar, toolbar, panes and pages."""

import pytest

from dj_design_system.services.media import FOUNDATION_CSS
from dj_design_system.services.registry import component_registry
from tests.html_utils import STATIC, css_homes, render, root, tags


NAMES = [
    "gallery_shell",
    "mobile_menu_toggle",
    "sidebar",
    "toolbar",
    "split_pane",
    "pane",
    "page",
    "prose",
]


def slotted(tag: str, args: str = "", **slots) -> str:
    body = "".join(
        f'{{% slot "{name}" %}}{value}{{% endslot %}}' for name, value in slots.items()
    )
    return render(
        f"{{% dds__layout__{tag} {args} %}}{body}{{% enddds__layout__{tag} %}}"
    )


def block(tag: str, args: str = "", content: str = "", **context) -> str:
    return render(
        f"{{% dds__layout__{tag} {args} %}}{content}{{% enddds__layout__{tag} %}}",
        **context,
    )


class TestRegistration:
    @pytest.mark.parametrize("name", NAMES)
    def test_internal_with_dds_name_and_foundation_first(self, name):
        info = component_registry.get_by_name(name, app_label="dj_design_system")
        assert info.is_internal
        assert info.qualified_name == f"dds__layout__{name}"
        assert info.media.css[0] == FOUNDATION_CSS

    def test_prose_loads_page_css_first(self):
        css = component_registry.get_by_name(
            "prose", app_label="dj_design_system"
        ).media.css
        assert css.index("dj_design_system/ui/layout/page.css") < css.index(
            "dj_design_system/ui/layout/prose.css"
        )


class TestMobileMenuToggle:
    def test_legacy_markup(self):
        assert tags(render("{% dds__layout__mobile_menu_toggle %}")) == [
            (
                "input",
                {
                    "type": "checkbox",
                    "id": "gallery-sidebar-toggle",
                    "class": "gallery-sidebar-toggle",
                    "aria-hidden": "true",
                },
            ),
            (
                "label",
                {
                    "for": "gallery-sidebar-toggle",
                    "class": "gallery-hamburger",
                    "aria-label": "Toggle navigation",
                },
            ),
            ("span", {"class": "gallery-hamburger__line"}),
            ("span", {"class": "gallery-hamburger__line"}),
            ("span", {"class": "gallery-hamburger__line"}),
            ("label", {"for": "gallery-sidebar-toggle", "class": "gallery-overlay"}),
        ]


class TestGalleryShell:
    def test_structure_and_slot_order(self):
        html = slotted(
            "gallery_shell",
            sidebar="<aside>S</aside>",
            toolbar="<div>T</div>",
            content="<p>C</p>",
        )
        names = [t for t, _ in tags(html)]
        assert names[0] == "div" and root(html)[1] == {"class": "gallery"}
        # The toggle precedes the sidebar: its :checked ~ sibling rules need that.
        assert names.index("input") < names.index("aside")
        assert ("main", {"class": "gallery-main"}) in tags(html)
        assert ("div", {"class": "gallery-content-area"}) in tags(html)
        assert html.index(">T<") < html.index('class="gallery-content-area"')
        assert html.index('class="gallery-content-area"') < html.index(">C<")


class TestSidebar:
    def test_title_search_and_nav(self):
        html = slotted(
            "sidebar",
            'title="My Library" title_url="/dds/"',
            search="<input id=s>",
            nav='<nav id="gallery-nav"></nav>',
        )
        assert tags(html)[:3] == [
            ("aside", {"class": "gallery-sidebar"}),
            ("div", {"class": "gallery-sidebar__header"}),
            ("a", {"class": "gallery-sidebar__title", "href": "/dds/"}),
        ]
        assert ">My Library</a>" in html
        assert html.index("<input id=s>") < html.index('id="gallery-nav"')

    def test_escapes_title(self):
        html = render(
            "{% dds__layout__sidebar title=t title_url='/' %}"
            '{% slot "nav" %}{% endslot %}{% enddds__layout__sidebar %}',
            t="<b>x</b>",
        )
        assert "&lt;b&gt;x&lt;/b&gt;" in html
        assert "<b>" not in html


class TestToolbar:
    def test_start_and_actions(self):
        html = slotted("toolbar", start="<a href='/'>Gallery</a>", actions="<b>A</b>")
        assert tags(html)[:3] == [
            ("div", {"class": "gallery-toolbar"}),
            ("div", {"class": "gallery-toolbar__breadcrumb"}),
            ("a", {"href": "/"}),
        ]
        assert ("div", {"class": "gallery-toolbar__actions"}) in tags(html)
        assert html.index("Gallery") < html.index("<b>A</b>")


class TestSplitPaneAndPane:
    def test_documentation_pane(self):
        html = block(
            "pane",
            'title="Documentation" pane_id="pane-docs" variant="documentation"'
            ' body_classes="gallery-docs"',
            "<p>docs</p>",
        )
        assert tags(html)[:3] == [
            (
                "div",
                {
                    "class": "gallery-documentation gallery-split__pane",
                    "id": "pane-docs",
                },
            ),
            ("div", {"class": "gallery-split__pane-header"}),
            ("div", {"class": "gallery-split__pane-body gallery-docs"}),
        ]
        assert ">Documentation</div>" in html

    def test_sandbox_pane_body_attrs(self):
        html = block(
            "pane",
            'title="Sandbox" pane_id="pane-sandbox" variant="sandbox" body_attrs=attrs',
            "x",
            attrs={"data-gallery-sandbox-body": ""},
        )
        (_, pane), _, (_, body) = tags(html)[:3]
        assert pane["class"] == "gallery-sandbox gallery-split__pane"
        assert body["data-gallery-sandbox-body"] == ""

    def test_split_pane_wraps_primary_then_secondary(self):
        html = slotted("split_pane", primary="<i>P</i>", secondary="<i>S</i>")
        assert root(html) == ("div", {"class": "gallery-split"})
        assert html.index(">P<") < html.index(">S<")


class TestPageAndProse:
    def test_page(self):
        html = block("page", content="<h1>Hi</h1>")
        assert tags(html)[:3] == [
            ("div", {"class": "gallery-page"}),
            ("div", {"class": "gallery-docs"}),
            ("h1", {}),
        ]

    def test_prose(self):
        html = block("prose", content="<p>Rich</p>")
        assert root(html) == ("div", {"class": "gallery-markdown"})
        assert "<p>Rich</p>" in html


class TestCssMovedNotCopied:
    @pytest.mark.parametrize(
        ("selector", "owner"),
        [
            (".gallery {", "gallery_shell.css"),
            (".gallery-main {", "gallery_shell.css"),
            (".gallery-content-area {", "gallery_shell.css"),
            (".gallery-sidebar {", "sidebar.css"),
            (".gallery-sidebar__title {", "sidebar.css"),
            (".gallery-toolbar {", "toolbar.css"),
            (".gallery-toolbar__actions {", "toolbar.css"),
            (".gallery-split {", "split_pane.css"),
            (".gallery-split__pane-header {", "pane.css"),
            (".gallery-page {", "page.css"),
            (".gallery-docs p {", "page.css"),
            (".gallery-markdown {", "prose.css"),
            (".gallery-hamburger {", "mobile_menu_toggle.css"),
            (".gallery-overlay {", "mobile_menu_toggle.css"),
        ],
    )
    def test_rule_lives_only_in_owner(self, selector, owner):
        assert css_homes(selector) == [f"ui/layout/{owner}"]

    def test_legacy_stylesheet_keeps_unmoved_sections(self):
        legacy = (STATIC / "gallery.css").read_text()
        assert ".gallery-sandbox__controls {" in legacy  # track 4

    def test_folder_heading_yields_to_page_context(self):
        # .gallery-docs h2 now loads before gallery.css; the folder heading
        # uses :where() to keep losing to it, as it did on source order.
        assert css_homes(":where(.gallery-folder-contents) h2 {") == [
            "ui/navigation/folder_listing.css"
        ]

    def test_section_heading_yields_to_page_context(self):
        # Page CSS now loads before the primitives, so SectionHeading uses
        # :where() to keep losing to .gallery-docs h3 as it did before.
        assert css_homes(
            ":where(h1, h2, h3, h4, h5, h6).gallery-docs__section-heading {"
        ) == ["ui/primitives/section_heading.css"]
