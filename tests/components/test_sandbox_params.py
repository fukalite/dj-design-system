"""Unit tests for the built-in ``dds__sandbox_params`` composite component."""

import dataclasses
import pathlib
import re
import types

import pytest
from django import forms, template
from django.utils import safestring

from dj_design_system import components, gallery, parameters
from dj_design_system.components.gallery.composites import (
    sandbox_params as sandbox_params_package,
)
from dj_design_system.components.gallery.composites.sandbox_params import (
    sandbox_params as sandbox_params_module,
)
from dj_design_system.services import registry as registry_service
from dj_design_system.services import slot_node as slot_node_service
from tests import conftest


APP_LABEL = "dj_design_system"
COMPONENT_NAME = "sandbox_params"
QUALIFIED_NAME = "dds__sandbox_params"
RELATIVE_PATH = "gallery.composites.sandbox_params"
TEMPLATE_PATH = (
    "dj_design_system/components/gallery/composites/sandbox_params/sandbox_params.html"
)
CSS_MEDIA_PATH = (
    "dj_design_system/components/gallery/composites/sandbox_params/sandbox_params.css"
)
JS_MEDIA_PATH = (
    "dj_design_system/components/gallery/composites/sandbox_params/sandbox_params.js"
)

SANDBOX_PARAMS_DIR = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "dj_design_system"
    / "components"
    / "gallery"
    / "composites"
    / "sandbox_params"
)
SANDBOX_PARAMS_PY_PATH = SANDBOX_PARAMS_DIR / "sandbox_params.py"
SANDBOX_PARAMS_HTML_PATH = SANDBOX_PARAMS_DIR / "sandbox_params.html"
SANDBOX_PARAMS_CSS_PATH = SANDBOX_PARAMS_DIR / "sandbox_params.css"
SANDBOX_PARAMS_TS_PATH = SANDBOX_PARAMS_DIR / "sandbox_params.ts"
SANDBOX_PARAMS_INDEX_MD_PATH = SANDBOX_PARAMS_DIR / "index.md"
TOKENS_CSS_PATH = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "dj_design_system"
    / "static"
    / "dj_design_system"
    / "tokens"
    / "semantic.css"
)


class SampleSandboxForm(forms.Form):
    """Sample Django form for testing BoundField row normalization."""

    label = forms.CharField(label="label", required=True)
    count = forms.IntegerField(label="count", required=False)


@dataclasses.dataclass(frozen=True)
class StubParamRowObject:
    """Attribute-based parameter form row stub for testing object normalization."""

    name: str
    label: str | None = None
    spec: object = None
    field: object = None
    field_id: str = ""
    description: str | None = None
    required: bool = False
    errors: tuple[str, ...] | None = None


def _make_registry() -> registry_service.ComponentRegistry:
    """Create a ComponentRegistry populated with built-in dj_design_system components."""
    reg = registry_service.ComponentRegistry()
    conftest.discover_app_into_registry(
        reg=reg,
        app_name=APP_LABEL,
        app_label=APP_LABEL,
    )
    return reg


def _render_template(source: str, context: dict[str, object] | None = None) -> str:
    """Render a Django template string with built-in dds component tags registered."""
    reg = _make_registry()
    library = template.Library()
    reg.register_templatetags(library=library)
    library.tag(name="slot", compile_function=slot_node_service.do_slot)
    engine = template.Engine(
        loaders=["dj_design_system.loaders.ComponentsTemplateLoader"],
        libraries={
            "design_components": "dj_design_system.templatetags.design_components"
        },
    )
    engine.template_builtins.append(library)
    compiled = engine.from_string(template_code=source)
    return compiled.render(context=template.Context(dict_=context or {}))


def _read_text(path: pathlib.Path) -> str:
    """Read UTF-8 text from a file path."""
    return path.read_text(encoding="utf-8")


def _extract_rule_blocks(css_text: str, selector: str) -> list[str]:
    """Extract CSS declaration blocks for a specific selector."""
    return conftest.extract_css_rule_blocks(css_text=css_text, selector=selector)


def _extract_defined_properties(block_text: str) -> dict[str, str]:
    """Extract custom property definitions from a CSS block string."""
    matches = re.findall(
        pattern=r"(--[a-z0-9_-]+)\s*:\s*([^;]+);",
        string=block_text,
    )
    return {name: value.strip() for name, value in matches}


