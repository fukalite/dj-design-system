"""Tests for loading internal (built-in) component media in the gallery."""

import re

import pytest
from django.test import override_settings
from django.urls import reverse

from dj_design_system.services.media import (
    FOUNDATION_CSS,
    get_gallery_media,
    merge_in_order,
)
from dj_design_system.services.registry import ComponentRegistry, component_registry
from tests.conftest import discover_app_into_registry


pytestmark = pytest.mark.django_db

CRUMB_CSS = "dj_design_system/ui/fixture_media/crumb.css"
CRUMB_JS = "dj_design_system/ui/fixture_media/crumb.js"
BUILTINS = {
    "fixture_media/crumb.py": f"""
        from dj_design_system.components import TagComponent


        class CrumbComponent(TagComponent):
            template_format_str = "<span class='fixture-crumb'>crumb</span>"

            class Media:
                css = ["{FOUNDATION_CSS}", "{CRUMB_CSS}"]
                js = "{CRUMB_JS}"
    """
}


@pytest.fixture()
def global_builtins(builtin_modules):
    """Temporarily add the fixture built-ins to the global registry."""
    builtin_modules(BUILTINS)
    before = list(component_registry._components)
    discover_app_into_registry(
        component_registry, "dj_design_system", "dj_design_system"
    )
    yield
    component_registry._components[:] = before


def _position(html: str, needle: str) -> int:
    assert needle in html, f"{needle!r} not found"
    return html.index(needle)


class TestGetGalleryMedia:
    def test_foundation_only_without_builtins(self):
        media = get_gallery_media(ComponentRegistry())
        assert media.css == [FOUNDATION_CSS]
        assert media.js == []

    def test_foundation_first_and_deduplicated(self, builtin_modules):
        builtin_modules(BUILTINS)
        reg = ComponentRegistry()
        discover_app_into_registry(reg, "dj_design_system", "dj_design_system")

        media = get_gallery_media(reg)
        assert media.css[0] == FOUNDATION_CSS
        assert media.css.count(FOUNDATION_CSS) == 1
        assert CRUMB_CSS in media.css
        assert CRUMB_JS in media.js


class TestGalleryShell:
    def test_foundation_is_the_first_stylesheet(self, client):
        html = client.get(reverse("gallery")).content.decode()
        first = re.search(r'<link rel="stylesheet" href="([^"]+)"', html)
        assert first.group(1) == f"/static/{FOUNDATION_CSS}"

    def test_internal_css_loads_after_foundation(self, client, global_builtins):
        html = client.get(reverse("gallery")).content.decode()
        crumb = _position(html, f"/static/{CRUMB_CSS}")
        assert _position(html, f"/static/{FOUNDATION_CSS}") < crumb
        assert html.count(f"/static/{FOUNDATION_CSS}") == 1

    def test_internal_js_loads_before_legacy_scripts(self, client, global_builtins):
        page = reverse("gallery") + "demo_components/button/"
        html = client.get(page).content.decode()
        crumb = _position(html, f"/static/{CRUMB_JS}")
        assert crumb < _position(html, "https://unpkg.com/htmx.org")

    def test_internal_js_carries_csp_nonce(self, client, global_builtins):
        from django.test import RequestFactory

        from dj_design_system.views import gallery_index

        request = RequestFactory().get(reverse("gallery"))
        request.user = type("U", (), {"is_authenticated": True, "is_staff": True})()
        request.csp_nonce = "n0nce"
        html = gallery_index(request).content.decode()
        (tag,) = re.findall(rf'<script src="/static/{CRUMB_JS}"[^>]*>', html)
        assert 'nonce="n0nce"' in tag


class TestCanvasIframe:
    def _canvas(self, client, component: str) -> str:
        url = reverse("gallery-canvas-iframe") + f"?component={component}"
        return client.get(url).content.decode()

    def test_internal_component_canvas_loads_its_own_media(
        self, client, global_builtins
    ):
        html = self._canvas(client, "dds__fixture_media__crumb")
        assert "fixture-crumb" in html
        assert f"/static/{FOUNDATION_CSS}" in html
        assert f"/static/{CRUMB_CSS}" in html
        assert f"/static/{CRUMB_JS}" in html

    def test_consumer_canvas_excludes_internal_media(self, client, global_builtins):
        html = self._canvas(client, "demo_components__button__button")
        assert "Canvas error" not in html
        assert CRUMB_CSS not in html
        assert CRUMB_JS not in html
        assert FOUNDATION_CSS not in html


class TestInternalUsageSnippets:
    def test_usage_snippets_use_the_qualified_name(self, client, global_builtins):
        url = reverse(
            "gallery-node",
            kwargs={"app_label": "dj_design_system", "path": "fixture_media/crumb"},
        )
        with override_settings(
            DJ_DESIGN_SYSTEM={"GALLERY_SHOW_BUILTIN_COMPONENTS": True}
        ):
            context = client.get(url).context
        assert context["tag_signature"].minimal == "{% dds__fixture_media__crumb %}"
        assert context["tag_signature"].maximal == "{% dds__fixture_media__crumb %}"


class TestMergeInOrder:
    def test_keeps_first_seen_order(self):
        assert merge_in_order([["a", "b"], ["c"], ["b", "d"]]) == ["a", "b", "c", "d"]

    def test_removes_duplicates(self):
        assert merge_in_order([["a", "a", "b"], ["b"]]) == ["a", "b"]

    def test_moves_a_path_after_one_a_list_puts_first(self):
        # "x" is seen first, but the second list needs it after "p".
        assert merge_in_order([["f", "x", "y"], ["f", "p", "x"]]) == [
            "f",
            "p",
            "x",
            "y",
        ]

    def test_conflicting_lists_fall_back_to_first_seen_order(self):
        assert merge_in_order([["a", "b"], ["b", "a"]]) == ["a", "b"]

    def test_gallery_loads_code_highlight_after_page_and_prose(self):
        css = get_gallery_media().css
        highlight = "dj_design_system/ui/primitives/code_highlight.css"
        assert css.index("dj_design_system/ui/layout/page.css") < css.index(highlight)
        assert css.index("dj_design_system/ui/layout/prose.css") < css.index(highlight)

    def test_gallery_media_keeps_every_builtins_order(self):
        css = get_gallery_media().css
        for info in component_registry.list_by_app("dj_design_system"):
            positions = [css.index(path) for path in info.media.css]
            assert positions == sorted(positions), info.qualified_name
