"""Unit tests for the built-in ``dds__params_form`` domain component."""

import dataclasses
import pathlib
import re
import types

import pytest
from django import forms, template
from django.utils import safestring

from dj_design_system import components, data, gallery, parameters
from dj_design_system.components.domain import (
    params_form as params_form_package,
)
from dj_design_system.components.domain.params_form import (
    params_form as params_form_module,
)
from dj_design_system.services import canvas as canvas_service
from dj_design_system.services import registry as registry_service
from tests import conftest


APP_LABEL = "dj_design_system"
COMPONENT_NAME = "params_form"
QUALIFIED_NAME = "dds__params_form"
RELATIVE_PATH = "domain.params_form"
TEMPLATE_PATH = "dj_design_system/components/domain/params_form/params_form.html"
CSS_MEDIA_PATH = "dj_design_system/components/domain/params_form/params_form.css"
JS_MEDIA_PATH = "dj_design_system/components/domain/params_form/params_form.js"

PARAMS_FORM_DIR = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "dj_design_system"
    / "components"
    / "domain"
    / "params_form"
)
PARAMS_FORM_PY_PATH = PARAMS_FORM_DIR / "params_form.py"
PARAMS_FORM_HTML_PATH = PARAMS_FORM_DIR / "params_form.html"
PARAMS_FORM_CSS_PATH = PARAMS_FORM_DIR / "params_form.css"
PARAMS_FORM_TS_PATH = PARAMS_FORM_DIR / "params_form.ts"
PARAMS_FORM_INDEX_MD_PATH = PARAMS_FORM_DIR / "index.md"
TOKENS_CSS_PATH = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "dj_design_system"
    / "static"
    / "dj_design_system"
    / "tokens.css"
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


def _render_template(
    source: str, context: dict[str, object] | None = None
) -> str:
    """Render a Django template string with built-in dds component tags registered."""
    reg = _make_registry()
    library = template.Library()
    reg.register_templatetags(library=library)
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
    escaped = re.escape(pattern=selector)
    pattern = re.compile(
        pattern=rf"{escaped}\s*\{{([^}}]*)\}}", flags=re.DOTALL
    )
    return pattern.findall(string=css_text)


def _extract_defined_properties(block_text: str) -> dict[str, str]:
    """Extract custom property definitions from a CSS block string."""
    matches = re.findall(
        pattern=r"(--[a-z0-9_-]+)\s*:\s*([^;]+);",
        string=block_text,
    )
    return {name: value.strip() for name, value in matches}


class TestParamsFormDiscoveryAndMetadata:
    """Verify ParamsForm exports, metadata, media, and registry discovery."""

    def test_exported_from_package_init(self) -> None:
        """Verify ParamsForm is exported in dj_design_system.components.domain.params_form."""
        assert (
            params_form_package.ParamsForm is params_form_module.ParamsForm
        )
        assert issubclass(
            params_form_module.ParamsForm,
            components.TagComponent,
        )

    def test_template_media_and_positional_args(self) -> None:
        """Verify ParamsForm declares co-located template_name, Media.css, Media.js, and positional_args."""
        assert params_form_module.ParamsForm.template_name == TEMPLATE_PATH
        assert params_form_module.ParamsForm.Media.css == CSS_MEDIA_PATH
        assert params_form_module.ParamsForm.Media.js == JS_MEDIA_PATH
        assert params_form_module.ParamsForm.get_positional_args() == [
            "param_rows",
        ]

    def test_discovered_as_dds_params_form_in_registry(self) -> None:
        """Verify ComponentRegistry discovers ParamsForm as internal dds__params_form."""
        reg = _make_registry()
        info = reg.get_by_name(name=COMPONENT_NAME, app_label=APP_LABEL)
        assert info.component_class is params_form_module.ParamsForm
        assert info.qualified_name == QUALIFIED_NAME
        assert info.relative_path == RELATIVE_PATH
        assert info.is_internal is True
        assert info.template_name == TEMPLATE_PATH
        assert info.media.css == [CSS_MEDIA_PATH]
        assert info.media.js == [JS_MEDIA_PATH]


