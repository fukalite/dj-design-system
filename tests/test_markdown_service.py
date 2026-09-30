"""Tests for dj_design_system.services.markdown."""

from pathlib import Path

import pytest
from django.test import override_settings

from dj_design_system.services.markdown import render_markdown_doc
from dj_design_system.views.gallery import _render_markdown


@pytest.mark.django_db
class TestRenderMarkdownService:
    def test_render_markdown_doc_basic(self, tmp_path: Path):
        doc = tmp_path / "test.md"
        doc.write_text(
            "# Heading 1\n\nThis is a paragraph with **bold** text.", encoding="utf-8"
        )

        html = render_markdown_doc(doc)
        assert ">Heading 1</h1>" in html
        assert "<strong>bold</strong>" in html

    def test_render_markdown_doc_with_table_and_fenced_code(self, tmp_path: Path):
        doc = tmp_path / "table.md"
        doc.write_text(
            "| A | B |\n|---|---|\n| 1 | 2 |\n\n```python\nx = 1\n```",
            encoding="utf-8",
        )

        html = render_markdown_doc(doc)
        assert "<table>" in html
        assert "<code>" in html

    @override_settings(DJ_DESIGN_SYSTEM={"GALLERY_CODEHILITE_STYLE": "monokai"})
    def test_render_markdown_doc_codehilite(self, tmp_path: Path):
        doc = tmp_path / "code.md"
        doc.write_text("```python\nx = 42\n```", encoding="utf-8")

        html = render_markdown_doc(doc)
        assert "gallery-highlight" in html

    def test_deprecated_views_render_markdown_shim(self, tmp_path: Path):
        doc = tmp_path / "shim.md"
        doc.write_text("## Subtitle\n\nContent", encoding="utf-8")

        html_service = render_markdown_doc(doc)
        html_shim = _render_markdown(doc)
        assert html_shim == html_service
