"""Service for parsing and rendering Python component docstrings."""

from __future__ import annotations

import html
import inspect
import re

import markdown as markdown_lib
from django.template import Context, Template
from django.utils import safestring


SECTION_HEADING_PATTERN: re.Pattern[str] = re.compile(r"^([A-Z][A-Za-z0-9 _-]*):$")
SPHINX_LITERAL_HEADER_PATTERN: re.Pattern[str] = re.compile(r"^(.*?)::\s*$")
EXPLICIT_ITEM_PATTERN: re.Pattern[str] = re.compile(r"^(\s*)[-*]\s+(.*)$")
PARAM_ITEM_PATTERN: re.Pattern[str] = re.compile(
    r"^\s*([a-zA-Z0-9_*]+)(?:\s*(\([^)]+\)))?\s*:\s*(.*)$"
)
FENCED_CODE_BLOCK_PATTERN: re.Pattern[str] = re.compile(
    r"^[ \t]{0,3}```([a-zA-Z0-9_+-]*)\s*\n(.*?)\n^[ \t]{0,3}```\s*$",
    re.MULTILINE | re.DOTALL,
)
STASH_TOKEN_PATTERN: re.Pattern[str] = re.compile(
    r"<p><!--(DDS_CODE_STASH_\d+)--></p>|<!--(DDS_CODE_STASH_\d+)-->"
)
DJANGO_SYNTAX_PATTERN: re.Pattern[str] = re.compile(r"\{[%{]")
PYTHON_SYNTAX_PATTERN: re.Pattern[str] = re.compile(
    r"^\s*(?:import |from |def |class |>>> )",
    re.MULTILINE,
)
PARAM_SECTION_NAMES: frozenset[str] = frozenset(
    {
        "Args",
        "Arguments",
        "Parameters",
        "Params",
        "Attributes",
        "Keyword Args",
        "Keyword Arguments",
        "Fields",
        "Properties",
    }
)