class TestParamsFormParametersAndContext:
    """Verify parameter validation, __init__ normalisation, and get_context() shaping."""

    def test_default_parameters_and_empty_context(self) -> None:
        """Verify default parameters produce empty rows and default fallback values."""
        comp = params_form_module.ParamsForm()
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
        assert ctx["hx_target"] == "closest [data-gallery-sandbox-body]"
        assert (
            ctx["empty_message"]
            == "This component has no configurable parameters."
        )

    def test_normalises_active_variant_object_in_init(self) -> None:
        """Verify active_variant accepts a Variant dataclass or object with a name attribute."""
        variant_obj = gallery.Variant(
            name="secondary",
            label="Secondary Button",
            kwargs={"variant": "secondary"},
        )
        comp = params_form_module.ParamsForm(active_variant=variant_obj)
        ctx = comp.get_context()
        assert comp.active_variant == "secondary"
        assert ctx["active_variant"] == "secondary"
        assert ctx["has_active_variant"] is True

        namespace_variant = types.SimpleNamespace(name="ghost")
        comp_ns = params_form_module.ParamsForm(active_variant=namespace_variant)
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

        comp = params_form_module.ParamsForm(
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
        assert isinstance(rows[0]["field_html"], safestring.SafeString)
        assert 'name="label"' in rows[0]["field_html"]

        assert rows[1]["name"] == "count"
        assert rows[1]["field_id"] == "id_count"
        assert rows[1]["description"] == "Badge count."
        assert rows[1]["required"] is False
        assert rows[1]["errors"] == ["Enter a whole number."]
        assert rows[1]["error"] == "Enter a whole number."

        assert rows[2]["name"] == "custom_dict"
        assert rows[2]["label"] == "Custom Dict Field"
        assert rows[2]["field_id"] == "custom-id"
        assert rows[2]["description"] == "From dict spec."
        assert rows[2]["required"] is True
        assert rows[2]["errors"] == ["First error.", "Second error."]
        assert rows[2]["error"] == "First error. Second error."
        assert (
            rows[2]["field_html"]
            == '<input type="text" id="custom-id" name="custom_dict">'
        )

        assert rows[3]["name"] == "obj_param"
        assert rows[3]["label"] == "obj_param"
        assert rows[3]["field_id"] == "id_obj_param"
        assert rows[3]["description"] == "Direct row description."
        assert rows[3]["required"] is False
        assert rows[3]["errors"] == []
        assert (
            rows[3]["field_html"]
            == '<input type="text" id="id_obj_param" name="obj_param">'
        )

    def test_invalid_parameter_types_raise_type_error(self) -> None:
        """Verify invalid parameter types raise TypeError."""
        with pytest.raises(expected_exception=TypeError, match="Expected list"):
            params_form_module.ParamsForm(param_rows="not-a-list")
        with pytest.raises(expected_exception=TypeError, match="Expected str"):
            params_form_module.ParamsForm(action_url=123)
        with pytest.raises(expected_exception=TypeError, match="Expected str"):
            params_form_module.ParamsForm(active_theme=123)

    def test_python_module_purity_and_no_private_methods(self) -> None:
        """Verify params_form.py has no private helper methods, service imports, or comments."""
        py_text = _read_text(path=PARAMS_FORM_PY_PATH)
        assert "format_html" not in py_text
        assert "dj_design_system.services" not in py_text
        assert "#" not in py_text
        private_methods = [
            name
            for name, value in params_form_module.ParamsForm.__dict__.items()
            if name.startswith("_")
            and not name.startswith("__")
            and callable(value)
        ]
        assert private_methods == []


class TestParamsFormRenderingAndTemplate:
    """Verify HTML rendering via template tags, child dds__form_field delegation, and template purity."""

    def test_renders_form_with_htmx_attributes_hidden_inputs_and_form_fields(
        self,
    ) -> None:
        """Verify populated param_rows render <form data-params-form> and child dds__form_field elements."""
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
                "{% dds__params_form param_rows action_url=action_url "
                "active_theme=active_theme active_variant=active_variant %}"
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
            '<dds-params-form class="dds-params-form" data-surface="sandbox">'
            in html
        )
        assert "<form method=\"get\"" in html
        assert "data-params-form" in html
        assert (
            'action="/gallery/components/button/" '
            'hx-get="/gallery/components/button/"'
        ) in html
        assert 'hx-replace-url="true"' in html
        assert 'hx-target="closest [data-gallery-sandbox-body]"' in html
        assert 'hx-swap="innerHTML"' in html
        assert (
            'hx-trigger="change delay:400ms, keyup delay:400ms from:input, '
            'keyup delay:400ms from:textarea"'
        ) in html
        assert '<input type="hidden" name="_iss" value="1">' in html
        assert '<input type="hidden" name="_dds_theme" value="dark">' in html
        assert (
            '<input type="hidden" name="_dds_variant" value="primary">' in html
        )
        assert "<l-stack data-params-fields>" in html
        assert 'class="dds-form-field"' in html
        assert (
            '<label for="id_label">label<span aria-hidden="true">*</span></label>'
            in html
        )
        assert "<p>Primary button text.</p>" in html
        assert (
            '<input type="text" id="id_label" name="label" value="Submit">'
            in html
        )
        assert 'data-invalid="true"' in html
        assert '<p role="alert">Enter a whole number.</p>' in html
        assert "data-params-empty" not in html

    def test_omits_optional_action_and_hidden_inputs_when_empty(self) -> None:
        """Verify action, hx-get, _dds_theme, and _dds_variant are omitted when not provided."""
        html = _render_template(
            source="{% dds__params_form param_rows %}",
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
        assert 'name="_iss"' in html
        assert 'name="_dds_theme"' not in html
        assert 'name="_dds_variant"' not in html
        assert '<input type="text" id="id_title" name="title">' in html

    def test_renders_empty_state_when_no_rows(self) -> None:
        """Verify empty param_rows renders <p data-params-empty> and no <form>."""
        html = _render_template(
            source='{% dds__params_form param_rows empty_message="No editable params." %}',
            context={"param_rows": []},
        )
        assert (
            '<dds-params-form class="dds-params-form" data-surface="sandbox">'
            in html
        )
        assert "<p data-params-empty>No editable params.</p>" in html
        assert "<form" not in html

    def test_escapes_untrusted_strings(self) -> None:
        """Verify untrusted strings in labels, descriptions, errors, and empty_message are escaped."""
        html_with_rows = _render_template(
            source="{% dds__params_form param_rows active_theme=theme %}",
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
            source="{% dds__params_form empty_message=msg %}",
            context={"msg": "<script>alert(2)</script>"},
        )
        assert "<script>" not in html_empty
        assert "&lt;script&gt;alert(2)&lt;/script&gt;" in html_empty

    def test_template_contains_no_filters_or_bem(self) -> None:
        """Verify params_form.html loads design_components and contains zero filters or BEM."""
        template_text = _read_text(path=PARAMS_FORM_HTML_PATH)
        assert template_text.startswith("{% load design_components %}")
        assert "|" not in template_text
        bem_matches = re.findall(
            pattern=r"\.[a-z0-9-]+(?:__|--)[a-z0-9-]+",
            string=template_text,
        )
        assert not bem_matches


class TestParamsFormStylesheet:
    """Verify CUBE CSS @layer blocks, Tier 3 tokens, and formatting in params_form.css."""

    def test_wrapped_in_layer_blocks_and_sets_zero_margin(self) -> None:
        """Verify params_form.css wraps rules in @layer blocks without redeclaring layer order."""
        css_text = _read_text(path=PARAMS_FORM_CSS_PATH)
        assert css_text.startswith("@layer blocks {")
        assert "@layer reset" not in css_text
        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector="dds-params-form,\n  .dds-params-form",
        )
        assert root_blocks
        assert "margin: 0;" in root_blocks[0]
        assert "display: block;" in root_blocks[0]

    def test_tier_3_tokens_map_exclusively_from_defined_tier_2_tokens(
        self,
    ) -> None:
        """Verify all --_params-form-* tokens map to Tier 2 tokens defined in tokens.css."""
        css_text = _read_text(path=PARAMS_FORM_CSS_PATH)
        tokens_text = _read_text(path=TOKENS_CSS_PATH)
        defined_tier_2 = set(
            re.findall(pattern=r"(--dds-[a-z0-9-]+)\s*:", string=tokens_text)
        )

        assert "--_dds-" not in css_text
        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector="dds-params-form,\n  .dds-params-form",
        )
        root_props = _extract_defined_properties(
            block_text="\n".join(root_blocks)
        )
        assert root_props
        for name, value in root_props.items():
            assert name.startswith("--_params-form-")
            match = re.fullmatch(
                pattern=r"var\((--dds-[a-z0-9-]+)\)", string=value
            )
            assert match is not None
            assert match.group(1) in defined_tier_2

    def test_no_bem_single_quotes_and_alphabetised_declarations(self) -> None:
        """Verify zero BEM selectors, single quotes, no child leaks, and alphabetised declarations."""
        css_text = _read_text(path=PARAMS_FORM_CSS_PATH)
        assert '"' not in css_text
        assert "!important" not in css_text
        assert ".dds-form-field" not in css_text
        bem_matches = re.findall(
            pattern=r"\.[a-z0-9-]+(?:__|--)[a-z0-9-]+",
            string=css_text,
        )
        assert not bem_matches

        rule_blocks = re.findall(pattern=r"\{([^{}]+)\}", string=css_text)
        assert rule_blocks
        for block in rule_blocks:
            prop_names = re.findall(
                pattern=r"^\s*([a-z0-9_-]+)\s*:",
                string=block,
                flags=re.MULTILINE,
            )
            assert prop_names == sorted(prop_names)


