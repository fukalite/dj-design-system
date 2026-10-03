"""Tests for the SearchBox, ThemeSelect and Tabs built-ins.

Each is checked for parity with the legacy markup it replaces in
``base.html`` / ``component.html``, compared after parsing. Each owns the
legacy script it replaces, loaded once per gallery page with the CSP nonce.
"""

import re

import pytest
from django.template import Context, Template
from django.test import RequestFactory
from django.urls import reverse

from dj_design_system.services.media import FOUNDATION_CSS
from dj_design_system.services.registry import component_registry
from dj_design_system.types import Theme
from tests.html_utils import STATIC, css_homes, render, root, tags
from tests.test_navigation_components import structure


SEARCH_JS = "dj_design_system/ui/navigation/search_box.js"
THEME_JS = "dj_design_system/ui/navigation/theme_select.js"
TABS_JS = "dj_design_system/ui/navigation/tabs.js"
PREVIEW_RESIZE_JS = "dj_design_system/gallery-preview-resize.js"


def _staff_request(path: str):
    request = RequestFactory().get(path)
    request.user = type("U", (), {"is_authenticated": True, "is_staff": True})()
    request.csp_nonce = "n0nce"
    return request


def _scripts(html: str, needle: str) -> list[str]:
    return re.findall(rf"<script[^>]*{re.escape(needle)}[^>]*>", html)


# ---------------------------------------------------------------------------
# SearchBox
# ---------------------------------------------------------------------------

LEGACY_SEARCH = """
<div class="gallery-sidebar__search">
    <input type="search"
           id="gallery-search-input"
           class="gallery-search-input gallery-sidebar__search-input"
           placeholder="Search..."
           autocomplete="off"
           aria-label="Search components and documentation">
</div>
<div id="gallery-search-results"
     class="gallery-search-results gallery-sidebar__search-results"
     role="listbox"
     aria-label="Search results"
     hidden></div>
"""


class TestSearchBox:
    def test_matches_legacy_markup(self):
        html = render("{% dds__navigation__search_box %}")
        assert structure(html) == structure(LEGACY_SEARCH)

    def test_owns_the_search_script(self):
        info = component_registry.get_by_name(
            "search_box", app_label="dj_design_system"
        )
        assert info.media.js == [SEARCH_JS]

    def test_result_icons_css_loads_first(self):
        # Results reuse the nav tree's type icons.
        css = component_registry.get_by_name(
            "search_box", app_label="dj_design_system"
        ).media.css
        assert css.index("dj_design_system/ui/navigation/nav_tree.css") < css.index(
            "dj_design_system/ui/navigation/search_box.css"
        )


# ---------------------------------------------------------------------------
# ThemeSelect
# ---------------------------------------------------------------------------

LEGACY_THEME_SELECT = Template(
    """
{% if available_themes|length > 1 %}
    <div class="gallery-header-theme">
        <select class="gallery-header-theme__select"
                id="gallery-global-theme-select"
                title="Global Theme">
            {% for theme_dict in available_themes %}
                <option value="{{ theme_dict.value }}"
                        {% if theme_dict.value == active_theme %}selected{% endif %}>
                    {{ theme_dict.label }}
                </option>
            {% endfor %}
        </select>
    </div>
{% endif %}
"""
)

THEMES = [
    Theme(value="default", label="Default"),
    Theme(value="dark", label="Dark"),
    Theme(value="brand", label="Brand <b>"),
]


def theme_select(themes, active: str) -> str:
    return render(
        "{% dds__navigation__theme_select themes active %}",
        themes=themes,
        active=active,
    )


class TestThemeSelect:
    @pytest.mark.parametrize("active", ["default", "dark", "missing"])
    def test_matches_legacy_markup(self, active):
        legacy = LEGACY_THEME_SELECT.render(
            Context({"available_themes": THEMES, "active_theme": active})
        )
        assert structure(theme_select(THEMES, active)) == structure(legacy)

    @pytest.mark.parametrize("count", [0, 1])
    def test_renders_nothing_with_fewer_than_two_themes(self, count):
        assert theme_select(THEMES[:count], "default") == ""

    def test_marks_the_active_theme_selected(self):
        options = [a for t, a in tags(theme_select(THEMES, "dark")) if t == "option"]
        assert [("selected" in a) for a in options] == [False, True, False]

    def test_accepts_plain_dicts(self):
        themes = [{"value": t.value, "label": t.label} for t in THEMES]
        assert structure(theme_select(themes, "dark")) == structure(
            theme_select(THEMES, "dark")
        )

    def test_escapes_labels(self):
        assert "Brand &lt;b&gt;" in theme_select(THEMES, "default")

    def test_owns_the_theme_script(self):
        info = component_registry.get_by_name(
            "theme_select", app_label="dj_design_system"
        )
        assert info.media.js == [THEME_JS]


# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

LEGACY_TABS = """
<div class="gallery-tabs"
     role="radiogroup"
     aria-label="Documentation and Sandbox view switcher">
    <input type="radio"
           name="gallery-tab"
           id="gallery-tab-docs"
           class="gallery-tabs__input"
           checked>
    <label for="gallery-tab-docs" class="gallery-tabs__label">Documentation</label>
    <input type="radio"
           name="gallery-tab"
           id="gallery-tab-sandbox"
           class="gallery-tabs__input">
    <label for="gallery-tab-sandbox" class="gallery-tabs__label">Sandbox</label>
</div>
"""

