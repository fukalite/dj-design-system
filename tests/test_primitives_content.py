"""Tests for the Divider, SectionHeading, CodeBlock, Notice and Table primitives."""

import re

import pytest
from django.urls import reverse

from dj_design_system.services.media import FOUNDATION_CSS
from dj_design_system.services.registry import component_registry
from tests.html_utils import css_homes, render, root, tags


NAMES = ["divider", "section_heading", "code_block", "notice", "table"]
NOTICE_JS = "dj_design_system/ui/primitives/notice.js"


def block(tag: str, args: str = "", content: str = "", **context) -> str:
    return render(
        f"{{% dds__primitives__{tag} {args} %}}{content}{{% enddds__primitives__{tag} %}}",
        **context,
    )


class TestRegistration:
    @pytest.mark.parametrize("name", NAMES)
    def test_internal_with_dds_name_and_foundation_first(self, name):
        info = component_registry.get_by_name(name, app_label="dj_design_system")
        assert info.is_internal
        assert info.qualified_name == f"dds__primitives__{name}"
        assert info.media.css[0] == FOUNDATION_CSS


class TestDivider:
    def test_renders_legacy_hr(self):
        assert tags(render("{% dds__primitives__divider %}")) == [
            ("hr", {"class": "gallery-docs__divider"})
        ]


class TestSectionHeading:
    def test_defaults_to_h3_section_heading(self):
        html = block("section_heading", content="Usage")
        assert tags(html) == [("h3", {"class": "gallery-docs__section-heading"})]
        assert html.endswith(">Usage</h3>")

    @pytest.mark.parametrize("level", [2, 3, 4, 5, 6])
    def test_honours_level(self, level):
        tag, _ = root(block("section_heading", f"level={level}", "x"))
        assert tag == f"h{level}"

    def test_sub_variant_is_usage_heading(self):
        html = block("section_heading", 'variant="sub" level=4', "Minimal example")
        assert tags(html) == [("h4", {"class": "gallery-usage__heading"})]

    def test_rejects_unknown_level(self):
        with pytest.raises(ValueError):
            block("section_heading", "level=7", "x")

    def test_escapes_variables_in_content(self):
        html = block("section_heading", content="{{ text }}", text="<b>x</b>")
        assert "&lt;b&gt;" in html
        assert "<b>" not in html


class TestCodeBlock:
    def _code(self, html: str) -> str:
        match = re.fullmatch(
            r'<pre class="gallery-usage__pre"><code class="gallery-usage__code">'
            r"(.*)</code></pre>",
            html,
            re.DOTALL,
        )
        assert match, html
        return match.group(1)

    def test_plain_code_is_escaped(self):
        html = block("code_block", "code=src", src='{% button "<b>" %}')
        assert self._code(html) == "{% button &quot;&lt;b&gt;&quot; %}"

    def test_highlighted_html_passes_through(self):
        highlighted = '<span class="nt">{%</span> button <span class="s">"x"</span>'
        html = block("code_block", "highlighted=src", src=highlighted)
        assert self._code(html) == highlighted

    def test_highlighted_wins_over_code(self):
        html = block("code_block", 'code="plain" highlighted=hl', hl="<span>hl</span>")
        assert self._code(html) == "<span>hl</span>"

    def test_block_content_is_the_fallback(self):
        html = block("code_block", content="{{ src }}", src="<p>")
        assert self._code(html) == "&lt;p&gt;"

    def test_preserves_whitespace(self):
        html = block("code_block", "code=src", src="a\n  b\n")
        assert self._code(html) == "a\n  b\n"


class TestNotice:
    def test_warning_variant(self):
        html = block("notice", content="<p>Careful</p>")
        assert root(html) == ("div", {"class": "gallery-static-snapshot-notice"})
        assert "<p>Careful</p>" in html

    def test_hint_variant(self):
        html = block("notice", 'variant="hint"', "<p>Tip</p>")
        assert root(html) == ("div", {"class": "gallery-debug-hint"})

    def test_snapshot_warning_has_script_hook_id(self):
        tag, attrs = root(block("notice", "snapshot=True", "x"))
        assert attrs == {
            "id": "static-snapshot-notice",
            "class": "gallery-static-snapshot-notice",
        }

    def test_snapshot_requires_warning_variant(self):
        with pytest.raises(ValueError, match="snapshot"):
            block("notice", 'variant="hint" snapshot=True', "x")

    def test_owns_the_snapshot_script(self):
        info = component_registry.get_by_name("notice", app_label="dj_design_system")
        assert info.media.js == [NOTICE_JS]

    @pytest.mark.django_db
    def test_gallery_loads_the_script_once_with_nonce(self, client):
        from django.test import RequestFactory

        from dj_design_system.views import gallery_index

        request = RequestFactory().get(reverse("gallery"))
        request.user = type("U", (), {"is_authenticated": True, "is_staff": True})()
        request.csp_nonce = "n0nce"
        html = gallery_index(request).content.decode()

        scripts = re.findall(r"<script[^>]*notice\.js[^>]*>", html)
        assert len(scripts) == 1
        assert f"/static/{NOTICE_JS}" in scripts[0]
        assert 'nonce="n0nce"' in scripts[0]
        assert "gallery-snapshot-notice.js" not in html


class TestTable:
    HEAD = '{% slot "head" %}<tr><th>Name</th></tr>{% endslot %}'
    BODY = '{% slot "body" %}<tr><td>label</td></tr>{% endslot %}'

    def test_renders_head_and_body(self):
        html = block("table", content=self.HEAD + self.BODY)
        assert [t for t, _ in tags(html)] == [
            "table",
            "thead",
            "tr",
            "th",
            "tbody",
            "tr",
            "td",
        ]
        assert root(html) == ("table", {"class": "gallery-params"})
        assert "<th>Name</th>" in html
        assert "<td>label</td>" in html

    def test_head_is_optional(self):
        html = block("table", content=self.BODY)
        assert [t for t, _ in tags(html)] == ["table", "tbody", "tr", "td"]


class TestCssMovedNotCopied:
    @pytest.mark.parametrize(
        ("selector", "owner"),
        [
            (".gallery-docs__divider {", "divider.css"),
            (
                ":is(h1, h2, h3, h4, h5, h6).gallery-docs__section-heading {",
                "section_heading.css",
            ),
            (".gallery-usage__heading {", "section_heading.css"),
            (".gallery-usage__pre {", "code_block.css"),
            (
                ":is(.gallery-docs, .gallery-sandbox) .gallery-usage__pre {",
                "code_block.css",
            ),
            (".gallery-usage__code {", "code_block.css"),
            (".gallery-debug-hint {", "notice.css"),
            (".gallery-static-snapshot-notice {", "notice.css"),
            (".gallery-params {", "table.css"),
            (".gallery-params th,", "table.css"),
            (".gallery-params td code {", "table.css"),
        ],
    )
    def test_rule_lives_only_in_owner(self, selector, owner):
        assert css_homes(selector) == [f"ui/primitives/{owner}"]

    def test_legacy_section_heading_selector_is_gone(self):
        assert css_homes("h3.gallery-docs__section-heading") == []

    def test_responsive_table_rule_moved(self):
        from tests.html_utils import STATIC

        legacy = (STATIC / "gallery.css").read_text()
        assert ".gallery-params {" not in legacy
        table = (STATIC / "ui/primitives/table.css").read_text()
        assert "@media (max-width: 768px)" in table

    def test_snapshot_script_moved(self):
        from tests.html_utils import STATIC

        assert not (STATIC / "gallery-snapshot-notice.js").exists()
        assert (STATIC / "ui/primitives/notice.js").exists()
