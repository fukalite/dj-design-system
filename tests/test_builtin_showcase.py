"""How the built-in components present themselves in a gallery that shows them."""

from pathlib import Path

import pytest
from django.apps import apps
from django.test import override_settings

import dj_design_system
from dj_design_system.services.navigation import build_navigation


pytestmark = pytest.mark.django_db

COMPONENTS = Path(dj_design_system.__file__).parent / "components"
GROUPS = ["canvas", "docs", "layout", "navigation", "primitives", "sandbox"]

show_builtins = override_settings(
    DJ_DESIGN_SYSTEM={
        "GALLERY_SHOW_BUILTIN_COMPONENTS": True,
        "GALLERY_IS_PUBLIC": True,
    }
)


def _builtin_app():
    return next(n for n in build_navigation() if n.slug == "dj_design_system")


class TestAppLabel:
    def test_verbose_name(self):
        assert apps.get_app_config("dj_design_system").verbose_name == (
            "Django Design System"
        )

    @show_builtins
    def test_gallery_uses_verbose_name(self):
        assert _builtin_app().label == "Django Design System"


class TestGroupPages:
    def test_every_group_folder_is_listed(self):
        folders = sorted(
            p.name
            for p in COMPONENTS.iterdir()
            if p.is_dir() and p.name != "__pycache__"
        )
        assert folders == GROUPS

    @pytest.mark.parametrize("group", ["", *GROUPS])
    def test_has_index_page(self, group):
        index = COMPONENTS / group / "index.md"
        assert index.is_file()
        text = index.read_text()
        assert text.startswith("# ")
        assert "internal" in text.lower()

    @show_builtins
    @pytest.mark.parametrize("group", ["", *GROUPS])
    def test_page_shows_the_index(self, client, group):
        app = _builtin_app()
        node = next(n for n in app.children if n.slug == group) if group else app
        heading = (COMPONENTS / group / "index.md").read_text().splitlines()[0][2:]
        response = client.get(node.url)
        assert response.status_code == 200
        assert f">{heading}</h1>" in response.content.decode()
