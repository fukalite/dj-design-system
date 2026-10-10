"""Unit tests for the built-in ``dds__params_table`` domain component."""

import dataclasses
import pathlib
import re
import types

import pytest
from django import template

from dj_design_system import components, gallery, parameters, slots
from dj_design_system.components.domain import (
    params_table as params_table_package,
)
from dj_design_system.components.domain.params_table import (
    params_table as params_table_module,
)
from dj_design_system.services import registry as registry_service
from tests import conftest


APP_LABEL = "dj_design_system"
COMPONENT_NAME = "params_table"
QUALIFIED_NAME = "dds__params_table"
RELATIVE_PATH = "domain.params_table"
TEMPLATE_PATH = (
    "dj_design_system/components/domain/params_table/params_table.html"
)
CSS_MEDIA_PATH = (
    "dj_design_system/components/domain/params_table/params_table.css"
)

PARAMS_TABLE_DIR = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "dj_design_system"
    / "components"
    / "domain"
    / "params_table"
)
PARAMS_TABLE_PY_PATH = PARAMS_TABLE_DIR / "params_table.py"
PARAMS_TABLE_HTML_PATH = PARAMS_TABLE_DIR / "params_table.html"
PARAMS_TABLE_CSS_PATH = PARAMS_TABLE_DIR / "params_table.css"
PARAMS_TABLE_INDEX_MD_PATH = PARAMS_TABLE_DIR / "index.md"
TOKENS_CSS_PATH = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "dj_design_system"
    / "static"
    / "dj_design_system"
    / "tokens.css"
)


@dataclasses.dataclass(frozen=True)
class StubParamRow:
    """Attribute-based parameter row stub for testing object normalization."""

    name: str
    type_name: str | None = None
    type: object = None
    required: bool = False
    default: object = None
    choices: tuple[object, ...] | None = None
    description: str | None = None
    spec: object = None


@dataclasses.dataclass(frozen=True)
class StubSlotRow:
    """Attribute-based slot row stub for testing slot object normalization."""

    name: str
    required: bool = False
    default: str | None = None
    description: str | None = None
    slot: object = None


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


class TestParamsTableDiscoveryAndMetadata:
    """Verify ParamsTable exports, metadata, media, and registry discovery."""

    def test_exported_from_package_init(self) -> None:
        """Verify ParamsTable is exported in dj_design_system.components.domain.params_table."""
        assert (
            params_table_package.ParamsTable
            is params_table_module.ParamsTable
        )
        assert issubclass(
            params_table_module.ParamsTable,
            components.TagComponent,
        )

    def test_template_media_and_positional_args(self) -> None:
        """Verify ParamsTable relies on co-located template_name, Media.css, and positional_args."""
        reg = _make_registry()
        info = reg.get_by_name(name=COMPONENT_NAME, app_label=APP_LABEL)
        assert info.template_name == TEMPLATE_PATH
        assert info.media.css == [CSS_MEDIA_PATH]
        assert params_table_module.ParamsTable.get_positional_args() == [
            "params",
        ]

    def test_discovered_as_dds_params_table_in_registry(self) -> None:
        """Verify ComponentRegistry discovers ParamsTable as internal dds__params_table."""
        reg = _make_registry()
        info = reg.get_by_name(name=COMPONENT_NAME, app_label=APP_LABEL)
        assert info.component_class is params_table_module.ParamsTable
        assert info.qualified_name == QUALIFIED_NAME
        assert info.relative_path == RELATIVE_PATH
        assert info.is_internal is True
        assert info.template_name == TEMPLATE_PATH
        assert info.media.css == [CSS_MEDIA_PATH]


