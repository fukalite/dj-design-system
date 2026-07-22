from pathlib import Path
from xml.etree import ElementTree

from dj_design_system.services.markdown_links import RelativeLinksTreeprocessor


def test_relative_links_treeprocessor(monkeypatch):
    class MockNode:
        def __init__(self, doc_path, url, children=None):
            self.doc_path = Path(doc_path)
            self.index_doc_path = None
            self.url = url
            self.children = children or []

    # Setup a fake nav tree
    fake_tree = [
        MockNode("/path/to/docs/another.md", "/gallery/another/"),
        MockNode(
            "/path/to/docs/component/index.md",
            "/gallery/component/",
            children=[
                MockNode(
                    "/path/to/docs/component/child.md", "/gallery/component/child/"
                )
            ],
        ),
    ]

    monkeypatch.setattr(
        "dj_design_system.services.navigation.build_navigation", lambda: fake_tree
    )

    processor = RelativeLinksTreeprocessor(
        md=None, current_file_path=Path("/path/to/docs/current.md")
    )

    root = ElementTree.Element("div")
    a1 = ElementTree.SubElement(root, "a", {"href": "another.md"})
    a2 = ElementTree.SubElement(root, "a", {"href": "component/index.md#section"})
    a3 = ElementTree.SubElement(root, "a", {"href": "http://external.com"})
    a4 = ElementTree.SubElement(root, "a", {"href": "/absolute/path"})
    a5 = ElementTree.SubElement(root, "a", {"href": "missing.md"})

    processor.run(root)

    assert a1.get("href") == "/gallery/another/"
    assert a2.get("href") == "/gallery/component/#section"
    assert a3.get("href") == "http://external.com"
    assert a4.get("href") == "/absolute/path"
    assert a5.get("href") == "missing.md"
