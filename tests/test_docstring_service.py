"""Tests for docstring parsing and rendering service (dj_design_system.services.docstring)."""

import pytest
from django.utils.safestring import SafeString

from dj_design_system.components.gallery.elements.button.button import Button
from dj_design_system.components.gallery.elements.code_block.code_block import CodeBlock
from dj_design_system.components.gallery.elements.notice.notice import Notice
from dj_design_system.services.docstring import (
    render_docstring,
    transform_docstring_to_markdown,
)


class TestTransformDocstringToMarkdown:
    """Unit tests for converting Python docstrings to clean Markdown."""

    def test_empty_or_none_returns_empty_string(self) -> None:
        assert transform_docstring_to_markdown(docstring="") == ""
        assert transform_docstring_to_markdown(docstring="   \n  \t ") == ""

    def test_single_paragraph_preserved(self) -> None:
        doc = "A simple component description."
        assert (
            transform_docstring_to_markdown(docstring=doc)
            == "A simple component description."
        )

    def test_cleandoc_strips_uniform_indentation(self) -> None:
        doc = """
            First line.
            Second line.
        """
        result = transform_docstring_to_markdown(docstring=doc)
        assert result == "First line.\nSecond line."

    def test_sphinx_literal_block_converted_to_fenced_code(self) -> None:
        doc = """Example usage::

            {% dds__notice variant="info" %}
                Changes take effect.
            {% enddds__notice %}
        """
        result = transform_docstring_to_markdown(docstring=doc)
        assert "**Example usage:**" in result
        assert "```django" in result
        assert '{% dds__notice variant="info" %}' in result
        assert "    Changes take effect." in result
        assert "{% enddds__notice %}" in result
        assert "```" in result

    def test_sphinx_literal_block_python_detection(self) -> None:
        doc = """Python Example::

            from dj_design_system import components

            def build():
                return 42
        """
        result = transform_docstring_to_markdown(docstring=doc)
        assert "**Python Example:**" in result
        assert "```python" in result
        assert "from dj_design_system import components" in result

    def test_section_heading_with_explicit_list(self) -> None:
        doc = """Variants:
            - ``info`` (default): General tip.
            - ``warning``: Caution alert.
        """
        result = transform_docstring_to_markdown(docstring=doc)
        assert "**Variants:**" in result
        assert "- ``info`` (default): General tip." in result
        assert "- ``warning``: Caution alert." in result

    def test_section_heading_with_implicit_list(self) -> None:
        doc = """Args:
            code: Source code snippet to render.
            language: Code language identifier.
        """
        result = transform_docstring_to_markdown(docstring=doc)
        assert "**Args:**" in result
        assert "- **code**: Source code snippet to render." in result
        assert "- **language**: Code language identifier." in result

    def test_section_heading_with_typed_implicit_list(self) -> None:
        doc = """Parameters:
            name (str): The component identifier.
            count (int, optional): Number of items.
        """
        result = transform_docstring_to_markdown(docstring=doc)
        assert "**Parameters:**" in result
        assert "- **name** (str): The component identifier." in result
        assert "- **count** (int, optional): Number of items." in result

    def test_implicit_list_multiline_continuation(self) -> None:
        doc = """Args:
            items: Ordered list of trail items (BreadcrumbItem instances, dicts with
                'label' and optional 'url'/'href' and 'icon', or strings).
            icon: Optional leading icon.
        """
        result = transform_docstring_to_markdown(docstring=doc)
        assert "- **items**: Ordered list of trail items" in result
        assert "'label' and optional 'url'/'href' and 'icon', or strings)." in result
        assert "- **icon**: Optional leading icon." in result

    def test_multiple_sections_in_sequence(self) -> None:
        doc = """Polymorphic button component.

        Variants:
            - ``default``: Standard button.
            - ``primary``: Action button.

        Args:
            label: Button text.
            variant: Visual style.

        Example usage::

            {% dds__button label="Save" %}
        """
        result = transform_docstring_to_markdown(docstring=doc)
        assert "**Variants:**" in result
        assert "- ``default``: Standard button." in result
        assert "- ``primary``: Action button." in result
        assert "**Args:**" in result
        assert "- **label**: Button text." in result
        assert "- **variant**: Visual style." in result
        assert "**Example usage:**" in result
        assert "```django" in result
        assert '{% dds__button label="Save" %}' in result


@pytest.mark.django_db
class TestRenderDocstring:
    """Integration tests for rendering docstrings to SafeString HTML with dds-code-block."""

    def test_empty_docstring_returns_safestring(self) -> None:
        html = render_docstring(docstring="")
        assert isinstance(html, SafeString)
        assert html == ""

    def test_renders_explicit_list_as_unordered_list(self) -> None:
        doc = """Variants:
            - ``info``: General tip.
            - ``error``: Critical alert.
        """
        html = render_docstring(docstring=doc)
        assert isinstance(html, SafeString)
        assert "<strong>Variants:</strong>" in html
        assert "<ul>" in html
        assert "<li><code>info</code>: General tip.</li>" in html
        assert "<li><code>error</code>: Critical alert.</li>" in html
        assert "</ul>" in html

    def test_renders_implicit_list_as_unordered_list(self) -> None:
        doc = """Args:
            label: Button text label.
            disabled: Whether interaction is disabled.
        """
        html = render_docstring(docstring=doc)
        assert "<strong>Args:</strong>" in html
        assert "<ul>" in html
        assert "<li><strong>label</strong>: Button text label.</li>" in html
        assert (
            "<li><strong>disabled</strong>: Whether interaction is disabled.</li>"
            in html
        )
        assert "</ul>" in html

    def test_renders_multiline_code_as_dds_code_block(self) -> None:
        doc = """Example usage::

            {% dds__notice variant="info" title="Note" %}
                Changes take effect.
            {% enddds__notice %}
        """
        html = render_docstring(docstring=doc)
        assert "<dds-code-block" in html
        assert 'class="dds-code-block"' in html
        assert 'data-surface="code"' in html
        assert 'data-language="django"' in html
        assert "data-copy-trigger" in html
        assert "Changes take effect." in html

    def test_notice_docstring_end_to_end(self) -> None:
        raw_doc = Notice.__doc__ or ""
        html = render_docstring(docstring=raw_doc)
        assert "<strong>Variants:</strong>" in html
        assert "<ul>" in html
        assert "<code>info</code> (default):" in html
        assert "<code>success</code>:" in html
        assert "<code>warning</code>:" in html
        assert "<code>error</code>:" in html
        assert "<strong>Example usage:</strong>" in html
        assert "<dds-code-block" in html
        assert 'data-language="django"' in html

    def test_code_block_docstring_end_to_end(self) -> None:
        raw_doc = CodeBlock.__doc__ or ""
        html = render_docstring(docstring=raw_doc)
        assert "<strong>Args:</strong>" in html
        assert "<ul>" in html
        assert "<strong>code</strong>: Source code snippet to render." in html
        assert "<strong>language</strong>:" in html
        assert "<dds-code-block" in html

    def test_button_docstring_end_to_end(self) -> None:
        raw_doc = Button.__doc__ or ""
        html = render_docstring(docstring=raw_doc)
        assert "<strong>Variants:</strong>" in html
        assert "<strong>Args:</strong>" in html
        assert "<code>default</code>:" in html
        assert "<strong>label</strong>:" in html
