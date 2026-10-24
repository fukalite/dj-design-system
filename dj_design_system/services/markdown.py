"""Service for rendering markdown documentation files with design system extensions."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING, Any

import markdown as markdown_lib
from django.conf import settings
from django.utils.safestring import mark_safe
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

from dj_design_system.services.markdown_canvas import CanvasExtension
from dj_design_system.services.markdown_links import RelativeLinksExtension
from dj_design_system.settings import dds_settings
from dj_design_system.types import ColorScheme


if TYPE_CHECKING:
    from dj_design_system.types import Theme


FRONTMATTER_PATTERN = re.compile(
    r"^---\s*\r?\n(?:(.*?)\r?\n)?---\s*(?:\r?\n|$)",
    re.DOTALL,
)


def extract_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Extract YAML-like frontmatter from markdown content.

    Parses an optional leading metadata block enclosed by lines containing only
    `---`. Key-value pairs are separated by a colon, converting integer values
    (such as `order: 2` or `order: -5`) to `int` and stripping matching
    surrounding quotes from strings.

    Args:
        content: Raw markdown text potentially starting with frontmatter.

    Returns:
        A tuple of `(metadata_dict, remaining_body)`.
    """
    clean_content = content.lstrip("\ufeff")
    match = FRONTMATTER_PATTERN.match(clean_content)
    if not match:
        return {}, content

    raw_yaml = match.group(1) or ""
    body = clean_content[match.end() :]
    metadata: dict[str, Any] = {}

    for line in raw_yaml.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key = key.strip()
        val = val.strip()
        if not key:
            continue

        if (val.startswith('"') and val.endswith('"') and len(val) >= 2) or (
            val.startswith("'") and val.endswith("'") and len(val) >= 2
        ):
            parsed_val: Any = val[1:-1]
        else:
            try:
                parsed_val = int(val)
            except ValueError:
                if val.lower() == "true":
                    parsed_val = True
                elif val.lower() == "false":
                    parsed_val = False
                else:
                    parsed_val = val

        if key == "order" and isinstance(parsed_val, str):
            try:
                parsed_val = int(parsed_val)
            except ValueError:
                pass

        metadata[key] = parsed_val

    return metadata, body


class LooseListPreprocessor(Preprocessor):
    """Preprocessor ensuring lists without preceding blank lines are parsed as lists.

    Python-Markdown requires an empty line before a bulleted or numbered list
    when it immediately follows a paragraph. Outside fenced code blocks (` ``` `
    or `~~~`), if a non-blank, non-list, non-heading, non-table, non-blockquote line
    is immediately followed by a list item, an empty line is inserted before the
    list item.
    """

    LIST_ITEM_RE = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+")
    FENCE_START_RE = re.compile(r"^[ ]{0,3}(`{3,}|~{3,})")

    def run(self, lines: list[str]) -> list[str]:
        """Process markdown lines, injecting blank lines before loose lists."""
        new_lines: list[str] = []
        in_fence = False
        fence_char = ""
        fence_length = 0

        for line in lines:
            fence_match = self.FENCE_START_RE.match(line)
            if not in_fence:
                if fence_match:
                    in_fence = True
                    marker = fence_match.group(1)
                    fence_char = marker[0]
                    fence_length = len(marker)
                    new_lines.append(line)
                    continue
            else:
                if fence_match:
                    marker = fence_match.group(1)
                    if marker[0] == fence_char and len(marker) >= fence_length:
                        in_fence = False
                        fence_char = ""
                        fence_length = 0
                new_lines.append(line)
                continue

            if new_lines and self.LIST_ITEM_RE.match(line):
                prev = new_lines[-1]
                prev_stripped = prev.strip()
                if (
                    prev_stripped
                    and not self.LIST_ITEM_RE.match(prev)
                    and not prev_stripped.startswith("#")
                    and not prev_stripped.startswith("|")
                    and not prev_stripped.endswith("|")
                    and not prev_stripped.startswith(">")
                    and not prev_stripped.startswith("```")
                    and not prev_stripped.startswith("~~~")
                    and not re.match(r"^[-*_ ]{3,}$", prev_stripped)
                ):
                    new_lines.append("")

            new_lines.append(line)

        return new_lines


class LooseListExtension(Extension):
    """Python-Markdown extension registering LooseListPreprocessor."""

    def extendMarkdown(self, md: markdown_lib.Markdown) -> None:
        """Register the loose list preprocessor with Python-Markdown."""
        md.preprocessors.register(LooseListPreprocessor(md), "loose_lists", 26)


def render_markdown_doc(
    file_path: Path,
    app_label: str = "",
    theme_dict: Theme | dict[str, Any] | None = None,
    color_scheme: ColorScheme | str = ColorScheme.LIGHT,
) -> str:
    """Render a markdown file to HTML with gallery extensions and syntax highlighting."""
    if not file_path or not file_path.is_file():
        return ""
    content = file_path.read_text(encoding="utf-8")
    _, body = extract_frontmatter(content)

    resolved_color_scheme = (
        color_scheme
        if isinstance(color_scheme, ColorScheme)
        else (
            ColorScheme.DARK
            if str(color_scheme).lower() == "dark"
            else ColorScheme.LIGHT
        )
    )

    extensions: list = [
        CanvasExtension(
            app_label=app_label,
            debug=settings.DEBUG,
            theme_dict=theme_dict,
            color_scheme=resolved_color_scheme,
        ),
        RelativeLinksExtension(current_file_path=file_path),
        LooseListExtension(),
        "sane_lists",
        "fenced_code",
        "tables",
        "toc",
    ]
    extension_configs: dict = {}
    style = dds_settings.GALLERY_CODEHILITE_STYLE
    if style:
        extensions.append("codehilite")
        extension_configs["codehilite"] = {
            "css_class": "gallery-highlight",
            "noclasses": False,
            "pygments_style": style,
        }
    return mark_safe(
        markdown_lib.markdown(
            text=body,
            extensions=extensions,
            extension_configs=extension_configs,
        )
    )
