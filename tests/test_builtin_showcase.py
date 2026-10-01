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


class TestCanvasTheming:
    """Built-ins previewed under the example project's themes get its tokens."""

    @pytest.fixture
    def example_settings(self):
        from example_project import settings as example

        options = {**example.DJ_DESIGN_SYSTEM, "GALLERY_IS_PUBLIC": True}
        with override_settings(DJ_DESIGN_SYSTEM=options):
            yield

    def _canvas(self, client, theme):
        from django.urls import reverse

        url = reverse("gallery-canvas-iframe")
        response = client.get(
            url, {"component": "dds__primitives__divider", "theme": theme}
        )
        assert response.status_code == 200
        return response.content.decode()

    @pytest.mark.parametrize(
        ("theme", "token_class"),
        [("default", "gallery-theme-light"), ("dark", "gallery-theme-dark")],
    )
    def test_theme_sets_the_token_class(
        self, client, example_settings, theme, token_class
    ):
        html = self._canvas(client, theme)
        opening = html[html.index("<html") : html.index(">", html.index("<html"))]
        assert f'class="{token_class}"' in opening
