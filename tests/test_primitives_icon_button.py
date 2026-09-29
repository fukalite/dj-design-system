"""Tests for the Icon, Button and IconButton built-in primitives."""

from html.parser import HTMLParser
from pathlib import Path

import pytest
from django.template import Context, Template

import dj_design_system
from dj_design_system.services.media import FOUNDATION_CSS
from dj_design_system.services.registry import component_registry


STATIC = Path(dj_design_system.__file__).parent / "static" / "dj_design_system"
SVG_ICONS = [
    "external-link",
    "eye",
    "code",
    "file-code",
    "monitor",
    "box-model",
    "ruler",
    "rtl",
]
MASK_ICONS = ["component", "doc", "folder", "folder-open"]


def render(source: str, **context) -> str:
    html = Template("{% load design_components %}" + source).render(Context(context))
    return html.strip()


class _Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags: list[tuple[str, dict[str, str | None]]] = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


def tags(html: str) -> list[tuple[str, dict[str, str | None]]]:
    """Return ``(tag, attrs)`` for every start tag, in document order."""
    parser = _Tags()
    parser.feed(html)
    return parser.tags


def root(html: str) -> tuple[str, dict[str, str | None]]:
    return tags(html)[0]


def _info(name: str):
    return component_registry.get_by_name(name, app_label="dj_design_system")


class TestRegistration:
    @pytest.mark.parametrize(
        ("name", "qualified"),
        [
            ("icon", "dds__primitives__icon"),
            ("button", "dds__primitives__button"),
            ("icon_button", "dds__primitives__icon_button"),
        ],
    )
    def test_builtins_are_internal_with_dds_names(self, name, qualified):
        info = _info(name)
        assert info.is_internal
        assert info.qualified_name == qualified

    @pytest.mark.parametrize("name", ["icon", "button", "icon_button"])
    def test_media_lists_foundation_first(self, name):
        assert _info(name).media.css[0] == FOUNDATION_CSS

    def test_icon_button_media_includes_icon_css(self):
        css = _info("icon_button").media.css
        assert css.index("dj_design_system/ui/primitives/icon.css") < css.index(
            "dj_design_system/ui/primitives/icon_button.css"
        )


class TestIcon:
    @pytest.mark.parametrize("name", SVG_ICONS)
    def test_svg_icons(self, name):
        tag, attrs = root(render("{% dds__primitives__icon name %}", name=name))
        assert tag == "svg"
        assert attrs["class"] == f"gallery-icon gallery-icon--{name}"
        assert (attrs["width"], attrs["height"]) == ("14", "14")
        assert attrs["viewbox"] == "0 0 24 24"
        assert attrs["aria-hidden"] == "true"
        assert attrs["focusable"] == "false"

    def test_svg_icon_size(self):
        _, attrs = root(render('{% dds__primitives__icon "eye" size=20 %}'))
        assert (attrs["width"], attrs["height"]) == ("20", "20")

    def test_svg_matches_legacy_external_link_paths(self):
        html = render('{% dds__primitives__icon "external-link" %}')
        _, attrs = root(html)
        assert attrs["stroke-linecap"] == attrs["stroke-linejoin"] == "round"
        assert ("polyline", {"points": "15 3 21 3 21 9"}) in tags(html)

    def test_square_line_caps_match_legacy(self):
        _, attrs = root(render('{% dds__primitives__icon "monitor" %}'))
        assert "stroke-linecap" not in attrs

    @pytest.mark.parametrize("name", MASK_ICONS)
    def test_mask_icons(self, name):
        html = render("{% dds__primitives__icon name %}", name=name)
        assert tags(html) == [
            (
                "span",
                {
                    "class": f"gallery-icon gallery-icon--mask gallery-icon--{name}",
                    "aria-hidden": "true",
                },
            )
        ]

    def test_extra_classes_keep_icon_classes(self):
        html = render(
            '{% dds__primitives__icon "component"'
            ' extra_classes="gallery-nav__icon gallery-nav__icon--component" %}'
        )
        _, attrs = root(html)
        assert attrs["class"] == (
            "gallery-icon gallery-icon--mask gallery-icon--component"
            " gallery-nav__icon gallery-nav__icon--component"
        )

    def test_mask_icon_size(self):
        _, attrs = root(render('{% dds__primitives__icon "doc" size=24 %}'))
        assert attrs["style"] == "width: 24px; height: 24px"

    def test_unknown_icon_is_rejected(self):
        with pytest.raises(ValueError):
            render('{% dds__primitives__icon "nope" %}')


def button(source: str = "", content: str = "x", **context):
    html = render(
        "{% dds__primitives__button "
        + source
        + " %}"
        + content
        + "{% enddds__primitives__button %}",
        **context,
    )
    return html, root(html)[1]


