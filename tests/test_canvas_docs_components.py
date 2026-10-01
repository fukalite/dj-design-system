"""Tests for the CanvasWidget, UsageExample and ParamsTable built-ins.

Each is checked for parity with the legacy markup it replaces, compared
after parsing. The allowed differences come from the components they reuse:
``Icon``'s classes and its ``aria-hidden``/``focusable`` on decorative SVGs,
and ``IconButton``'s ``aria-label``.
"""

import html
import re
from html.parser import HTMLParser
from pathlib import Path

import pytest
from django.template import Context, Template

from dj_design_system.parameters import BoolParam, StrParam
from dj_design_system.parameters.base import _get_type_name
from dj_design_system.services.media import FOUNDATION_CSS
from dj_design_system.services.registry import component_registry
from dj_design_system.services.tag_signature import highlight_code, highlight_html
from tests.html_utils import STATIC, css_homes, render, tags


class _Events(HTMLParser):
    def __init__(self):
        super().__init__()
        self.events: list = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = [
            c
            for c in (attrs.pop("class", "") or "").split()
            if not c.startswith("gallery-icon")
        ]
        if tag == "svg":
            attrs.pop("aria-hidden", None)
            attrs.pop("focusable", None)
        if "gallery-doc-preview__sandbox-link" in classes:
            attrs.pop("aria-label", None)
        if classes:
            attrs["class"] = " ".join(sorted(classes))
        self.events.append(("start", tag, tuple(sorted(attrs.items()))))

    def handle_endtag(self, tag):
        self.events.append(("end", tag))

    def handle_data(self, data):
        if data.strip():
            self.events.append(("text", " ".join(data.split())))


def structure(markup: str) -> list:
    parser = _Events()
    parser.feed(markup)
    return parser.events


def _code_texts(markup: str) -> list[str]:
    """The exact inner HTML of every <code> element, for whitespace checks."""
    return re.findall(r"<code[^>]*>(.*?)</code>", markup, flags=re.S)


# ---------------------------------------------------------------------------
# CodeBlock's bare variant
# ---------------------------------------------------------------------------


class TestBareCodeBlock:
    def test_renders_a_plain_pre_and_code(self):
        markup = render(
            '{% dds__primitives__code_block language="django" variant="bare" %}'
            "{{ src }}{% enddds__primitives__code_block %}",
            src='{% alert "info" %}',
        )
        assert [t for t in tags(markup)][:2] == [("pre", {}), ("code", {})]
        assert _code_texts(markup) == [highlight_code('{% alert "info" %}').rstrip()]

    def test_block_is_the_default(self):
        markup = render(
            "{% dds__primitives__code_block %}x{% enddds__primitives__code_block %}"
        )
        assert tags(markup)[0] == ("pre", {"class": "gallery-usage__pre"})

    def test_rejects_unknown_variants(self):
        with pytest.raises(ValueError, match="got nope"):
            render(
                '{% dds__primitives__code_block variant="nope" %}'
                "x{% enddds__primitives__code_block %}"
            )


# ---------------------------------------------------------------------------
# CanvasWidget
# ---------------------------------------------------------------------------

SOURCE = '{% alert "info" %}\n    Sample & <content>\n{% endalert %}'
OUTPUT = "\n<div class='alert alert-info info' role='alert'>Sample</div>\n"


# canvas_widget.html as it was before it became a wrapper around CanvasWidget.
LEGACY_WIDGET = (
    Path(__file__).parent / "legacy_partials" / "templates" / "canvas_widget.html"
)


def widget_context(**overrides) -> dict:
    """canvas_widget.html's context, fed exactly as its two callers fed it."""
    return {
        "unique_id": "sandbox",
        "source_html": highlight_code(SOURCE) or html.escape(SOURCE),
        "rendered_output_html": highlight_html(OUTPUT.strip())
        or html.escape(OUTPUT.strip()),
        **overrides,
    }


