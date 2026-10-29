"""Tests for markdown services, frontmatter extraction, and loose list parsing."""

import markdown as markdown_lib

from dj_design_system.services.markdown import (
    LooseListExtension,
    extract_frontmatter,
    render_markdown_doc,
)


class TestExtractFrontmatter:
    """Tests for extract_frontmatter helper."""

    def test_extract_frontmatter_standard(self):
        content = """---
order: 2
title: "My Component"
---
# Content Heading
Here is the body.
"""
        meta, body = extract_frontmatter(content=content)
        assert meta == {"order": 2, "title": "My Component"}
        assert body == "# Content Heading\nHere is the body.\n"

    def test_extract_frontmatter_negative_order(self):
        content = """---
order: -10
label: 'Custom Label'
---
Paragraph
"""
        meta, body = extract_frontmatter(content=content)
        assert meta == {"order": -10, "label": "Custom Label"}
        assert body == "Paragraph\n"

    def test_extract_frontmatter_boolean(self):
        content = """---
active: true
disabled: false
---
Body
"""
        meta, body = extract_frontmatter(content=content)
        assert meta == {"active": True, "disabled": False}
        assert body == "Body\n"

    def test_extract_frontmatter_quoted_order_converts_to_int(self):
        content = """---
order: "15"
---
Body
"""
        meta, body = extract_frontmatter(content=content)
        assert meta == {"order": 15}

    def test_extract_frontmatter_colon_in_value(self):
        content = """---
title: "Prefix: Subtitle"
---
Body
"""
        meta, body = extract_frontmatter(content=content)
        assert meta == {"title": "Prefix: Subtitle"}

    def test_extract_frontmatter_comments_and_blank_lines(self):
        content = """---
# Comment line
order: 5

title: Unquoted Title
---
Body
"""
        meta, body = extract_frontmatter(content=content)
        assert meta == {"order": 5, "title": "Unquoted Title"}
        assert body == "Body\n"

    def test_extract_frontmatter_empty_block(self):
        content = """---
---
Body
"""
        meta, body = extract_frontmatter(content=content)
        assert meta == {}
        assert body == "Body\n"

    def test_extract_frontmatter_no_frontmatter(self):
        content = "# Just Heading\n---\nHorizontal rule\n"
        meta, body = extract_frontmatter(content=content)
        assert meta == {}
        assert body == content

    def test_extract_frontmatter_unclosed_block(self):
        content = """---
order: 5
title: Never closed
# No closing delimiter
"""
        meta, body = extract_frontmatter(content=content)
        assert meta == {}
        assert body == content

    def test_extract_frontmatter_bom_handling(self):
        content = "\ufeff---\norder: 1\n---\nBody\n"
        meta, body = extract_frontmatter(content=content)
        assert meta == {"order": 1}
        assert body == "Body\n"


class TestLooseListExtension:
    """Tests for LooseListPreprocessor and LooseListExtension."""

    def test_loose_bullet_list_after_paragraph(self):
        text = "Some text:\n- bullet 1\n- bullet 2"
        html = markdown_lib.markdown(
            text, extensions=[LooseListExtension(), "sane_lists"]
        )
        assert "<p>Some text:</p>" in html
        assert "<ul>" in html
        assert "<li>bullet 1</li>" in html
        assert "<li>bullet 2</li>" in html

    def test_loose_asterisk_bullet_list(self):
        text = "Intro:\n* first\n* second"
        html = markdown_lib.markdown(
            text, extensions=[LooseListExtension(), "sane_lists"]
        )
        assert "<p>Intro:</p>" in html
        assert "<ul>" in html
        assert "<li>first</li>" in html

    def test_loose_numbered_list_after_paragraph(self):
        text = "Steps to follow:\n1. Step one\n2. Step two"
        html = markdown_lib.markdown(
            text, extensions=[LooseListExtension(), "sane_lists"]
        )
        assert "<p>Steps to follow:</p>" in html
        assert "<ol>" in html
        assert "<li>Step one</li>" in html
        assert "<li>Step two</li>" in html

    def test_fenced_code_block_preserved(self):
        text = """```python
Some text:
- not a bullet list item
```"""
        html = markdown_lib.markdown(
            text, extensions=[LooseListExtension(), "fenced_code"]
        )
        assert "- not a bullet list item" in html
        assert "<ul>" not in html

    def test_tilde_fenced_code_block_preserved(self):
        text = """~~~text
Some text:
- not a bullet list item
~~~"""
        html = markdown_lib.markdown(
            text, extensions=[LooseListExtension(), "fenced_code"]
        )
        assert "- not a bullet list item" in html
        assert "<ul>" not in html

    def test_list_after_heading_preserved(self):
        text = "# Heading\n- item 1\n- item 2"
        html = markdown_lib.markdown(
            text, extensions=[LooseListExtension(), "sane_lists"]
        )
        assert "<h1>Heading</h1>" in html
        assert "<ul>" in html
        assert "<li>item 1</li>" in html

    def test_list_already_spaced_preserved(self):
        text = "Paragraph\n\n- item 1\n- item 2"
        html = markdown_lib.markdown(
            text, extensions=[LooseListExtension(), "sane_lists"]
        )
        assert "<p>Paragraph</p>" in html
        assert "<ul>" in html


class TestRenderMarkdownDoc:
    """Tests for render_markdown_doc function."""

    def test_render_strips_frontmatter(self, tmp_path):
        doc = tmp_path / "test_doc.md"
        doc.write_text(
            """---
order: 5
title: "Frontmatter Title"
---
# Actual Heading

This is content.
- List item 1
- List item 2
""",
            encoding="utf-8",
        )

        html = render_markdown_doc(doc)
        assert "Frontmatter Title" not in html
        assert "order: 5" not in html
        assert "Actual Heading</h1>" in html
        assert "<ul>" in html
        assert "<li>List item 1</li>" in html

    def test_render_nonexistent_returns_empty(self, tmp_path):
        missing = tmp_path / "nonexistent.md"
        assert render_markdown_doc(missing) == ""
