"""Unit tests for the built-in dds__form_field element component."""

import pathlib
import re

import pytest
from django import template
from django.utils import safestring

from dj_design_system import data
from dj_design_system.components.elements import form_field as form_field_pkg
from dj_design_system.components.elements.form_field import form_field as form_field_mod
from dj_design_system.services import canvas, registry, slot_node
from tests import conftest


COMPONENT_DIR = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "dj_design_system"
    / "components"
    / "elements"
    / "form_field"
)
HTML_PATH = COMPONENT_DIR / "form_field.html"
CSS_PATH = COMPONENT_DIR / "form_field.css"
GALLERY_PATH = COMPONENT_DIR / "gallery.py"
DOCS_PATH = COMPONENT_DIR / "index.md"
CASCADE_LAYER_ORDER = "@layer reset, tokens, global, composition, blocks, utilities;"


def _make_builtin_registry() -> registry.ComponentRegistry:
    """Create a ComponentRegistry populated with built-in dj_design_system components."""
    reg = registry.ComponentRegistry()
    conftest.discover_app_into_registry(
        reg=reg,
        app_name="dj_design_system",
        app_label="dj_design_system",
    )
    return reg


def _render_template(template_source: str, context_data: dict | None = None) -> str:
    """Render a Django template string with dds__form_field and slot tags registered."""
    reg = _make_builtin_registry()
    engine = template.engines["django"].engine
    lib = template.Library()

    reg.register_templatetags(library=lib)
    lib.tag(name="slot", compile_function=slot_node.do_slot)
    previous = engine.template_libraries.get("dds_test_form_field")
    engine.template_libraries["dds_test_form_field"] = lib
    try:
        compiled = template.Template(
            template_string="{% load dds_test_form_field %}" + template_source
        )
        return compiled.render(context=template.Context(dict_=context_data or {}))
    finally:
        if previous is None:
            engine.template_libraries.pop("dds_test_form_field", None)
        else:
            engine.template_libraries["dds_test_form_field"] = previous


class TestFormFieldDiscoveryAndContract:
    """Verify component export, registry discovery, parameters, and media declarations."""

    def test_exported_in_package_init(self) -> None:
        """Verify FormField is exported from dj_design_system.components.elements.form_field."""
        assert form_field_pkg.FormField is form_field_mod.FormField

    def test_discovered_as_dds_form_field(self) -> None:
        """Verify ComponentRegistry discovers FormField as internal dds__form_field."""
        reg = _make_builtin_registry()
        info = reg.get_by_name(name="form_field", app_label="dj_design_system")
        assert info.component_class is form_field_mod.FormField
        assert info.qualified_name == "dds__form_field"
        assert info.is_internal is True
        assert form_field_mod.FormField.has_slots() is True

    def test_template_and_media_paths(self) -> None:
        """Verify template_name and Media.css match the co-located paths."""
        assert (
            form_field_mod.FormField.template_name
            == "dj_design_system/components/elements/form_field/form_field.html"
        )
        assert (
            form_field_mod.FormField.Media.css
            == "dj_design_system/components/elements/form_field/form_field.css"
        )
        reg = _make_builtin_registry()
        info = reg.get_by_name(name="form_field", app_label="dj_design_system")
        assert (
            "dj_design_system/components/elements/form_field/form_field.css"
            in info.media.css
        )

    def test_parameter_defaults_and_validation(self) -> None:
        """Verify parameter defaults, positional args, and layout choice validation."""
        assert form_field_mod.FormField.get_positional_args() == ["label"]
        slots_spec = form_field_mod.FormField.get_slots()
        assert "control" in slots_spec
        assert slots_spec["control"].required is False

        instance = form_field_mod.FormField(label="Username")
        assert instance.label == "Username"
        assert instance.field_id == ""
        assert instance.description == ""
        assert instance.error == ""
        assert instance.required_field is False
        assert instance.layout == "stacked"

        with pytest.raises(expected_exception=ValueError, match="Expected one of"):
            form_field_mod.FormField(label="Username", layout="diagonal")

    def test_get_context_computes_boolean_flags(self) -> None:
        """Verify get_context computes has_field_id, has_description, and has_error."""
        minimal = form_field_mod.FormField(label="Bio")
        min_ctx = minimal.get_context()
        assert min_ctx["has_field_id"] is False
        assert min_ctx["has_description"] is False
        assert min_ctx["has_error"] is False
        assert min_ctx["is_inline"] is False

        populated = form_field_mod.FormField(
            label="Bio",
            field_id="bio-input",
            description="Max 200 characters.",
            error="Bio cannot be blank.",
            required_field=True,
            layout="inline",
        )
        pop_ctx = populated.get_context()
        assert pop_ctx["has_field_id"] is True
        assert pop_ctx["has_description"] is True
        assert pop_ctx["has_error"] is True
        assert pop_ctx["is_inline"] is True