def legacy_widget(**overrides) -> str:
    """The legacy template's output."""
    return Template(LEGACY_WIDGET.read_text()).render(
        Context(widget_context(**overrides))
    )


def widget(**kwargs) -> str:
    kwargs = {
        "unique_id": "sandbox",
        "template_source": SOURCE,
        "rendered_output": OUTPUT,
        **kwargs,
    }
    args = " ".join(f"{k}={k}" for k in kwargs)
    return render(f"{{% dds__canvas__canvas_widget {args} %}}", **kwargs)


class TestCanvasWidget:
    def test_matches_legacy_with_src(self):
        kwargs = {
            "iframe_src": "/dds/_canvas/?component=alert",
            "iframe_class": "gallery-sandbox__iframe",
            "extra_classes": "gallery-sandbox__widget",
        }
        assert structure(widget(**kwargs)) == structure(legacy_widget(**kwargs))

    def test_matches_legacy_with_srcdoc_and_sandbox(self):
        srcdoc = '<!DOCTYPE html><html><body><p class="x">"hi" & bye</p></body></html>'
        new = widget(unique_id="3", iframe_srcdoc=srcdoc, sandbox_attrs="allow-scripts")
        old = legacy_widget(
            unique_id="3", iframe_srcdoc=srcdoc, sandbox_attrs="allow-scripts"
        )
        assert structure(new) == structure(old)

    def test_code_panes_match_legacy_highlighting(self):
        new = _code_texts(widget(iframe_src="/x/"))
        old = _code_texts(legacy_widget(iframe_src="/x/"))
        # Pygments ends its output with a newline; CodeBlock trims it.
        assert new == [text.rstrip("\n") for text in old]

    def test_iframe_class_defaults_to_the_markdown_canvas(self):
        iframe = dict(tags(widget(iframe_src="/x/")))["iframe"]
        assert iframe["class"] == "gallery-canvas gallery-md-canvas__iframe"
        assert iframe["data-canvas-id"] == "sandbox"
        assert "sandbox" not in iframe

    def test_needs_exactly_one_iframe_source(self):
        with pytest.raises(ValueError, match="iframe_src or iframe_srcdoc"):
            widget()
        with pytest.raises(ValueError, match="iframe_src or iframe_srcdoc"):
            widget(iframe_src="/x/", iframe_srcdoc="<p>x</p>")

    def test_uses_icons(self):
        classes = [a.get("class", "") for t, a in tags(widget(iframe_src="/x/"))]
        for name in ["eye", "code", "file-code"]:
            assert f"gallery-icon gallery-icon--{name}" in classes

    def test_owns_the_preview_resize_script(self):
        info = component_registry.get_by_name(
            "canvas_widget", app_label="dj_design_system"
        )
        assert info.media.js == ["dj_design_system/ui/canvas/canvas_widget.js"]
        script = (STATIC / "ui/canvas/canvas_widget.js").read_text()
        assert '"canvas-resize"' in script
        assert not (STATIC / "gallery-preview-resize.js").exists()


# ---------------------------------------------------------------------------
# UsageExample
# ---------------------------------------------------------------------------

# Copied from the Usage section of gallery/component.html.
LEGACY_USAGE = Template(
    """{% load static %}
<div class="gallery-usage__block">
    <h4 class="gallery-usage__heading">{{ heading }}</h4>
    {% if preview_url %}
        <div class="gallery-doc-preview">
            <iframe class="gallery-canvas gallery-doc-preview__iframe"
                    src="{{ preview_url }}"
                    name="{{ preview_id }}"
                    data-canvas-id="{{ preview_id }}"
                    title="{{ preview_title }}"></iframe>
            <a class="gallery-doc-preview__sandbox-link"
               href="#pane-sandbox"
               title="Open in sandbox">
                <svg width="14"
                     height="14"
                     viewBox="0 0 24 24"
                     fill="none"
                     stroke="currentColor"
                     stroke-width="2"
                     stroke-linecap="round"
                     stroke-linejoin="round">
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                    <polyline points="15 3 21 3 21 9" /><line x1="10" y1="14" x2="21" y2="3" />
                </svg>
            </a>
        </div>
    {% endif %}
    <pre class="gallery-usage__pre"><code class="gallery-usage__code">{{ code_html|safe }}</code></pre>
</div>
"""
)