def transform_docstring_to_markdown(*, docstring: str) -> str:
    """Transform a Python docstring to normalized Markdown.

    Interprets Sphinx literal blocks (``::``), section headers (``Variants:``,
    ``Args:``), implicit parameter definitions, explicit lists, and multiline
    indentation into standard Markdown paragraphs, lists, and fenced blocks.
    """
    if not docstring or not docstring.strip():
        return ""

    cleaned = inspect.cleandoc(docstring)
    lines = cleaned.split("\n")
    output_lines: list[str] = []
    line_index = 0
    total_lines = len(lines)

    while line_index < total_lines:
        line = lines[line_index]

        literal_match = SPHINX_LITERAL_HEADER_PATTERN.match(line)
        if literal_match:
            heading_prefix = literal_match.group(1).strip()
            line_index += 1
            while line_index < total_lines and not lines[line_index].strip():
                line_index += 1

            code_lines: list[str] = []
            if line_index < total_lines:
                first_line = lines[line_index]
                base_indent = len(first_line) - len(first_line.lstrip())
                while line_index < total_lines:
                    current_line = lines[line_index]
                    if not current_line.strip():
                        code_lines.append("")
                        line_index += 1
                        continue
                    current_indent = len(current_line) - len(current_line.lstrip())
                    if base_indent > 0:
                        if current_indent >= base_indent:
                            code_lines.append(current_line[base_indent:])
                            line_index += 1
                        else:
                            break
                    else:
                        if SECTION_HEADING_PATTERN.match(current_line.strip()):
                            break
                        code_lines.append(current_line)
                        line_index += 1

            while code_lines and not code_lines[-1].strip():
                code_lines.pop()

            code_text = "\n".join(code_lines)
            if DJANGO_SYNTAX_PATTERN.search(code_text):
                lang = "django"
            elif PYTHON_SYNTAX_PATTERN.search(code_text):
                lang = "python"
            else:
                lang = "django"

            if heading_prefix:
                output_lines.append(f"**{heading_prefix}:**\n")
            output_lines.append(f"```{lang}\n{code_text}\n```\n")
            continue

        heading_match = SECTION_HEADING_PATTERN.match(line.strip())
        if heading_match:
            heading_name = heading_match.group(1)
            output_lines.append(f"**{heading_name}:**\n")
            line_index += 1
            while line_index < total_lines and not lines[line_index].strip():
                line_index += 1

            if line_index < total_lines:
                if EXPLICIT_ITEM_PATTERN.match(lines[line_index]):
                    while line_index < total_lines:
                        if not lines[line_index].strip():
                            lookahead_index = line_index + 1
                            while (
                                lookahead_index < total_lines
                                and not lines[lookahead_index].strip()
                            ):
                                lookahead_index += 1
                            if lookahead_index < total_lines and (
                                EXPLICIT_ITEM_PATTERN.match(lines[lookahead_index])
                                or lines[lookahead_index].startswith(" ")
                            ):
                                line_index += 1
                                continue
                            break
                        explicit_match = EXPLICIT_ITEM_PATTERN.match(lines[line_index])
                        if explicit_match:
                            output_lines.append(f"- {explicit_match.group(2).strip()}")
                            line_index += 1
                        elif lines[line_index].startswith(" ") or lines[
                            line_index
                        ].startswith("\t"):
                            output_lines.append(f"  {lines[line_index].strip()}")
                            line_index += 1
                        else:
                            break
                    output_lines.append("")
                    continue

                is_param_section = heading_name in PARAM_SECTION_NAMES
                first_item_match = PARAM_ITEM_PATTERN.match(lines[line_index])
                if is_param_section or first_item_match:
                    while line_index < total_lines:
                        if not lines[line_index].strip():
                            lookahead_index = line_index + 1
                            while (
                                lookahead_index < total_lines
                                and not lines[lookahead_index].strip()
                            ):
                                lookahead_index += 1
                            if lookahead_index < total_lines and (
                                PARAM_ITEM_PATTERN.match(lines[lookahead_index])
                                or lines[lookahead_index].startswith(" ")
                            ):
                                line_index += 1
                                continue
                            break
                        param_match = PARAM_ITEM_PATTERN.match(lines[line_index])
                        if param_match and not SECTION_HEADING_PATTERN.match(
                            lines[line_index].strip()
                        ):
                            param_name = param_match.group(1)
                            param_type = (
                                f" {param_match.group(2)}"
                                if param_match.group(2)
                                else ""
                            )
                            param_description = param_match.group(3)
                            output_lines.append(
                                f"- **{param_name}**{param_type}: {param_description}".rstrip()
                            )
                            line_index += 1
                        elif lines[line_index].startswith(" ") or lines[
                            line_index
                        ].startswith("\t"):
                            output_lines.append(f"  {lines[line_index].strip()}")
                            line_index += 1
                        else:
                            break
                    output_lines.append("")
                    continue
            continue

        if EXPLICIT_ITEM_PATTERN.match(line):
            explicit_match = EXPLICIT_ITEM_PATTERN.match(line)
            if (
                output_lines
                and output_lines[-1].strip()
                and not output_lines[-1].startswith("- ")
            ):
                output_lines.append("")
            if explicit_match:
                output_lines.append(f"- {explicit_match.group(2).strip()}")
            line_index += 1
            continue

        output_lines.append(line)
        line_index += 1

    return "\n".join(output_lines).strip()


def _render_code_block_markup(*, code: str, language: str) -> str:
    """Render a highlighted code block using the built-in dds__code_block component."""
    try:
        template_str = (
            "{% load design_components %}"
            "{% dds__code_block code=code language=language %}"
        )
        template = Template(template_str)
        return template.render(Context({"code": code, "language": language}))
    except Exception:
        escaped_code = html.escape(code)
        return f'<pre><code class="language-{language}">{escaped_code}</code></pre>'


def render_docstring(*, docstring: str) -> safestring.SafeString:
    """Render a docstring to formatted SafeString HTML with dds code blocks."""
    if not docstring or not docstring.strip():
        return safestring.mark_safe("")

    markdown_source = transform_docstring_to_markdown(docstring=docstring)
    stash: dict[str, str] = {}
    counter = 0

    def _replace_fenced_code(match: re.Match[str]) -> str:
        nonlocal counter
        counter += 1
        lang = match.group(1).strip() or "django"
        code = match.group(2)
        rendered_block = _render_code_block_markup(code=code, language=lang)
        token = f"DDS_CODE_STASH_{counter}"
        stash[token] = rendered_block
        return f"\n\n<!--{token}-->\n\n"

    processed_markdown = FENCED_CODE_BLOCK_PATTERN.sub(
        _replace_fenced_code, markdown_source
    )
    rendered_html = markdown_lib.markdown(
        processed_markdown,
        extensions=["tables"],
    )

    def _restore_stash(match: re.Match[str]) -> str:
        token = match.group(1) or match.group(2)
        return stash.get(token, "")

    final_html = STASH_TOKEN_PATTERN.sub(_restore_stash, rendered_html)
    return safestring.mark_safe(final_html)