class TestParamsTableParametersAndContext:
    """Verify parameter validation and get_context() normalization."""

    def test_default_parameters_and_empty_context(self) -> None:
        """Verify default parameters produce empty rows, default title, and default message."""
        comp = params_table_module.ParamsTable()
        ctx = comp.get_context()
        assert comp.params is None
        assert comp.slots_list is None
        assert ctx["params"] == []
        assert ctx["normalized_params"] == []
        assert ctx["slots_list"] == []
        assert ctx["normalized_slots"] == []
        assert ctx["has_params"] is False
        assert ctx["has_slots"] is False
        assert ctx["title"] == "Parameters"
        assert ctx["has_title"] is True
        assert ctx["empty_message"] == "This component has no parameters."

    def test_normalizes_tuple_spec_items(self) -> None:
        """Verify 2-tuple (name, spec) items normalize accurately."""
        label_spec = parameters.StrParam(description="Button label.")
        variant_spec = parameters.StrParam(
            description="Visual variant.",
            default="primary",
            required=False,
            choices=["primary", "secondary"],
        )
        json_spec = parameters.JSONParam(
            description="Payload data.",
            required=False,
        )
        custom_spec = types.SimpleNamespace(
            type_name="custom_type",
            required=False,
            default=0,
            choices=None,
            description="",
        )

        comp = params_table_module.ParamsTable(
            params=[
                ("label", label_spec),
                ("variant", variant_spec),
                ("payload", json_spec),
                ("count", custom_spec),
            ],
        )
        ctx = comp.get_context()
        assert ctx["has_params"] is True
        assert ctx["normalized_params"] == [
            {
                "name": "label",
                "type_name": "str",
                "required": True,
                "required_label": "Required",
                "required_variant": "error",
                "has_default": False,
                "default_display": "—",
                "choices": [],
                "has_choices": False,
                "description": "Button label.",
            },
            {
                "name": "variant",
                "type_name": "str",
                "required": False,
                "required_label": "Optional",
                "required_variant": "neutral",
                "has_default": True,
                "default_display": "primary",
                "choices": ["primary", "secondary"],
                "has_choices": True,
                "description": "Visual variant.",
            },
            {
                "name": "payload",
                "type_name": "dict | list | str | int | float | bool | NoneType",
                "required": False,
                "required_label": "Optional",
                "required_variant": "neutral",
                "has_default": False,
                "default_display": "—",
                "choices": [],
                "has_choices": False,
                "description": "Payload data.",
            },
            {
                "name": "count",
                "type_name": "custom_type",
                "required": False,
                "required_label": "Optional",
                "required_variant": "neutral",
                "has_default": True,
                "default_display": "0",
                "choices": [],
                "has_choices": False,
                "description": "—",
            },
        ]

    def test_normalizes_param_rows_and_flat_dicts_and_objects(self) -> None:
        """Verify param_rows dicts with 'spec', flat dicts, and objects normalize accurately."""
        size_spec = parameters.StrParam(
            description="Control size.",
            default="md",
            required=False,
            choices=["sm", "md", "lg"],
        )
        comp = params_table_module.ParamsTable(
            params=[
                {"name": "size", "spec": size_spec},
                {
                    "name": "disabled",
                    "type": "bool",
                    "required": False,
                    "default": False,
                    "choices": [True, False],
                    "description": "Disable control.",
                },
                {
                    "name": "retries",
                    "type": int,
                    "required": True,
                },
                StubParamRow(
                    name="untyped",
                    required=False,
                    default=None,
                    choices=None,
                    description=None,
                ),
            ],
        )
        ctx = comp.get_context()
        rows = ctx["normalized_params"]
        assert rows[0]["name"] == "size"
        assert rows[0]["type_name"] == "str"
        assert rows[0]["has_default"] is True
        assert rows[0]["default_display"] == "md"
        assert rows[0]["choices"] == ["sm", "md", "lg"]
        assert rows[0]["has_choices"] is True

        assert rows[1]["name"] == "disabled"
        assert rows[1]["type_name"] == "bool"
        assert rows[1]["has_default"] is True
        assert rows[1]["default_display"] == "False"
        assert rows[1]["choices"] == ["True", "False"]

        assert rows[2]["name"] == "retries"
        assert rows[2]["type_name"] == "int"
        assert rows[2]["required"] is True
        assert rows[2]["required_label"] == "Required"
        assert rows[2]["required_variant"] == "error"
        assert rows[2]["description"] == "—"

        assert rows[3]["name"] == "untyped"
        assert rows[3]["type_name"] == "any"
        assert rows[3]["has_default"] is False
        assert rows[3]["default_display"] == "—"
        assert rows[3]["has_choices"] is False
        assert rows[3]["description"] == "—"

    def test_normalizes_slots_list_tuples_dicts_and_objects(self) -> None:
        """Verify slots_list normalizes (name, Slot) tuples, dicts, and objects."""
        head_slot = slots.Slot(
            required=False,
            default="",
            description="Header rows.",
        )
        body_slot = slots.Slot(
            required=True,
            default="",
            description="Body rows.",
        )
        footer_slot = slots.Slot(
            required=False,
            default="<tr><td>Total</td></tr>",
            description="",
        )

        comp = params_table_module.ParamsTable(
            slots_list=[
                ("head", head_slot),
                {"name": "body", "slot": body_slot},
                StubSlotRow(name="footer", slot=footer_slot),
                {
                    "name": "actions",
                    "required": False,
                    "default": None,
                    "description": "Action buttons.",
                },
            ],
        )
        ctx = comp.get_context()
        assert ctx["has_slots"] is True
        assert ctx["normalized_slots"] == [
            {
                "name": "head",
                "required": False,
                "required_label": "Optional",
                "required_variant": "neutral",
                "has_default": False,
                "default_display": "—",
                "description": "Header rows.",
            },
            {
                "name": "body",
                "required": True,
                "required_label": "Required",
                "required_variant": "error",
                "has_default": False,
                "default_display": "—",
                "description": "Body rows.",
            },
            {
                "name": "footer",
                "required": False,
                "required_label": "Optional",
                "required_variant": "neutral",
                "has_default": True,
                "default_display": "<tr><td>Total</td></tr>",
                "description": "—",
            },
            {
                "name": "actions",
                "required": False,
                "required_label": "Optional",
                "required_variant": "neutral",
                "has_default": False,
                "default_display": "—",
                "description": "Action buttons.",
            },
        ]

    def test_invalid_parameter_types_raise_type_error(self) -> None:
        """Verify invalid parameter types raise TypeError."""
        with pytest.raises(expected_exception=TypeError, match="Expected list"):
            params_table_module.ParamsTable(params="not-a-list")
        with pytest.raises(expected_exception=TypeError, match="Expected list"):
            params_table_module.ParamsTable(slots_list="not-a-list")
        with pytest.raises(expected_exception=TypeError, match="Expected str"):
            params_table_module.ParamsTable(title=123)

    def test_python_module_purity_and_no_private_methods(self) -> None:
        """Verify params_table.py has no private helper methods or HTML string building."""
        py_text = _read_text(path=PARAMS_TABLE_PY_PATH)
        assert "format_html" not in py_text
        assert "mark_safe" not in py_text
        assert "dj_design_system.services" not in py_text
        private_methods = [
            name
            for name, value in params_table_module.ParamsTable.__dict__.items()
            if name.startswith("_")
            and not name.startswith("__")
            and callable(value)
        ]
        assert private_methods == []


