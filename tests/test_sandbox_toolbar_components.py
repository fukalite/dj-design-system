"""Tests for the SandboxToolbar, Popout, PopoutOption and ToggleButton built-ins.

Composed together they are checked for parity with the legacy toolbar in
``gallery/toolbar.html``, compared after parsing. The allowed differences
come from the components they reuse: ``Icon``'s classes and its
``aria-hidden``/``focusable`` on decorative SVGs.
"""

import pytest
from django.template import TemplateSyntaxError
from django.template.loader import render_to_string
from django.templatetags.static import static

from dj_design_system.gallery import Variant
from dj_design_system.services.media import FOUNDATION_CSS
from dj_design_system.services.registry import component_registry
from tests.html_utils import STATIC, css_homes, render, root, tags
from tests.test_canvas_docs_components import structure


BACKGROUNDS = [
    {"value": "white", "label": "White"},
    {"value": "dark-grey", "label": "Dark grey"},
    {"value": "theme-dark", "label": "Theme <dark>"},
]
ACTIVE_BG = "dark-grey"

VIEWPORTS = [
    ("responsive", "Responsive (fill available width)", "Responsive"),
    ("320", "Small mobile (320px)", "Small mobile — 320px"),
    ("414", "Large mobile (414px)", "Large mobile — 414px"),
    ("768", "Tablet (768px)", "Tablet — 768px"),
    ("1024", "Desktop (1024px)", "Desktop — 1024px"),
    ("1920", "Full HD (1920px)", "Full HD — 1920px"),
    ("2560", "Ultrawide (2560px)", "Ultrawide — 2560px"),
]

# The legacy toolbar, built from the components.
TOOLBAR = """
{% dds__sandbox__sandbox_toolbar variants=variants variants_url=variants_url active_variant=active_variant theme=theme %}
    {% dds__sandbox__popout panel_id="gallery-bg-panel" panel_name="bg" title="Background colour" toggle_class="gallery-sandbox-toolbar__bg-toggle" panel_attrs=bg_attrs %}
        {% slot "toggle" %}<span class="gallery-sandbox-toolbar__bg-swatch"></span>{% endslot %}
        {% slot "options" %}
            {% for bg in backgrounds %}
                {% dds__sandbox__popout_option data_name="bg" value=bg.value active=bg.active title=bg.label extra_classes="gallery-sandbox-toolbar__bg-option" %}
                    <span class="gallery-sandbox-toolbar__bg-chip gallery-sandbox-toolbar__bg-chip--{{ bg.value }} gallery-bg-chip-{{ bg.value }}"></span>
                    <span class="gallery-sandbox-toolbar__bg-option-label">{{ bg.label }}</span>
                {% enddds__sandbox__popout_option %}
            {% endfor %}
        {% endslot %}
    {% enddds__sandbox__popout %}
    {% dds__sandbox__popout panel_id="gallery-viewport-panel" panel_name="viewport" title="Viewport width" toggle_class="gallery-sandbox-toolbar__viewport-toggle" %}
        {% slot "toggle" %}{% dds__primitives__icon "monitor" %}<span class="gallery-sandbox-toolbar__viewport-value">Responsive</span>{% endslot %}
        {% slot "options" %}
            {% for vp in viewports %}
                {% dds__sandbox__popout_option data_name="viewport" value=vp.value active=vp.active title=vp.title extra_classes="gallery-sandbox-toolbar__viewport-btn" %}{{ vp.label }}{% enddds__sandbox__popout_option %}
            {% endfor %}
        {% endslot %}
    {% enddds__sandbox__popout %}
    {% dds__sandbox__popout panel_id="gallery-zoom-panel" panel_name="zoom" title="Zoom level" toggle_class="gallery-sandbox-toolbar__zoom-toggle" %}
        {% slot "toggle" %}<span class="gallery-sandbox-toolbar__zoom-value">100%</span>{% endslot %}
        {% slot "options" %}
            {% for level in zoom_levels %}
                {% dds__sandbox__popout_option data_name="zoom" value=level.value active=level.active title=level.title extra_classes="gallery-sandbox-toolbar__zoom-btn" %}{{ level.value }}%{% enddds__sandbox__popout_option %}
            {% endfor %}
        {% endslot %}
    {% enddds__sandbox__popout %}
    {% dds__sandbox__toggle_button "outline" %}
    {% dds__sandbox__toggle_button "measure" %}
    {% dds__sandbox__toggle_button "rtl" %}
{% enddds__sandbox__sandbox_toolbar %}
"""


VARIANTS = [Variant(name="critical"), Variant(name="dismissible", label="Dismiss <me>")]