class TestParamsFormGalleryAndDocs:
    """Verify co-located gallery.py and index.md for dds__params_form."""

    def test_gallery_config_variants_render_via_canvas(self) -> None:
        """Verify gallery.py exports a valid GalleryConfig whose variants all render."""
        reg = _make_registry()
        cfg = gallery.load_gallery_config(
            source_dir=PARAMS_FORM_DIR,
            component_name=COMPONENT_NAME,
        )
        assert isinstance(cfg, gallery.GalleryConfig)
        assert len(cfg.variants) >= 3
        for variant in cfg.variants:
            spec = data.CanvasSpec(
                component_name=QUALIFIED_NAME,
                variant=variant.name,
            )
            rendered = canvas_service.render_component(spec=spec, registry=reg)
            assert 'class="dds-params-form"' in rendered

    def test_index_md_exists_and_documents_component(self) -> None:
        """Verify index.md exists and documents dds__params_form and all parameters."""
        doc_text = _read_text(path=PARAMS_FORM_INDEX_MD_PATH)
        assert "dds__params_form" in doc_text
        assert "param_rows" in doc_text
        assert "action_url" in doc_text
        assert "active_theme" in doc_text
        assert "active_variant" in doc_text
        assert "hx_target" in doc_text
        assert "empty_message" in doc_text


