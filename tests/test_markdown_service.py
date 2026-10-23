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

        html_service = render_markdown_doc(file_path=doc)
        html_shim = _render_markdown(file_path=doc)
        assert html_shim == html_service

    @override_settings(
        DJ_DESIGN_SYSTEM={
            "GALLERY_DEFAULT_THEME": "light",
            "GALLERY_THEMES": {
                "light": {"label": "Light", "css": ["themes/light.css"]},
                "dark": {"label": "Dark", "css": ["themes/dark.css"]},
            },
            "APP_CSS": {
                "demo_components": ["demo_components/app_bundle.css"],
            },
        }
    )
    def test_render_component_uses_validated_theme_and_owning_app_label(
        self, tmp_path: Path
    ):
        """_render_component passes validated theme and info.app_label to render_markdown_doc (#186, #187)."""
        from django.test import RequestFactory

        from dj_design_system.components import TagComponent
        from dj_design_system.data import ComponentInfo, NavNode
        from dj_design_system.gallery import GalleryConfig
        from dj_design_system.parameters.base import StrParam
        from dj_design_system.services.registry import component_registry
        from dj_design_system.types import NodeType
        from dj_design_system.views.component import render_component_node
        from dj_design_system.views.gallery import get_base_context

        class DocWidget(TagComponent):
            template_format_str = "<span>{label}</span>"
            label = StrParam(description="Label", default="Hello")

        info = ComponentInfo(
            component_class=DocWidget,
            name="doc_widget",
            app_label="demo_components",
            relative_path="promoted.doc_widget",
        )
        info.__dict__["gallery_config"] = GalleryConfig(theme="dark")
        component_registry._components.append(info)
        try:
            doc = tmp_path / "index.md"
            doc.write_text('```canvas\n{% button "Click" %}\n```', encoding="utf-8")

            node = NavNode(
                label="Doc Widget",
                slug="doc_widget",
                node_type=NodeType.COMPONENT,
                component=info,
                index_doc_path=doc,
                url="/promoted/doc_widget/",
                app_label="demo_components",
            )

            rf = RequestFactory()
            request = rf.get(path="/promoted/doc_widget/")
            request.COOKIES["dds_theme"] = "stale-invalid-theme"

            context = get_base_context(
                request=request,
                active_app="promoted",
                active_path="promoted/doc_widget",
            )
            render_component_node(
                request=request,
                context=context,
                node=node,
                app_label="promoted",
                path_parts=["doc_widget"],
            )

            # Invalid cookie falls back to default theme ('light'), updating context['active_theme']
            assert context["active_theme"] == "light"
            assert "themes/light.css" in context["doc_html"]
            # Uses info.app_label ('demo_components') rather than promoted URL app_label ('promoted')
            assert "demo_components/app_bundle.css" in context["doc_html"]
        finally:
            component_registry._components.remove(info)

    @override_settings(
        DJ_DESIGN_SYSTEM={
            "GALLERY_DEFAULT_THEME": "light",
            "GALLERY_THEMES": {
                "light": {"label": "Light", "css": ["themes/light.css"]},
            },
            "APP_CSS": {
                "demo_components": ["demo_components/app_bundle.css"],
            },
        }
    )
    def test_render_folder_and_document_fallback_theme_and_owning_app_label(
        self, tmp_path: Path
    ):
        """_render_folder and _render_document fall back to default theme and use node.app_label (#186, #187)."""
        from django.test import RequestFactory

        from dj_design_system.data import NavNode
        from dj_design_system.types import NodeType
        from dj_design_system.views.gallery import (
            _render_document,
            _render_folder,
            get_base_context,
        )

        doc = tmp_path / "index.md"
        doc.write_text('```canvas\n{% button "Click" %}\n```', encoding="utf-8")

        rf = RequestFactory()
        request = rf.get(path="/promoted/guides/")
        request.COOKIES["dds_theme"] = "nonexistent-theme"

        folder_node = NavNode(
            label="Guides",
            slug="guides",
            node_type=NodeType.FOLDER,
            index_doc_path=doc,
            app_label="demo_components",
        )
        folder_ctx = get_base_context(
            request=request, active_app="promoted", active_path="promoted/guides"
        )
        _render_folder(
            request=request,
            context=folder_ctx,
            node=folder_node,
            app_label="promoted",
            path_parts=["guides"],
        )
        assert "themes/light.css" in folder_ctx["doc_html"]
        assert "demo_components/app_bundle.css" in folder_ctx["doc_html"]

        doc_node = NavNode(
            label="Overview",
            slug="overview",
            node_type=NodeType.DOCUMENT,
            doc_path=doc,
            app_label="demo_components",
        )
        doc_ctx = get_base_context(
            request=request, active_app="promoted", active_path="promoted/overview"
        )
        _render_document(
            request=request,
            context=doc_ctx,
            node=doc_node,
            app_label="promoted",
            path_parts=["overview"],
        )
        assert "themes/light.css" in doc_ctx["doc_html"]
        assert "demo_components/app_bundle.css" in doc_ctx["doc_html"]