def new_toolbar(variants=(), active_variant=None, theme="") -> str:
    return render(
        TOOLBAR,
        variants=list(variants),
        variants_url="/dds/demo_components/alert/",
        active_variant=active_variant.name if active_variant else "",
        theme=theme,
        bg_attrs={"data-initial-bg": ACTIVE_BG},
        backgrounds=[{**bg, "active": bg["value"] == ACTIVE_BG} for bg in BACKGROUNDS],
        viewports=[
            {"value": v, "title": t, "label": label, "active": v == "responsive"}
            for v, t, label in VIEWPORTS
        ],
        zoom_levels=[
            {"value": z, "title": f"Zoom {z}%", "active": z == "100"}
            for z in ["50", "75", "100", "125", "150", "200"]
        ],
    )


def legacy_toolbar(variants=(), active_variant=None, theme="") -> str:
    return render_to_string(
        "dj_design_system/gallery/toolbar.html",
        {
            "canvas_backgrounds": BACKGROUNDS,
            "active_bg_value": ACTIVE_BG,
            "gallery_variants": list(variants),
            "component_base_url": "/dds/demo_components/alert/",
            "active_variant": active_variant,
            "active_theme": theme,
        },
    )


def _info(name: str):
    return component_registry.get_by_name(name, app_label="dj_design_system")


class TestComposedToolbar:
    def test_matches_legacy(self):
        assert structure(new_toolbar()) == structure(legacy_toolbar())

    @pytest.mark.parametrize("active", [None, VARIANTS[1]])
    @pytest.mark.parametrize("theme", ["", "dark"])
    def test_matches_legacy_with_variant_presets(self, active, theme):
        new = new_toolbar(VARIANTS, active, theme)
        legacy = legacy_toolbar(VARIANTS, active, theme)
        assert "gallery-sandbox-toolbar__presets" in legacy
        assert structure(new) == structure(legacy)

    def test_escapes_labels(self):
        assert "Theme &lt;dark&gt;" in new_toolbar()
        assert "Theme <dark>" not in new_toolbar()


# ---------------------------------------------------------------------------
# Popout
# ---------------------------------------------------------------------------


def popout(**kwargs) -> str:
    kwargs.setdefault("panel_id", "zoom-panel")
    kwargs.setdefault("panel_name", "zoom")
    kwargs.setdefault("title", "Zoom level")
    args = " ".join(f"{k}={k}" for k in kwargs)
    return render(
        f"{{% dds__sandbox__popout {args} %}}"
        '{% slot "toggle" %}100%{% endslot %}'
        '{% slot "options" %}<b>options</b>{% endslot %}'
        "{% enddds__sandbox__popout %}",
        **kwargs,
    )


class TestPopout:
    def test_groups_its_button_and_panel(self):
        markup = popout()
        assert root(markup) == (
            "div",
            {"class": "gallery-sandbox-toolbar__group gallery-sandbox-toolbar__zoom"},
        )
        button = dict(tags(markup))["button"]
        assert button == {
            "class": "gallery-sandbox-toolbar__btn",
            "type": "button",
            "aria-expanded": "false",
            "aria-controls": "zoom-panel",
            "title": "Zoom level",
        }
        panel = [a for t, a in tags(markup) if t == "div"][1]
        assert panel == {
            "class": "gallery-sandbox-toolbar__popout",
            "id": "zoom-panel",
            "data-gallery-panel": "zoom",
            "hidden": None,
        }
        assert "<b>options</b>" in markup

    def test_toggle_class_and_panel_attrs(self):
        markup = popout(
            toggle_class="gallery-sandbox-toolbar__zoom-toggle",
            panel_attrs={"data-initial": '"><i>'},
        )
        button = dict(tags(markup))["button"]
        assert button["class"] == (
            "gallery-sandbox-toolbar__btn gallery-sandbox-toolbar__zoom-toggle"
        )
        panel = [a for t, a in tags(markup) if t == "div"][1]
        assert panel["data-initial"] == '"><i>'
        assert "<i>" not in markup

    def test_escapes_its_parameters(self):
        markup = popout(title='a"<b>', panel_id='p"<b>')
        button = dict(tags(markup))["button"]
        assert (button["title"], button["aria-controls"]) == ('a"<b>', 'p"<b>')
        assert "<b>" not in markup.replace("<b>options</b>", "")

    def test_needs_both_slots(self):
        with pytest.raises(TemplateSyntaxError, match="options"):
            render(
                '{% dds__sandbox__popout panel_id="p" panel_name="p" title="t" %}'
                '{% slot "toggle" %}x{% endslot %}{% enddds__sandbox__popout %}'
            )


