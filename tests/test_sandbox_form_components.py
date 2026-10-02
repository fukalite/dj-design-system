"""Tests for the ParamsForm and FormRow built-ins.

Both are checked for parity with the legacy sandbox form markup in
``gallery/sandbox_fragment.html``, compared after parsing, using real
parameter forms built for the example project's components.
"""

import pytest
from django.template import Context, Template

from dj_design_system.forms import build_component_form
from dj_design_system.gallery import Variant
from dj_design_system.services.media import FOUNDATION_CSS
from dj_design_system.services.registry import component_registry
from tests.html_utils import STATIC, css_homes, render, root, tags
from tests.test_navigation_components import structure


def _form(name: str, app_label: str = "demo_components", data=None):
    info = component_registry.get_by_name(name, app_label=app_label)
    return build_component_form(info.component_class)(data=data)


# ---------------------------------------------------------------------------
# FormRow
# ---------------------------------------------------------------------------

# Copied from the parameter loop in gallery/sandbox_fragment.html. The view's
# row name and description are the form field's name and help text.
LEGACY_ROW = Template(
    """<div class="gallery-params-form__row">
    <label class="gallery-params-form__label" for="{{ row.field.id_for_label }}">
        <code>{{ row.name }}</code>
        {% if row.spec.description %}<span class="gallery-params-form__hint">{{ row.spec.description }}</span>{% endif %}
    </label>
    <div class="gallery-params-form__field">
        {{ row.field }}
        {% if row.field.errors %}
            <ul class="gallery-params-form__errors gallery-params__errors">
                {% for error in row.field.errors %}<li>{{ error }}</li>{% endfor %}
            </ul>
        {% endif %}
    </div>
</div>"""
)


def legacy_row(field) -> str:
    row = {"name": field.name, "spec": {"description": field.help_text}, "field": field}
    return LEGACY_ROW.render(Context({"row": row}))


def form_row(field) -> str:
    return render("{% dds__sandbox__form_row field %}", field=field)


class TestFormRow:
    @pytest.mark.django_db  # user_card's ModelParam field lists users
    @pytest.mark.parametrize(
        "component", ["button", "alert", "quote_oneup", "user_card", "badge"]
    )
    def test_matches_legacy_for_every_field(self, component):
        form = _form(component)
        for field in form:
            assert structure(form_row(field)) == structure(legacy_row(field)), (
                field.name
            )

    def test_matches_legacy_with_errors(self):
        form = _form("button", data={"label": "Save"})
        assert form.is_valid()
        form.add_error("label", "Too long.")
        form.add_error("label", "Not <allowed>.")
        field = form["label"]
        assert structure(form_row(field)) == structure(legacy_row(field))
        assert "Not &lt;allowed&gt;." in form_row(field)

    def test_no_hint_without_help_text(self):
        form = _form("button")
        form.fields["label"].help_text = ""
        spans = [a for t, a in tags(form_row(form["label"])) if t == "span"]
        assert spans == []

    def test_accepts_an_example_dict(self):
        row = {
            "name": "variant",
            "help_text": "Visual style.",
            "value": "danger",
            "choices": ["primary", "danger"],
            "errors": ["Pick one."],
        }
        markup = form_row(row)
        assert root(markup) == ("div", {"class": "gallery-params-form__row"})
        select = dict(tags(markup))["select"]
        assert select["name"] == "variant"
        assert dict(tags(markup))["label"]["for"] == select["id"]
        assert '<option value="danger" selected>' in markup
        assert "<li>Pick one.</li>" in markup
        assert '<span class="gallery-params-form__hint">Visual style.</span>' in markup

    def test_example_dict_without_choices_is_a_text_input(self):
        markup = form_row({"name": "label", "value": "Save <me>"})
        field = dict(tags(markup))["input"]
        assert (field["type"], field["name"], field["value"]) == (
            "text",
            "label",
            "Save <me>",
        )
        assert "gallery-params__errors" not in markup

    def test_rejects_other_values(self):
        with pytest.raises((TypeError, ValueError)):
            form_row("<input>")


# ---------------------------------------------------------------------------
# ParamsForm
# ---------------------------------------------------------------------------