class TestParamsTableRenderingAndTemplate:
    """Verify HTML rendering via template tags, child components, and template purity."""

    def test_renders_parameters_table_with_badges_defaults_and_choices(
        self,
    ) -> None:
        """Verify parameters table renders heading, compact dds__table, and dds__badge cells."""
        params_data = [
            (
                "label",
                parameters.StrParam(description="Button text."),
            ),
            (
                "variant",
                parameters.StrParam(
                    description="Visual style.",
                    default="primary",
                    required=False,
                    choices=["primary", "ghost"],
                ),
            ),
        ]
        html = _render_template(
            source="{% dds__params_table params %}",
            context={"params": params_data},
        )
        assert '<section class="dds-params-table">' in html
        assert "<l-stack>" in html
        assert "<h3 data-params-heading>Parameters</h3>" in html
        assert '<div class="dds-table" data-density="compact">' in html
        assert '<th scope="col">Name</th>' in html
        assert '<th scope="col">Type</th>' in html
        assert '<th scope="col">Requirement</th>' in html
        assert '<th scope="col">Default</th>' in html
        assert '<th scope="col">Choices</th>' in html
        assert '<th scope="col">Description</th>' in html
        assert "<code data-param-name>label</code>" in html
        assert "<code data-param-name>variant</code>" in html
        assert '<span class="dds-badge" data-variant="code">str</span>' in html
        assert (
            '<span class="dds-badge" data-variant="error">Required</span>'
            in html
        )
        assert (
            '<span class="dds-badge" data-variant="neutral">Optional</span>'
            in html
        )
        assert "<code data-param-default>primary</code>" in html
        assert "<l-cluster data-param-choices>" in html
        assert (
            '<span class="dds-badge" data-variant="code">primary</span>' in html
        )
        assert (
            '<span class="dds-badge" data-variant="code">ghost</span>' in html
        )
        assert "<span data-param-empty>—</span>" in html
        assert "<span data-param-description>Button text.</span>" in html
        assert "data-params-empty" not in html
        assert "data-slots-heading" not in html

    def test_renders_empty_state_and_omits_heading_when_title_empty(
        self,
    ) -> None:
        """Verify empty parameters render empty_message and empty title omits heading."""
        html = _render_template(
            source=(
                '{% dds__params_table params=empty_params title="" '
                'empty_message="No parameters declared." %}'
            ),
            context={"empty_params": []},
        )
        assert "data-params-heading" not in html
        assert "<p data-params-empty>No parameters declared.</p>" in html
        assert 'class="dds-table"' not in html

    def test_renders_slots_table_when_slots_list_provided(self) -> None:
        """Verify secondary Slots table renders when slots_list is non-empty."""
        slots_data = [
            (
                "head",
                slots.Slot(
                    required=False,
                    default="",
                    description="Header rows.",
                ),
            ),
            (
                "body",
                slots.Slot(
                    required=True,
                    default="",
                    description="Body rows.",
                ),
            ),
        ]
        html = _render_template(
            source="{% dds__params_table params=params slots_list=slots_list %}",
            context={"params": [], "slots_list": slots_data},
        )
        assert "<p data-params-empty>This component has no parameters.</p>" in html
        assert "<h4 data-slots-heading>Slots</h4>" in html
        assert '<div class="dds-table" data-density="compact">' in html
        assert "<code data-param-name data-slot-name>head</code>" in html
        assert "<code data-param-name data-slot-name>body</code>" in html
        assert "<span data-param-description>Header rows.</span>" in html
        assert "<span data-param-description>Body rows.</span>" in html

    def test_escapes_untrusted_html_in_fields(self) -> None:
        """Verify untrusted HTML in title, empty_message, and row fields is escaped."""
        html = _render_template(
            source=(
                "{% dds__params_table params=params title=title "
                "empty_message=empty_message %}"
            ),
            context={
                "title": "<script>alert(1)</script>",
                "params": [
                    {
                        "name": "<b>bad</b>",
                        "type_name": "<i>str</i>",
                        "required": False,
                        "default": "<img src=x>",
                        "choices": ["<a>1</a>"],
                        "description": "<svg onload=alert(1)>",
                    }
                ],
                "empty_message": "<script>evil()</script>",
            },
        )
        assert "<script>" not in html
        assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
        assert "&lt;b&gt;bad&lt;/b&gt;" in html
        assert "&lt;img src=x&gt;" in html
        assert "&lt;svg onload=alert(1)&gt;" in html

    def test_template_contains_no_filters_or_bem(self) -> None:
        """Verify params_table.html loads design_components and has no filters or BEM."""
        template_text = _read_text(path=PARAMS_TABLE_HTML_PATH)
        assert template_text.startswith("{% load design_components %}")
        assert "|" not in template_text
        bem_matches = re.findall(
            pattern=r"\.[a-z0-9-]+(?:__|--)[a-z0-9-]+",
            string=template_text,
        )
        assert not bem_matches
        assert "--" not in template_text