USAGE = '{% alert "info" %}\nSample content\n{% endalert %}'


def usage(**kwargs) -> str:
    kwargs = {"heading": "Minimal example", "code": USAGE, **kwargs}
    args = " ".join(f"{k}={k}" for k in kwargs)
    return render(f"{{% dds__docs__usage_example {args} %}}", **kwargs)


def legacy_usage(**context) -> str:
    context = {
        "heading": "Minimal example",
        "code_html": highlight_code(USAGE),
        **context,
    }
    return LEGACY_USAGE.render(Context(context))


class TestUsageExample:
    def test_matches_legacy_with_a_preview(self):
        preview = {
            "preview_url": "/dds/_canvas/?component=alert&mode=basic",
            "preview_id": "minimal",
            "preview_title": "Minimal example preview",
        }
        assert structure(usage(**preview)) == structure(legacy_usage(**preview))

    def test_matches_legacy_without_a_preview(self):
        assert structure(usage(heading="Qualified tag usage")) == structure(
            legacy_usage(heading="Qualified tag usage")
        )

    def test_code_matches_legacy_highlighting(self):
        assert _code_texts(usage()) == [highlight_code(USAGE).rstrip("\n")]

    def test_preview_needs_an_id_and_title(self):
        with pytest.raises(ValueError, match="preview_id and preview_title"):
            usage(preview_url="/x/")

    def test_css_follows_the_canvas_css(self):
        css = component_registry.get_by_name(
            "usage_example", app_label="dj_design_system"
        ).media.css
        assert css.index("dj_design_system/ui/canvas/canvas_widget.css") < css.index(
            "dj_design_system/ui/docs/usage_example.css"
        )


# ---------------------------------------------------------------------------
# ParamsTable
# ---------------------------------------------------------------------------

# Copied from the Parameters section of gallery/component.html.
LEGACY_PARAMS = Template(
    """{% if params %}
<table class="gallery-params">
    <thead>
        <tr>
            <th>Name</th>
            <th>Type</th>
            <th>Required</th>
            <th>Default</th>
            <th>Choices</th>
            <th>Description</th>
        </tr>
    </thead>
    <tbody>
        {% for name, spec in params %}
            <tr>
                <td>
                    <code>{{ name }}</code>
                </td>
                <td>
                    <code>{{ spec.type_name }}</code>
                </td>
                <td>{{ spec.required|yesno:"Yes,No" }}</td>
                <td>
                    {% if spec.default is not None %}
                        <code>{{ spec.default }}</code>
                    {% else %}
                        —
                    {% endif %}
                </td>
                <td>
                    {% if spec.choices %}
                        {% for choice in spec.choices %}
                            <code>{{ choice }}</code>
                            {% if not forloop.last %},{% endif %}
                        {% endfor %}
                    {% else %}
                        —
                    {% endif %}
                </td>
                <td>{{ spec.description|default:"—" }}</td>
            </tr>
        {% endfor %}
    </tbody>
</table>
{% else %}
<p>This component has no parameters.</p>
{% endif %}
"""
)

PARAMS = [
    ("level", StrParam("Alert level <b>", choices=["info", "warning"])),
    ("items", StrParam("", required=False, default="")),
    ("dismissible", BoolParam("Can be closed.", required=False, default=False)),
]


def params_table(params) -> str:
    return render("{% dds__docs__params_table params %}", params=params)