class TestParamsFormTypeScriptCustomElement:
    """Verify Light DOM <dds-params-form> TypeScript contract in params_form.ts."""

    def test_params_form_ts_implements_custom_element_and_lifecycle_contract(
        self,
    ) -> None:
        """Verify params_form.ts defines DDSParamsFormElement with AbortController and debounce cleanup."""
        assert PARAMS_FORM_TS_PATH.is_file()
        ts_text = _read_text(path=PARAMS_FORM_TS_PATH)
        assert (
            "import type { DDSCustomElement } from '../../types.js';"
            in ts_text
        )
        assert (
            "export class DDSParamsFormElement" in ts_text
            and "extends HTMLElement" in ts_text
            and "implements DDSCustomElement" in ts_text
        )
        assert (
            "private abortController: AbortController | null = null;"
            in ts_text
        )
        assert "private debounceTimer: number | null = null;" in ts_text
        assert "connectedCallback(): void" in ts_text
        assert "disconnectedCallback(): void" in ts_text
        assert "this.abortController?.abort();" in ts_text
        assert "this.abortController = new AbortController();" in ts_text
        assert "this.abortController = null;" in ts_text
        assert "this.clearDebounceTimer();" in ts_text
        assert "window.clearTimeout(this.debounceTimer);" in ts_text
        assert (
            "this.querySelector<HTMLFormElement>('form[data-params-form]')"
            in ts_text
        )
        assert "if (!customElements.get('dds-params-form'))" in ts_text
        assert (
            "customElements.define('dds-params-form', DDSParamsFormElement);"
            in ts_text
        )

    def test_params_form_ts_serialization_reset_and_events(self) -> None:
        """Verify debounced input, change/reset listeners, serializeParams, resetParams, and dds:params-change."""
        ts_text = _read_text(path=PARAMS_FORM_TS_PATH)
        assert "const DEBOUNCE_MS = 250;" in ts_text
        for event_name in ("change", "input", "reset"):
            assert f"'{event_name}'" in ts_text
        assert "serializeParams(): Record<string, string>" in ts_text
        assert "resetParams(): void" in ts_text
        assert "new FormData(form)" in ts_text
        assert "new URLSearchParams(params).toString()" in ts_text
        assert "form.reset();" in ts_text
        assert "new CustomEvent('dds:params-change'" in ts_text
        assert "bubbles: true" in ts_text
        assert "detail: { params, queryString }" in ts_text

    def test_params_form_ts_enforces_light_dom_encapsulation_and_styleguide(
        self,
    ) -> None:
        """Verify params_form.ts uses Light DOM only, scoped queries, single quotes, and <=80 cols."""
        ts_text = _read_text(path=PARAMS_FORM_TS_PATH)
        assert "attachShadow" not in ts_text
        assert "innerHTML" not in ts_text
        assert "document.getElementById" not in ts_text
        assert "document.querySelector" not in ts_text
        assert '"' not in ts_text
        assert "\t" not in ts_text
        for line in ts_text.splitlines():
            assert len(line) <= 80
            assert line == line.rstrip()