class TestParamsTableStylesheet:
    """Verify CUBE CSS @layer blocks, Tier 3 tokens, and formatting in params_table.css."""

    def test_wrapped_in_layer_blocks_and_sets_zero_margin(self) -> None:
        """Verify params_table.css wraps rules in @layer blocks and sets margin: 0."""
        css_text = _read_text(path=PARAMS_TABLE_CSS_PATH)
        assert css_text.startswith("@layer blocks {")
        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector=".dds-params-table",
        )
        assert root_blocks
        assert "margin: 0;" in root_blocks[0]
        assert "display: block;" in root_blocks[0]

    def test_tier_3_tokens_map_exclusively_from_defined_tier_2_tokens(
        self,
    ) -> None:
        """Verify all --_params-table-* tokens map to Tier 2 tokens defined in tokens.css."""
        css_text = _read_text(path=PARAMS_TABLE_CSS_PATH)
        tokens_text = _read_text(path=TOKENS_CSS_PATH)
        defined_tier_2 = set(
            re.findall(pattern=r"(--dds-[a-z0-9-]+)\s*:", string=tokens_text)
        )

        assert "--_dds-" not in css_text
        root_blocks = _extract_rule_blocks(
            css_text=css_text,
            selector=".dds-params-table",
        )
        root_props = _extract_defined_properties(
            block_text="\n".join(root_blocks)
        )
        assert root_props
        for name, value in root_props.items():
            assert name.startswith("--_params-table-")
            match = re.fullmatch(
                pattern=r"var\((--dds-[a-z0-9-]+)\)", string=value
            )
            assert match is not None
            assert match.group(1) in defined_tier_2

    def test_no_bem_single_quotes_and_alphabetized_declarations(self) -> None:
        """Verify zero BEM selectors, single quotes, and alphabetised declarations."""
        css_text = _read_text(path=PARAMS_TABLE_CSS_PATH)
        assert '"' not in css_text
        assert "!important" not in css_text
        assert ".dds-table" not in css_text
        assert ".dds-badge" not in css_text
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