TABS = [
    {"id": "gallery-tab-docs", "label": "Documentation"},
    {"id": "gallery-tab-sandbox", "label": "Sandbox"},
]


def tabs(**kwargs) -> str:
    args = " ".join(f"{k}={k}" for k in kwargs)
    return render(f"{{% dds__navigation__tabs items {args} %}}", items=TABS, **kwargs)


class TestTabs:
    def test_matches_legacy_markup(self):
        html = tabs(label="Documentation and Sandbox view switcher")
        assert structure(html) == structure(LEGACY_TABS)

    def test_label_is_optional(self):
        assert root(tabs()) == ("div", {"class": "gallery-tabs", "role": "radiogroup"})

    def test_first_tab_is_checked_by_default(self):
        radios = [a for t, a in tags(tabs()) if t == "input"]
        assert [("checked" in a) for a in radios] == [True, False]

    def test_checks_the_given_tab(self):
        radios = [
            a for t, a in tags(tabs(checked="gallery-tab-sandbox")) if t == "input"
        ]
        assert [("checked" in a) for a in radios] == [False, True]

    def test_rejects_an_unknown_checked_tab(self):
        with pytest.raises(ValueError, match="gallery-tab-nope"):
            tabs(checked="gallery-tab-nope")

    def test_owns_the_tabs_script(self):
        info = component_registry.get_by_name("tabs", app_label="dj_design_system")
        assert info.media.js == [TABS_JS]

    def test_script_only_syncs_tabs(self):
        # The preview auto-height listener stays out of Tabs: it runs only on
        # component pages, while built-in scripts load on every gallery page.
        assert "canvas-resize" not in (STATIC / "ui/navigation/tabs.js").read_text()
        assert "canvas-resize" in (STATIC / "gallery-preview-resize.js").read_text()


# ---------------------------------------------------------------------------
# Scripts on gallery pages
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestGalleryScripts:
    def _index(self) -> str:
        from dj_design_system.views import gallery_index

        return gallery_index(_staff_request(reverse("gallery"))).content.decode()

    def _component_page(self) -> str:
        from django.urls import resolve

        path = reverse("gallery") + "demo_components/button/"
        match = resolve(path)
        return match.func(_staff_request(path), **match.kwargs).content.decode()

    @pytest.mark.parametrize("script", [SEARCH_JS, THEME_JS, TABS_JS])
    def test_loaded_once_with_nonce(self, script):
        (tag,) = _scripts(self._index(), f"/static/{script}")
        assert 'nonce="n0nce"' in tag

    @pytest.mark.parametrize(
        "legacy", ["gallery-search.js", "gallery-theme.js", "gallery-tabs.js"]
    )
    def test_legacy_scripts_are_gone(self, legacy):
        assert not (STATIC / legacy).exists()
        assert legacy not in self._index()
        assert legacy not in self._component_page()

    def test_preview_resize_listener_only_on_component_pages(self):
        assert PREVIEW_RESIZE_JS not in self._index()
        (tag,) = _scripts(self._component_page(), f"/static/{PREVIEW_RESIZE_JS}")
        assert 'nonce="n0nce"' in tag


# ---------------------------------------------------------------------------
# Registration and CSS
# ---------------------------------------------------------------------------


class TestRegistrationAndCss:
    @pytest.mark.parametrize("name", ["search_box", "theme_select", "tabs"])
    def test_internal_with_dds_name(self, name):
        info = component_registry.get_by_name(name, app_label="dj_design_system")
        assert info.is_internal
        assert info.qualified_name == f"dds__navigation__{name}"
        assert info.media.css[0] == FOUNDATION_CSS

    @pytest.mark.parametrize(
        ("selector", "owner"),
        [
            (".gallery-sidebar__search {", "search_box.css"),
            (".gallery-sidebar__search-input {", "search_box.css"),
            (".gallery-sidebar__search-input::placeholder {", "search_box.css"),
            (".gallery-sidebar__search-results {", "search_box.css"),
            (".gallery-tabs__input:focus-visible + .gallery-tabs__label {", "tabs.css"),
            (".gallery-search-result {", "search_box.css"),
            (".gallery-search-result__label mark {", "search_box.css"),
            (".gallery-search-empty {", "search_box.css"),
            (".gallery-header-theme {", "theme_select.css"),
            (".gallery-header-theme__select {", "theme_select.css"),
            (".gallery-header-theme__select:focus {", "theme_select.css"),
            (".gallery-tabs {", "tabs.css"),
            (".gallery-tabs__label {", "tabs.css"),
            (".gallery-tabs__input:checked + .gallery-tabs__label {", "tabs.css"),
        ],
    )
    def test_rule_lives_only_in_owner(self, selector, owner):
        assert css_homes(selector) == [f"ui/navigation/{owner}"]

    def test_wide_screen_tabs_rule_moved(self):
        assert ".gallery-tabs" not in (STATIC / "gallery.css").read_text()
        tabs_css = (STATIC / "ui/navigation/tabs.css").read_text()
        assert "@media (min-width: 1800px)" in tabs_css