# Copied from gallery/sandbox_fragment.html, with the rows as block content.
LEGACY_FORM = Template(
    """<div class="gallery-sandbox__controls-wrapper" data-gallery-drawer>
    <div class="gallery-sandbox__resizer"
         role="separator"
         tabindex="0"
         aria-orientation="horizontal"
         aria-label="Resize controls drawer"
         data-gallery-resizer></div>
    <div class="gallery-sandbox__controls">
        <form method="get"
              class="gallery-params-form"
              hx-get="{{ path }}"
              hx-replace-url="true"
              hx-target="closest [data-gallery-sandbox-body]"
              hx-swap="innerHTML"
              hx-trigger="change delay:400ms, keyup delay:400ms from:input, keyup delay:400ms from:textarea">
            <input type="hidden" name="theme" value="{{ active_theme }}">
            {% if active_variant %}
                <input type="hidden" name="variant" value="{{ active_variant.name }}">
            {% endif %}
            {{ rows|safe }}
        </form>
    </div>
</div>"""
)

ROWS = '<div class="gallery-params-form__row">row</div>'


def params_form(**kwargs) -> str:
    args = " ".join(f"{k}={k}" for k in kwargs)
    return render(
        f"{{% dds__sandbox__params_form {args} %}}{{{{ rows|safe }}}}"
        "{% enddds__sandbox__params_form %}",
        rows=ROWS,
        **kwargs,
    )


class TestParamsForm:
    def test_matches_legacy(self):
        new = params_form(url="/dds/demo_components/alert/", theme="dark")
        old = LEGACY_FORM.render(
            Context(
                {
                    "path": "/dds/demo_components/alert/",
                    "active_theme": "dark",
                    "rows": ROWS,
                }
            )
        )
        assert structure(new) == structure(old)

    def test_matches_legacy_on_a_variant_page(self):
        new = params_form(
            url="/dds/demo_components/alert/", theme="dark", active_variant="critical"
        )
        old = LEGACY_FORM.render(
            Context(
                {
                    "path": "/dds/demo_components/alert/",
                    "active_theme": "dark",
                    "active_variant": Variant(name="critical"),
                    "rows": ROWS,
                }
            )
        )
        assert structure(new) == structure(old)

    def test_escapes_url_and_theme(self):
        markup = params_form(url='/x/"><b>', theme='a"b')
        form = dict(tags(markup))["form"]
        assert form["hx-get"] == '/x/"><b>'
        assert "<b>" not in markup.replace(ROWS, "")

    def test_styles_its_rows(self):
        # Its content is FormRows, so previews of it need their CSS too.
        css = component_registry.get_by_name(
            "params_form", app_label="dj_design_system"
        ).media.css
        assert "dj_design_system/ui/sandbox/form_row.css" in css

    def test_owns_the_drawer_script(self):
        info = component_registry.get_by_name(
            "params_form", app_label="dj_design_system"
        )
        assert info.media.js == ["dj_design_system/ui/sandbox/params_form.js"]
        script = (STATIC / "ui/sandbox/params_form.js").read_text()
        assert "data-gallery-resizer" in script
        assert "htmx:afterSwap" in script
        assert "data-gallery-resizer" not in (STATIC / "gallery-toolbar.js").read_text()


# ---------------------------------------------------------------------------
# Registration and CSS
# ---------------------------------------------------------------------------


class TestRegistrationAndCss:
    @pytest.mark.parametrize("name", ["params_form", "form_row"])
    def test_internal_with_dds_name(self, name):
        info = component_registry.get_by_name(name, app_label="dj_design_system")
        assert info.is_internal
        assert info.qualified_name == f"dds__sandbox__{name}"
        assert info.media.css[0] == FOUNDATION_CSS

    @pytest.mark.parametrize(
        ("selector", "owner"),
        [
            (".gallery-sandbox__controls-wrapper {", "ui/sandbox/params_form.css"),
            (".gallery-sandbox__resizer {", "ui/sandbox/params_form.css"),
            (".gallery-sandbox__resizer::after {", "ui/sandbox/params_form.css"),
            (".gallery-sandbox__controls {", "ui/sandbox/params_form.css"),
            (".gallery-params-form {", "ui/sandbox/params_form.css"),
            (".gallery-params-form__row {", "ui/sandbox/form_row.css"),
            (".gallery-params-form__label code {", "ui/sandbox/form_row.css"),
            (".gallery-params-form__hint {", "ui/sandbox/form_row.css"),
            (".gallery-params-form__field {", "ui/sandbox/form_row.css"),
            (".gallery-params__errors {", "ui/sandbox/form_row.css"),
            (".gallery-sandbox__resizer:focus-visible {", "ui/sandbox/params_form.css"),
        ],
    )
    def test_rule_lives_only_in_owner(self, selector, owner):
        assert css_homes(selector) == [owner]

    def test_dark_theme_resizer_rule_moved(self):
        assert "gallery-sandbox__resizer" not in (STATIC / "gallery.css").read_text()