class TestSandboxParamsDiscoveryAndMetadata:
    """Verify SandboxParams exports, metadata, media, and registry discovery."""

    def test_exported_from_package_init(self) -> None:
        """Verify SandboxParams is exported in dj_design_system.components.gallery.composites.sandbox_params."""
        assert (
            sandbox_params_package.SandboxParams is sandbox_params_module.SandboxParams
        )
        assert issubclass(
            sandbox_params_module.SandboxParams,
            components.BlockComponent,
        )
        assert "extra_inputs" in sandbox_params_module.SandboxParams.get_slots()

    def test_template_media_and_positional_args(self) -> None:
        """Verify SandboxParams relies on co-located template_name, Media.css, Media.js, and positional_args."""
        reg = _make_registry()
        info = reg.get_by_name(name=COMPONENT_NAME, app_label=APP_LABEL)
        assert info.template_name == TEMPLATE_PATH
        assert info.media.css == [CSS_MEDIA_PATH]
        assert info.media.js == [JS_MEDIA_PATH]
        assert sandbox_params_module.SandboxParams.get_positional_args() == [
            "param_rows",
        ]

    def test_discovered_as_dds_sandbox_params_in_registry(self) -> None:
        """Verify ComponentRegistry discovers SandboxParams as internal dds__sandbox_params."""
        reg = _make_registry()
        info = reg.get_by_name(name=COMPONENT_NAME, app_label=APP_LABEL)
        assert info.component_class is sandbox_params_module.SandboxParams
        assert info.qualified_name == QUALIFIED_NAME
        assert info.relative_path == RELATIVE_PATH
        assert info.is_builtin is True
        assert info.template_name == TEMPLATE_PATH
        assert info.media.css == [CSS_MEDIA_PATH]
        assert info.media.js == [JS_MEDIA_PATH]


