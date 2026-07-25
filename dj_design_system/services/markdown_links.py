from __future__ import annotations

import urllib.parse
from pathlib import Path
from typing import TYPE_CHECKING

from markdown.extensions import Extension
from markdown.treeprocessors import Treeprocessor


if TYPE_CHECKING:
    from xml.etree import ElementTree

    from markdown import Markdown

    from dj_design_system.data import NavNode


class RelativeLinksTreeprocessor(Treeprocessor):
    """Treeprocessor that rewrites relative links to match gallery URLs."""

    def __init__(self, md: Markdown, current_file_path: Path):
        super().__init__(md)
        self.current_file_path = current_file_path
        self._path_to_url: dict[Path, str] | None = None

    def _build_mapping(self) -> dict[Path, str]:
        from dj_design_system.services.navigation import build_navigation

        mapping: dict[Path, str] = {}

        def traverse(node: NavNode) -> None:
            if getattr(node, "doc_path", None) is not None:
                doc_path: Path = node.doc_path  # type: ignore[assignment]
                mapping[doc_path.resolve()] = node.url
            if getattr(node, "index_doc_path", None) is not None:
                index_doc_path: Path = node.index_doc_path  # type: ignore[assignment]
                mapping[index_doc_path.resolve()] = node.url
            for child in node.children:
                traverse(child)

        nav_tree = build_navigation()
        for app_node in nav_tree:
            traverse(app_node)

        return mapping

    def run(self, root: ElementTree.Element) -> None:
        for element in root.iter():
            if element.tag == "a":
                href = element.get("href")
                if not href or href.startswith(
                    ("http://", "https://", "mailto:", "/", "#")
                ):
                    continue

                parts = urllib.parse.urlsplit(href)
                if not parts.path:
                    continue

                target_path = (self.current_file_path.parent / parts.path).resolve()

                if self._path_to_url is None:
                    self._path_to_url = self._build_mapping()

                if target_path in self._path_to_url:
                    new_url = self._path_to_url[target_path]
                    if parts.fragment:
                        new_url = f"{new_url}#{parts.fragment}"
                    element.set("href", new_url)


class RelativeLinksExtension(Extension):
    """Markdown extension to rewrite relative links to other markdown files."""

    def __init__(self, current_file_path: Path, **kwargs):
        self.current_file_path = current_file_path
        super().__init__(**kwargs)

    def extendMarkdown(self, md: Markdown) -> None:
        md.treeprocessors.register(
            RelativeLinksTreeprocessor(md, self.current_file_path),
            "relative_links",
            10,
        )