class TestFormFieldRendering:
    """Verify HTML rendering across slots, fallback content, layouts, and states."""

    def test_renders_control_slot_in_template(self) -> None:
        """Verify {% dds__form_field %} renders label and control slot markup."""
        html = _render_template(
            template_source=(
                '{% dds__form_field "Email" field_id="user-email" %}'
                '{% slot "control" %}<input id="user-email" type="email">{% endslot %}'
                "{% enddds__form_field %}"
            )
        )
        assert '<div class="dds-form-field" data-layout="stacked">' in html
        assert "data-invalid" not in html
        assert "<l-stack>" in html
        assert '<label for="user-email">Email</label>' in html
        assert '<input id="user-email" type="email">' in html

    def test_renders_fallback_content_when_control_slot_omitted(self) -> None:
        """Verify FormField falls back to default block content when control slot is omitted."""
        component = form_field_mod.FormField(
            content=safestring.mark_safe(s='<textarea id="notes"></textarea>'),
            label="Notes",
            field_id="notes",
        )
        html = component.render()
        assert '<label for="notes">Notes</label>' in html
        assert '<textarea id="notes"></textarea>' in html

    def test_renders_required_indicator_description_and_error_alert(self) -> None:
        """Verify required asterisk, description paragraph, and error alert paragraph."""
        html = _render_template(
            template_source=(
                '{% dds__form_field "Password" field_id="pwd" required_field=True '
                'description="At least 12 characters." error="Password is too short." %}'
                '{% slot "control" %}<input id="pwd" type="password">{% endslot %}'
                "{% enddds__form_field %}"
            )
        )
        assert (
            '<div class="dds-form-field" data-layout="stacked" data-invalid="true">'
            in html
        )
        assert (
            '<label for="pwd">Password<span aria-hidden="true">*</span></label>' in html
        )
        assert "<p>At least 12 characters.</p>" in html
        assert '<p role="alert">Password is too short.</p>' in html

    def test_renders_inline_layout_with_cluster_primitive(self) -> None:
        """Verify inline layout sets data-layout='inline' and uses <l-cluster>."""
        html = _render_template(
            template_source=(
                '{% dds__form_field "Subscribe" layout="inline" %}'
                '{% slot "control" %}<input type="checkbox">{% endslot %}'
                "{% enddds__form_field %}"
            )
        )
        assert '<div class="dds-form-field" data-layout="inline">' in html
        assert "<l-cluster>" in html
        assert "<label>Subscribe</label>" in html
        assert '<input type="checkbox">' in html

    def test_gallery_variants_render_via_canvas_service(self) -> None:
        """Verify gallery.py and index.md exist and all gallery variants render cleanly."""
        assert GALLERY_PATH.is_file()
        assert DOCS_PATH.is_file()
        reg = _make_builtin_registry()
        info = reg.get_by_name(name="form_field", app_label="dj_design_system")
        assert len(info.gallery_config.variants) >= 2
        for variant in info.gallery_config.variants:
            spec = data.CanvasSpec(
                component_name="dds__form_field",
                variant=variant.name,
            )
            rendered = canvas.render_component(spec=spec, registry=reg)
            assert 'class="dds-form-field"' in rendered


class TestFormFieldCssAndMarkupStandards:
    """Verify CUBE CSS @layer blocks, Tier 3 tokens, and styleguide compliance."""

    def test_css_uses_blocks_layer_and_tier_3_tokens_from_tier_2(self) -> None:
        """Verify form_field.css wraps rules in @layer blocks and maps Tier 3 from Tier 2 tokens."""
        css_text = CSS_PATH.read_text(encoding="utf-8")
        assert CASCADE_LAYER_ORDER in css_text
        assert "@layer blocks {" in css_text
        assert "--_dds-" not in css_text

        root_match = re.search(
            pattern=r"\.dds-form-field\s*\{([^}]*)\}",
            string=css_text,
            flags=re.DOTALL,
        )
        assert root_match
        root_block = root_match.group(1)
        assert "margin: 0;" in root_block

        tier_3_defs = re.findall(
            pattern=r"(--_form-field-[a-z0-9-]+)\s*:\s*([^;]+);",
            string=root_block,
        )
        assert len(tier_3_defs) >= 10
        for _name, value in tier_3_defs:
            assert value.strip().startswith("var(--dds-")

        for required_domain in (
            "var(--dds-control-",
            "var(--dds-status-error-",
            "var(--dds-state-focus-",
            "var(--dds-text-",
            "var(--dds-space-",
        ):
            assert required_domain in root_block

    def test_css_styles_child_controls_and_conforms_to_styleguide(self) -> None:
        """Verify child input/select/textarea rules, zero BEM, and alphabetical declarations."""
        css_text = CSS_PATH.read_text(encoding="utf-8")
        html_text = HTML_PATH.read_text(encoding="utf-8")

        for control_tag in (
            ".dds-form-field input",
            ".dds-form-field select",
            ".dds-form-field textarea",
        ):
            assert control_tag in css_text

        for text in (css_text, html_text):
            bem_matches = re.findall(
                pattern=r"\.[a-z0-9-]+(?:__|--)[a-z0-9-]+",
                string=text,
            )
            assert not bem_matches

        assert "!important" not in css_text
        assert '"' not in css_text
        for line in css_text.splitlines():
            assert line == line.rstrip()

        rule_blocks = re.findall(pattern=r"\{([^{}]+)\}", string=css_text)
        assert rule_blocks
        for block in rule_blocks:
            prop_names = re.findall(
                pattern=r"^\s*([a-z0-9_-]+)\s*:",
                string=block,
                flags=re.MULTILINE,
            )
            assert prop_names == sorted(prop_names)