class TestSandboxParamsParametersAndContext:
    """Verify parameter validation, __init__ normalisation, and get_context() shaping."""

    def test_default_parameters_and_empty_context(self) -> None:
        """Verify default parameters produce empty rows and no hardcoded hx_target."""
        comp = sandbox_params_module.SandboxParams()
        ctx = comp.get_context()
        assert comp.param_rows is None
        assert ctx["param_rows"] == []
        assert ctx["normalized_rows"] == []
        assert ctx["has_rows"] is False
        assert ctx["action_url"] == ""
        assert ctx["has_action_url"] is False
        assert ctx["active_theme"] == ""
        assert ctx["has_active_theme"] is False
        assert ctx["active_variant"] == ""
        assert ctx["has_active_variant"] is False
        assert ctx["hx_target"] == ""
        assert ctx["has_hx_target"] is False
        assert "DEFAULT_HX_TARGET" not in sandbox_params_module.__dict__
        assert ctx["empty_message"] == "This component has no configurable parameters."

    def test_normalises_active_variant_object_in_init(self) -> None:
        """Verify active_variant accepts a Variant dataclass or object with a name attribute."""
        variant_obj = gallery.Variant(
            name="secondary",
            label="Secondary Button",
            kwargs={"variant": "secondary"},
        )
        comp = sandbox_params_module.SandboxParams(active_variant=variant_obj)
        ctx = comp.get_context()
        assert comp.active_variant == "secondary"
        assert ctx["active_variant"] == "secondary"
        assert ctx["has_active_variant"] is True

        namespace_variant = types.SimpleNamespace(name="ghost")
        comp_ns = sandbox_params_module.SandboxParams(active_variant=namespace_variant)
        assert comp_ns.active_variant == "ghost"

    def test_normalises_dict_rows_bound_fields_and_object_rows(self) -> None:
        """Verify get_context normalises BoundField dicts, fallback field dicts, and row objects."""
        bound_form = SampleSandboxForm(
            data={"label": "Click me", "count": "not-an-int"}
        )
        assert bound_form.is_valid() is False

        label_spec = parameters.StrParam(
            description="Button text.",
            required=True,
        )
        count_spec = parameters.IntParam(
            description="Badge count.",
            required=False,
        )

        comp = sandbox_params_module.SandboxParams(
            param_rows=[
                {
                    "name": "label",
                    "spec": label_spec,
                    "field": bound_form["label"],
                },
                {
                    "name": "count",
                    "spec": count_spec,
                    "field": bound_form["count"],
                },
                {
                    "name": "custom_dict",
                    "label": "Custom Dict Field",
                    "field_id": "custom-id",
                    "spec": {
                        "description": "From dict spec.",
                        "required": True,
                    },
                    "field": None,
                    "errors": ["First error.", "Second error."],
                },
                StubParamRowObject(
                    name="obj_param",
                    label=None,
                    spec=None,
                    field=None,
                    description="Direct row description.",
                    required=False,
                    errors=None,
                ),
            ],
            action_url="/gallery/button/",
            active_theme="dark",
            active_variant="primary",
            hx_target="#sandbox-pane",
        )
        ctx = comp.get_context()
        assert ctx["has_rows"] is True
        assert ctx["action_url"] == "/gallery/button/"
        assert ctx["has_action_url"] is True
        assert ctx["active_theme"] == "dark"
        assert ctx["has_active_theme"] is True
        assert ctx["active_variant"] == "primary"
        assert ctx["has_active_variant"] is True
        assert ctx["hx_target"] == "#sandbox-pane"

        rows = ctx["normalized_rows"]
        assert len(rows) == 4

        assert rows[0]["name"] == "label"
        assert rows[0]["label"] == "label"
        assert rows[0]["field_id"] == "id_label"
        assert rows[0]["description"] == "Button text."
        assert rows[0]["required"] is True
        assert rows[0]["errors"] == []
        assert rows[0]["error"] == ""
        assert rows[0]["has_field_html"] is True
        assert isinstance(rows[0]["field_html"], safestring.SafeString)
        assert 'name="label"' in rows[0]["field_html"]

        assert rows[1]["name"] == "count"
        assert rows[1]["field_id"] == "id_count"
        assert rows[1]["description"] == "Badge count."
        assert rows[1]["required"] is False
        assert rows[1]["errors"] == ["Enter a whole number."]
        assert rows[1]["error"] == "Enter a whole number."
        assert rows[1]["has_field_html"] is True

        assert rows[2]["name"] == "custom_dict"
        assert rows[2]["label"] == "Custom Dict Field"
        assert rows[2]["field_id"] == "custom-id"
        assert rows[2]["description"] == "From dict spec."
        assert rows[2]["required"] is True
        assert rows[2]["errors"] == ["First error.", "Second error."]
        assert rows[2]["error"] == "First error. Second error."
        assert rows[2]["has_field_html"] is False
        assert rows[2]["field_html"] == ""

        assert rows[3]["name"] == "obj_param"
        assert rows[3]["label"] == "obj_param"
        assert rows[3]["field_id"] == "id_obj_param"
        assert rows[3]["description"] == "Direct row description."
        assert rows[3]["required"] is False
        assert rows[3]["errors"] == []
        assert rows[3]["has_field_html"] is False
        assert rows[3]["field_html"] == ""

    def test_invalid_parameter_types_raise_type_error(self) -> None:
        """Verify invalid parameter types raise TypeError."""
        with pytest.raises(expected_exception=TypeError, match="Expected list"):
            sandbox_params_module.SandboxParams(param_rows="not-a-list")
        with pytest.raises(expected_exception=TypeError, match="Expected str"):
            sandbox_params_module.SandboxParams(action_url=123)
        with pytest.raises(expected_exception=TypeError, match="Expected str"):
            sandbox_params_module.SandboxParams(active_theme=123)

    def test_python_module_purity_and_no_private_methods(self) -> None:
        """Verify sandbox_params.py has no private helper methods, service imports, HTML tags, or comments."""
        py_text = _read_text(path=SANDBOX_PARAMS_PY_PATH)
        assert "format_html" not in py_text
        assert "<input" not in py_text
        assert "dj_design_system.services" not in py_text
        assert "#" not in py_text
        private_methods = [
            name
            for name, value in sandbox_params_module.SandboxParams.__dict__.items()
            if name.startswith("_") and not name.startswith("__") and callable(value)
        ]
        assert private_methods == []