class TestButton:
    def test_toolbar_button(self):
        html, attrs = button('title="Zoom level"', content="100%")
        assert root(html)[0] == "button"
        assert attrs == {
            "class": "gallery-sandbox-toolbar__btn",
            "type": "button",
            "title": "Zoom level",
        }
        assert html.endswith(">100%</button>")

    def test_option_variant_and_active(self):
        _, attrs = button('variant="option" active=True')
        assert attrs["class"] == (
            "gallery-sandbox-toolbar__popout-option"
            " gallery-sandbox-toolbar__popout-option--active"
        )

    def test_active_toolbar_button(self):
        _, attrs = button("active=True")
        assert attrs["class"] == (
            "gallery-sandbox-toolbar__btn gallery-sandbox-toolbar__btn--active"
        )

    @pytest.mark.parametrize(("value", "text"), [(True, "true"), (False, "false")])
    def test_pressed(self, value, text):
        _, attrs = button("pressed=value", value=value)
        assert attrs["aria-pressed"] == text

    def test_no_aria_state_by_default(self):
        _, attrs = button()
        assert not {"aria-pressed", "aria-expanded", "aria-controls"} & set(attrs)

    def test_expanded_and_controls(self):
        _, attrs = button('expanded=False controls="gallery-bg-panel"')
        assert attrs["aria-expanded"] == "false"
        assert attrs["aria-controls"] == "gallery-bg-panel"

    def test_extra_classes_and_attrs(self):
        html, attrs = button(
            'extra_classes="gallery-sandbox-toolbar__zoom-btn" attrs=attrs',
            attrs={"data-zoom": "50", "data-x": '"><script>'},
        )
        assert attrs["class"] == (
            "gallery-sandbox-toolbar__btn gallery-sandbox-toolbar__zoom-btn"
        )
        assert attrs["data-zoom"] == "50"
        assert attrs["data-x"] == '"><script>'
        assert "<script>" not in html

    def test_escapes_title(self):
        html, attrs = button("title=title", title='"><b>')
        assert attrs["title"] == '"><b>'
        assert "<b>" not in html

    def test_content_is_rendered(self):
        html, _ = button(content='{% dds__primitives__icon "ruler" %}')
        assert [t for t, _ in tags(html)][:2] == ["button", "svg"]


class TestIconButton:
    def test_link(self):
        html = render(
            '{% dds__primitives__icon_button "external-link" "Open in sandbox"'
            ' href="#pane-sandbox" %}'
        )
        (tag, attrs), (svg, svg_attrs) = tags(html)[:2]
        assert tag == "a"
        assert attrs == {
            "class": "gallery-doc-preview__sandbox-link",
            "href": "#pane-sandbox",
            "title": "Open in sandbox",
            "aria-label": "Open in sandbox",
        }
        assert svg == "svg"
        assert svg_attrs["class"] == "gallery-icon gallery-icon--external-link"
        assert html.endswith("</a>")

    def test_button_without_href(self):
        html = render('{% dds__primitives__icon_button "eye" "Preview" %}')
        tag, attrs = root(html)
        assert tag == "button"
        assert attrs["type"] == "button"
        assert attrs["aria-label"] == attrs["title"] == "Preview"
        assert html.endswith("</button>")

    def test_extra_classes(self):
        html = render(
            '{% dds__primitives__icon_button "eye" "Preview" extra_classes="x" %}'
        )
        assert root(html)[1]["class"] == "gallery-doc-preview__sandbox-link x"

    def test_label_is_required(self):
        with pytest.raises(ValueError, match="label"):
            render('{% dds__primitives__icon_button "eye" %}')

    def test_empty_label_is_rejected(self):
        with pytest.raises(ValueError, match="label"):
            render('{% dds__primitives__icon_button "eye" "" %}')


class TestCssMovedNotCopied:
    """Rules owned by a component exist only in that component's stylesheet."""

    @pytest.mark.parametrize(
        ("selector", "owner"),
        [
            (".gallery-sandbox-toolbar__btn {", "ui/primitives/button.css"),
            (".gallery-sandbox-toolbar__btn:hover {", "ui/primitives/button.css"),
            (".gallery-sandbox-toolbar__btn--active {", "ui/primitives/button.css"),
            (".gallery-sandbox-toolbar__popout-option {", "ui/primitives/button.css"),
            (
                ".gallery-sandbox-toolbar__popout-option--active {",
                "ui/primitives/button.css",
            ),
            (".gallery-doc-preview__sandbox-link {", "ui/primitives/icon_button.css"),
            (".gallery-icon--mask {", "ui/primitives/icon.css"),
        ],
    )
    def test_rule_lives_only_in_owner(self, selector, owner):
        homes = [
            str(path.relative_to(STATIC))
            for path in sorted(STATIC.rglob("*.css"))
            if any(line.startswith(selector) for line in path.read_text().splitlines())
        ]
        assert homes == [owner]
