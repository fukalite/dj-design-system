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
        html = render('{% dds__primitives__section_heading "Usage" %}')
        assert tags(html) == [("h3", {"class": "gallery-docs__section-heading"})]
        assert html.endswith(">Usage</h3>")

    @pytest.mark.parametrize("level", [2, 3, 4, 5, 6])
    def test_honours_level(self, level):
        tag, _ = root(
            render(f'{{% dds__primitives__section_heading "x" level={level} %}}')
        )
        assert tag == f"h{level}"

    def test_sub_variant_is_usage_heading(self):
        html = render(
            '{% dds__primitives__section_heading "Minimal example" variant="sub" level=4 %}'
        )
        assert tags(html) == [("h4", {"class": "gallery-usage__heading"})]
        assert ">Minimal example</h4>" in html

    def test_rejects_unknown_level(self):
        with pytest.raises(ValueError):
            render('{% dds__primitives__section_heading "x" level=7 %}')

    def test_escapes_text(self):
        html = render("{% dds__primitives__section_heading text %}", text="<b>x</b>")
        assert "&lt;b&gt;" in html
        assert "<b>" not in html

    def test_is_a_tag(self):
        from dj_design_system.types import TagType

        info = component_registry.get_by_name(
            "section_heading", app_label="dj_design_system"
        )
        assert info.tag_type is TagType.TAG


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

    def test_body_is_the_code(self):
        html = block("code_block", content="\ntotal = price * quantity\n")
        assert self._code(html) == "total = price * quantity"

    def test_plain_text_by_default_and_escaped(self):
        html = block("code_block", content='<b class="x">&</b>')
        assert self._code(html) == "&lt;b class=&quot;x&quot;&gt;&amp;&lt;/b&gt;"

    def test_template_variables_are_not_double_escaped(self):
        html = block("code_block", content="{{ src }}", src='{% button "<b>" %}')
        assert self._code(html) == "{% button &quot;&lt;b&gt;&quot; %}"

    def test_dedents_and_preserves_inner_whitespace(self):
        html = block(
            "code_block",
            'language="python"',
            "\n    def f():\n        return 1\n",
        )
        text = re.sub(r"<[^>]+>", "", self._code(html))
        assert text == "def f():\n    return 1"

    def test_highlights_the_given_language(self):
        html = block("code_block", 'language="python"', "def f(): pass")
        code = self._code(html)
        assert '<span class="k">def</span>' in code
        assert '<span class="nf">f</span>' in code

    def test_highlights_django_templates(self):
        html = block(
            "code_block", 'language="django"', "{{ src }}", src='{% button "Save" %}'
        )
        code = self._code(html)
        assert "<span" in code
        assert "button" in code
        assert "<b>" not in code

    def test_unknown_language_is_rejected(self):
        with pytest.raises(ValueError, match="language"):
            block("code_block", 'language="no-such-language"', "x")


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
                ":where(h1, h2, h3, h4, h5, h6).gallery-docs__section-heading {",
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

        table = (STATIC / "ui/primitives/table.css").read_text()
        assert "@media (max-width: 768px)" in table

    def test_highlight_theme_moved_under_code_block(self):
        from tests.html_utils import STATIC

        assert not (STATIC / "gallery-highlight.css").exists()
        info = component_registry.get_by_name(
            "code_block", app_label="dj_design_system"
        )
        assert "dj_design_system/ui/primitives/code_highlight.css" in info.media.css

    def test_snapshot_script_moved(self):
        from tests.html_utils import STATIC

        assert not (STATIC / "gallery-snapshot-notice.js").exists()
        assert (STATIC / "ui/primitives/notice.js").exists()