class TestSandboxParamsRenderingAndTemplate:
    """Verify HTML rendering via template tags, child dds__form_field delegation, and template purity."""

    def test_renders_form_with_htmx_attributes_hidden_inputs_and_form_fields(
        self,
    ) -> None:
        """Verify populated param_rows render <form data-params-form>, extra_inputs slot, and child dds__form_field elements."""
        rows_data = [
            {
                "name": "label",
                "spec": parameters.StrParam(
                    description="Primary button text.",
                    required=True,
                ),
                "field": safestring.SafeString(
                    '<input type="text" id="id_label" name="label" value="Submit">'
                ),
            },
            {
                "name": "count",
                "spec": parameters.IntParam(
                    description="Item count.",
                    required=False,
                ),
                "field": safestring.SafeString(
                    '<input type="number" id="id_count" name="count" value="bad">'
                ),
                "errors": ["Enter a whole number."],
            },
        ]
        html = _render_template(
            source=(
                '{% dds__sandbox_params param_rows action_url=action_url hx_target="[data-gallery-sandbox-body]" %}'
                '{% slot "extra_inputs" %}'
                '<input type="hidden" name="_iss" value="1">'
                '<input type="hidden" name="_dds_theme" value="{{ active_theme }}">'
                '<input type="hidden" name="_dds_variant" value="{{ active_variant.name }}">'
                "{% endslot %}"
                "{% enddds__sandbox_params %}"
            ),
            context={
                "param_rows": rows_data,
                "action_url": "/gallery/components/button/",
                "active_theme": "dark",
                "active_variant": gallery.Variant(
                    name="primary", label="Primary", kwargs={}
                ),
            },
        )
        assert (
            '<dds-sandbox-params class="dds-sandbox-params" data-surface="sandbox"'
            in html
        )
        assert '<form method="get"' in html
        assert "data-params-form" in html
        assert (
            'action="/gallery/components/button/" hx-get="/gallery/components/button/"'
        ) in html
        assert 'hx-replace-url="true"' in html
        assert 'hx-target="[data-gallery-sandbox-body]"' in html
        assert 'hx-swap="innerHTML show:none"' in html
        assert (
            'hx-trigger="change delay:400ms, keyup delay:400ms from:input, '
            'keyup delay:400ms from:textarea"'
        ) in html
        assert '<input type="hidden" name="_iss" value="1">' in html
        assert '<input type="hidden" name="_dds_theme" value="dark">' in html
        assert '<input type="hidden" name="_dds_variant" value="primary">' in html
        assert "<l-stack data-params-fields>" in html
        assert 'class="dds-form-field"' in html
        assert (
            '<label for="id_label" data-part="label">'
            'label<span data-part="required" aria-hidden="true">*</span></label>'
            in html
        )
        assert "<p>Primary button text.</p>" in html
        assert '<input type="text" id="id_label" name="label" value="Submit">' in html
        assert 'data-invalid="true"' in html
        assert '<p role="alert">Enter a whole number.</p>' in html
        assert "data-params-empty" not in html

    def test_omits_optional_action_and_hidden_inputs_when_empty(self) -> None:
        """Verify action, hx-get, hx-target, and hidden inputs are omitted when not provided."""
        html = _render_template(
            source="{% dds__sandbox_params param_rows %}{% enddds__sandbox_params %}",
            context={
                "param_rows": [
                    {
                        "name": "title",
                        "spec": None,
                        "field": None,
                    }
                ]
            },
        )
        assert "action=" not in html
        assert "hx-get=" not in html
        assert "hx-target=" not in html
        assert 'name="_iss"' not in html
        assert 'name="_dds_theme"' not in html
        assert 'name="_dds_variant"' not in html
        assert '<input type="text" id="id_title" name="title">' in html

    def test_renders_empty_state_when_no_rows(self) -> None:
        """Verify empty param_rows renders <p data-params-empty> and no <form>."""
        html = _render_template(
            source='{% dds__sandbox_params param_rows empty_message="No editable params." %}{% enddds__sandbox_params %}',
            context={"param_rows": []},
        )
        assert (
            '<dds-sandbox-params class="dds-sandbox-params" data-surface="sandbox"'
            in html
        )
        assert "<p data-params-empty>No editable params.</p>" in html
        assert "<form" not in html

    def test_escapes_untrusted_strings(self) -> None:
        """Verify untrusted strings in labels, descriptions, errors, and empty_message are escaped."""
        html_with_rows = _render_template(
            source="{% dds__sandbox_params param_rows active_theme=theme %}{% enddds__sandbox_params %}",
            context={
                "theme": '"><script>alert(1)</script>',
                "param_rows": [
                    {
                        "name": "title",
                        "label": "<b>Title</b>",
                        "description": "<script>evil()</script>",
                        "errors": ["<img src=x onerror=alert(1)>"],
                        "field": safestring.SafeString(
                            '<input type="text" id="id_title" name="title">'
                        ),
                    }
                ],
            },
        )
        assert "<script>" not in html_with_rows
        assert "&lt;b&gt;Title&lt;/b&gt;" in html_with_rows
        assert "&lt;script&gt;evil()&lt;/script&gt;" in html_with_rows
        assert "&lt;img src=x onerror=alert(1)&gt;" in html_with_rows

        html_empty = _render_template(
            source="{% dds__sandbox_params empty_message=msg %}{% enddds__sandbox_params %}",
            context={"msg": "<script>alert(2)</script>"},
        )
        assert "<script>" not in html_empty
        assert "&lt;script&gt;alert(2)&lt;/script&gt;" in html_empty

    def test_template_contains_no_filters_or_bem(self) -> None:
        """Verify sandbox_params.html loads design_components and contains zero filters, BEM, or hardcoded routing inputs."""
        template_text = _read_text(path=SANDBOX_PARAMS_HTML_PATH)
        assert template_text.startswith("{% load design_components %}")
        assert "|" not in template_text
        assert 'name="_iss"' not in template_text
        assert 'name="_dds_theme"' not in template_text
        assert 'name="_dds_variant"' not in template_text
        assert "{{ extra_inputs }}" in template_text
        bem_matches = re.findall(
            pattern=r"\.[a-z0-9-]+(?:__|--)[a-z0-9-]+",
            string=template_text,
        )
        assert not bem_matches