class TestParamsTableGalleryAndDocs:
    """Verify co-located gallery.py and index.md for dds__params_table."""

    def test_gallery_config_variants_render(self) -> None:
        """Verify gallery.py exports a valid GalleryConfig whose variants all render."""
        _make_registry()
        cfg = gallery.load_gallery_config(
            source_dir=PARAMS_TABLE_DIR,
            component_name=COMPONENT_NAME,
        )
        assert isinstance(cfg, gallery.GalleryConfig)
        assert len(cfg.variants) >= 3
        for variant in cfg.variants:
            rendered = _render_template(
                source=(
                    "{% dds__params_table params=params slots_list=slots_list "
                    "title=title empty_message=empty_message %}"
                ),
                context={
                    "params": variant.kwargs.get("params", []),
                    "slots_list": variant.kwargs.get("slots_list", []),
                    "title": variant.kwargs.get("title", "Parameters"),
                    "empty_message": variant.kwargs.get(
                        "empty_message", "This component has no parameters."
                    ),
                },
            )
            assert 'class="dds-params-table"' in rendered

    def test_index_md_exists_and_documents_component(self) -> None:
        """Verify index.md exists and documents dds__params_table and its parameters."""
        doc_text = _read_text(path=PARAMS_TABLE_INDEX_MD_PATH)
        assert "dds__params_table" in doc_text
        assert "params" in doc_text
        assert "slots_list" in doc_text
        assert "title" in doc_text
        assert "empty_message" in doc_text