class TestParamsTable:
    def test_matches_legacy(self):
        for _, spec in PARAMS:  # as the component view prepares them
            spec.type_name = _get_type_name(spec.type)
        legacy = LEGACY_PARAMS.render(Context({"params": PARAMS}))
        assert structure(params_table(PARAMS)) == structure(legacy)

    def test_no_parameters(self):
        assert structure(params_table([])) == structure(
            "<p>This component has no parameters.</p>"
        )

    def test_accepts_plain_dicts(self):
        rows = [
            {
                "name": name,
                "type_name": _get_type_name(spec.type),
                "required": spec.required,
                "default": spec.default,
                "choices": spec.choices,
                "description": spec.description,
            }
            for name, spec in PARAMS
        ]
        assert structure(params_table(rows)) == structure(params_table(PARAMS))

    def test_uses_the_table_component(self):
        assert tags(params_table(PARAMS))[0] == ("table", {"class": "gallery-params"})


# ---------------------------------------------------------------------------
# Registration, CSS and scripts
# ---------------------------------------------------------------------------


class TestRegistrationAndAssets:
    @pytest.mark.parametrize(
        ("name", "qualified"),
        [
            ("canvas_widget", "dds__canvas__canvas_widget"),
            ("usage_example", "dds__docs__usage_example"),
            ("params_table", "dds__docs__params_table"),
        ],
    )
    def test_internal_with_dds_name(self, name, qualified):
        info = component_registry.get_by_name(name, app_label="dj_design_system")
        assert info.is_internal
        assert info.qualified_name == qualified
        assert info.media.css[0] == FOUNDATION_CSS

    @pytest.mark.parametrize(
        ("selector", "owner"),
        [
            (".gallery-canvas {", "ui/canvas/canvas_widget.css"),
            (".gallery-md-canvas {", "ui/canvas/canvas_widget.css"),
            (".gallery-md-canvas__toggles {", "ui/canvas/canvas_widget.css"),
            (".gallery-md-canvas__iframe {", "ui/canvas/canvas_widget.css"),
            (".gallery-usage {", "ui/docs/usage_example.css"),
            (".gallery-usage__block {", "ui/docs/usage_example.css"),
            (".gallery-doc-preview {", "ui/docs/usage_example.css"),
            (".gallery-doc-preview__iframe {", "ui/docs/usage_example.css"),
        ],
    )
    def test_rule_lives_only_in_owner(self, selector, owner):
        assert css_homes(selector) == [owner]

    def test_markdown_canvas_stylesheet_moved(self):
        assert not (STATIC / "gallery-markdown.css").exists()

    @pytest.mark.django_db
    def test_gallery_pages_no_longer_link_the_legacy_assets(self, client):
        from django.urls import reverse

        page = client.get(reverse("gallery") + "demo_components/button/")
        content = page.content.decode()
        assert "gallery-markdown.css" not in content
        assert "gallery-preview-resize.js" not in content
        assert "/static/dj_design_system/ui/canvas/canvas_widget.js" in content

    def test_works_out_type_names(self):
        spec = StrParam("Fresh from get_params.")
        assert not hasattr(spec, "type_name")
        assert "<code>str</code>" in params_table([("label", spec)])


class TestComposedMedia:
    """A canvas loads only the component's own Media, so a component that
    renders others must list their stylesheets too."""

    @pytest.mark.parametrize(
        ("name", "children"),
        [
            ("canvas_widget", ["icon", "code_block"]),
            ("usage_example", ["section_heading", "icon_button", "code_block"]),
            ("params_table", ["table"]),
        ],
    )
    def test_includes_its_childrens_css(self, name, children):
        own = component_registry.get_by_name(name, app_label="dj_design_system")
        for child in children:
            info = component_registry.get_by_name(child, app_label="dj_design_system")
            missing = [c for c in info.media.css if c not in own.media.css]
            assert missing == [], f"{name} is missing {child}'s {missing}"