class TestSandboxParamsStylesheet:
    """Verify CUBE CSS @layer blocks, Tier 3 tokens, and formatting in sandbox_params.css."""

    def test_wrapped_in_layer_blocks_and_sets_zero_margin(self) -> None:
        """Verify sandbox_params.css wraps rules in @layer blocks without redeclaring layer order."""
        css_text = _read_text(path=SANDBOX_PARAMS_CSS_PATH)
        assert css_text.startswith("@layer blocks {")
        assert "@layer reset" not in css_text
        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector="dds-sandbox-params,\n  .dds-sandbox-params",
        )
        assert root_blocks
        assert "margin: 0;" in root_blocks[0]
        assert "display: block;" in root_blocks[0]

    def test_tier_3_tokens_map_exclusively_from_defined_tier_2_tokens(
        self,
    ) -> None:
        """Verify all --_params-form-* tokens map to Tier 2 tokens defined in tokens.css."""
        css_text = _read_text(path=SANDBOX_PARAMS_CSS_PATH)
        tokens_text = _read_text(path=TOKENS_CSS_PATH)
        defined_tier_2 = set(
            re.findall(pattern=r"(--dds-[a-z0-9-]+)\s*:", string=tokens_text)
        )

        assert "--_dds-" not in css_text
        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector="dds-sandbox-params,\n  .dds-sandbox-params",
        )
        root_props = _extract_defined_properties(block_text="\n".join(root_blocks))
        assert root_props
        for name, value in root_props.items():
            assert name.startswith("--_sandbox-params-")
            match = re.fullmatch(pattern=r"var\((--dds-[a-z0-9-]+)\)", string=value)
            assert match is not None
            assert match.group(1) in defined_tier_2

    def test_css_boundary_encapsulation(self) -> None:
        """Verify child component selectors do not leak into sandbox_params.css and native nesting is used."""
        css_text = _read_text(path=SANDBOX_PARAMS_CSS_PATH)
        assert ".dds-form-field" not in css_text
        assert "--_sandbox-params-fields-gap" not in css_text
        assert "--_sandbox-params-padding" not in css_text
        assert "& [data-params-fields]" in css_text


class TestSandboxParamsGalleryAndDocs:
    """Verify co-located gallery.py and index.md for dds__sandbox_params."""

    def test_gallery_config_variants_render_via_canvas(self) -> None:
        """Verify gallery.py exports a valid GalleryConfig with leaf node configuration."""
        cfg = gallery.load_gallery_config(
            source_dir=SANDBOX_PARAMS_DIR,
            component_name=COMPONENT_NAME,
        )
        assert isinstance(cfg, gallery.GalleryConfig)
        assert cfg.variants == []
        rendered = sandbox_params_module.SandboxParams(**cfg.param_defaults).render()
        assert 'class="dds-sandbox-params"' in rendered

    def test_index_md_exists_and_documents_component(self) -> None:
        """Verify index.md exists and documents dds__sandbox_params and all parameters."""
        doc_text = _read_text(path=SANDBOX_PARAMS_INDEX_MD_PATH)
        assert "```canvas" in doc_text
        assert "dds__sandbox_params" in doc_text
        assert "param_rows" in doc_text
        assert "action_url" in doc_text
        assert "active_theme" in doc_text
        assert "active_variant" in doc_text
        assert "hx_target" in doc_text
        assert "empty_message" in doc_text