# ---------------------------------------------------------------------------
# PopoutOption
# ---------------------------------------------------------------------------


class TestPopoutOption:
    def test_renders_an_option_button(self):
        markup = render(
            '{% dds__sandbox__popout_option data_name="zoom" value="50" %}'
            "50%{% enddds__sandbox__popout_option %}"
        )
        assert root(markup) == (
            "button",
            {
                "class": "gallery-sandbox-toolbar__popout-option",
                "type": "button",
                "data-zoom": "50",
            },
        )
        assert markup.endswith(">50%</button>")

    def test_active_title_and_extra_classes(self):
        markup = render(
            '{% dds__sandbox__popout_option data_name="bg" value=value active=True'
            ' title=title extra_classes="gallery-sandbox-toolbar__bg-option" %}'
            "x{% enddds__sandbox__popout_option %}",
            value='w"<b>',
            title="White <b>",
        )
        attrs = root(markup)[1]
        assert attrs["class"].split() == [
            "gallery-sandbox-toolbar__popout-option",
            "gallery-sandbox-toolbar__popout-option--active",
            "gallery-sandbox-toolbar__bg-option",
        ]
        assert (attrs["data-bg"], attrs["title"]) == ('w"<b>', "White <b>")
        assert "<b>" not in markup


# ---------------------------------------------------------------------------
# ToggleButton
# ---------------------------------------------------------------------------


class TestToggleButton:
    @pytest.mark.parametrize(
        ("name", "icon", "title"),
        [
            ("outline", "box-model", "Toggle box model outline"),
            ("measure", "ruler", "Toggle measurement overlay on hover"),
            ("rtl", "rtl", "Toggle right-to-left direction"),
        ],
    )
    def test_renders_the_named_toggle(self, name, icon, title):
        markup = render(f'{{% dds__sandbox__toggle_button "{name}" %}}')
        assert root(markup) == ("div", {"class": "gallery-sandbox-toolbar__group"})
        button = dict(tags(markup))["button"]
        assert button == {
            "class": f"gallery-sandbox-toolbar__btn gallery-sandbox-toolbar__{name}-toggle",
            "type": "button",
            "aria-pressed": "false",
            "title": title,
        }
        assert f"gallery-icon--{icon}" in dict(tags(markup))["svg"]["class"]

    def test_pressed(self):
        markup = render('{% dds__sandbox__toggle_button "rtl" pressed=True %}')
        button = dict(tags(markup))["button"]
        assert button["aria-pressed"] == "true"
        assert "gallery-sandbox-toolbar__btn--active" in button["class"].split()

    def test_rejects_unknown_toggles(self):
        with pytest.raises(ValueError):
            render('{% dds__sandbox__toggle_button "zoom" %}')


# ---------------------------------------------------------------------------
# SandboxToolbar
# ---------------------------------------------------------------------------


class TestSandboxToolbar:
    def test_wraps_its_content(self):
        markup = render(
            "{% dds__sandbox__sandbox_toolbar %}<b>tools</b>"
            "{% enddds__sandbox__sandbox_toolbar %}"
        )
        assert root(markup) == (
            "div",
            {
                "class": "gallery-sandbox-toolbar",
                "data-measure-script": static("dj_design_system/ui/sandbox/measure.js"),
            },
        )
        assert "<b>tools</b>" in markup

    def test_measure_script_moved(self):
        assert (STATIC / "ui/sandbox/measure.js").is_file()
        assert not (STATIC / "gallery-measure.js").exists()


# ---------------------------------------------------------------------------
# Scripts: gallery-toolbar.js is split between the components
# ---------------------------------------------------------------------------


def _script(name: str) -> str:
    return (STATIC / f"ui/sandbox/{name}.js").read_text()


class TestScripts:
    def test_legacy_toolbar_assets_are_gone(self):
        assert not (STATIC / "gallery-toolbar.js").exists()
        assert not (STATIC / "gallery-toolbar.css").exists()

    def test_popout_opens_and_closes_panels(self):
        script = _script("popout")
        assert "aria-expanded" in script
        assert "htmx:afterSwap" in script

    def test_sandbox_toolbar_handles_bg_viewport_and_zoom(self):
        script = _script("sandbox_toolbar")
        for hook in ("data-bg", "data-viewport", "data-zoom", "dds-theme-changed"):
            assert hook.removeprefix("data-") in script, hook
        assert "htmx:afterSwap" in script

    def test_toggle_button_handles_the_toggles(self):
        script = _script("toggle_button")
        for name in ("outline", "measure", "rtl"):
            assert f"gallery-sandbox-toolbar__{name}-toggle" in script
        assert "measureScript" in script
        assert "htmx:afterSwap" in script

    def test_each_behaviour_has_one_owner(self):
        owners = {
            "initPopout(": "popout.js",
            "applyViewportScale(": "sandbox_toolbar.js",
            "initToggle(": "toggle_button.js",
        }
        for marker, owner in owners.items():
            homes = [p.name for p in STATIC.rglob("*.js") if marker in p.read_text()]
            assert homes == [owner], marker


# ---------------------------------------------------------------------------
# Registration, Media and CSS
# ---------------------------------------------------------------------------

UI = "dj_design_system/ui"


class TestRegistrationAndMedia:
    @pytest.mark.parametrize(
        "name", ["sandbox_toolbar", "popout", "popout_option", "toggle_button"]
    )
    def test_internal_with_dds_name(self, name):
        info = _info(name)
        assert info.is_internal
        assert info.qualified_name == f"dds__sandbox__{name}"
        assert info.media.css[0] == FOUNDATION_CSS

    @pytest.mark.parametrize(
        ("name", "css", "js"),
        [
            (
                "popout",
                [
                    "primitives/button.css",
                    "sandbox/sandbox_toolbar.css",
                    "sandbox/popout.css",
                ],
                ["sandbox/popout.js"],
            ),
            ("popout_option", ["primitives/button.css"], []),
            (
                "toggle_button",
                [
                    "primitives/icon.css",
                    "primitives/button.css",
                    "sandbox/sandbox_toolbar.css",
                    "sandbox/toggle_button.css",
                ],
                ["sandbox/toggle_button.js"],
            ),
            (
                "sandbox_toolbar",
                [
                    "primitives/icon.css",
                    "primitives/button.css",
                    "sandbox/sandbox_toolbar.css",
                    "sandbox/popout.css",
                    "sandbox/toggle_button.css",
                ],
                [
                    "sandbox/popout.js",
                    "sandbox/sandbox_toolbar.js",
                    "sandbox/toggle_button.js",
                ],
            ),
        ],
    )
    def test_media(self, name, css, js):
        # Composing components list their children's assets too, so that a
        # canvas preview (which loads only the component's own Media) works.
        media = _info(name).media
        assert media.css == [FOUNDATION_CSS] + [f"{UI}/{p}" for p in css]
        assert media.js == [f"{UI}/{p}" for p in js]

    @pytest.mark.parametrize(
        ("selector", "owner"),
        [
            (".gallery-sandbox-toolbar {", "ui/sandbox/sandbox_toolbar.css"),
            (".gallery-sandbox-toolbar__group {", "ui/sandbox/sandbox_toolbar.css"),
            (".gallery-sandbox-toolbar__bg-toggle {", "ui/sandbox/sandbox_toolbar.css"),
            (".gallery-sandbox-toolbar__bg-swatch {", "ui/sandbox/sandbox_toolbar.css"),
            (".gallery-sandbox-toolbar__bg-chip {", "ui/sandbox/sandbox_toolbar.css"),
            (".gallery-bg-chip-white {", "ui/sandbox/sandbox_toolbar.css"),
            (
                ".gallery-sandbox-toolbar__zoom-value {",
                "ui/sandbox/sandbox_toolbar.css",
            ),
            (
                ".gallery-sandbox-toolbar__viewport-value {",
                "ui/sandbox/sandbox_toolbar.css",
            ),
            (".gallery-sandbox__canvas--viewport {", "ui/sandbox/sandbox_toolbar.css"),
            (".gallery-sandbox-toolbar__popout {", "ui/sandbox/popout.css"),
            (".gallery-sandbox-toolbar__popout[hidden] {", "ui/sandbox/popout.css"),
            (
                ".gallery-sandbox-toolbar__outline-toggle.gallery-sandbox-toolbar__btn--active,",
                "ui/sandbox/toggle_button.css",
            ),
        ],
    )
    def test_rule_lives_only_in_owner(self, selector, owner):
        assert css_homes(selector) == [owner]

    def test_toolbar_tokens_have_fallbacks_outside_a_toolbar(self):
        # A Popout or ToggleButton previewed on its own has no toolbar to set
        # the --toolbar-* tokens, so each use repeats the token's value.
        for name in ("popout", "toggle_button"):
            css = (STATIC / f"ui/sandbox/{name}.css").read_text()
            assert "var(--toolbar-" in css
            assert all(
                "," in use.split(")")[0] for use in css.split("var(--toolbar-")[1:]
            ), name
