"""Unit tests for the built-in dds__table component."""

import pathlib
import re

import pytest
from django import template as django_template
from django.utils import safestring

from dj_design_system import components
from dj_design_system.components.elements import table as table_package
from dj_design_system.components.elements.table import table as table_module
from dj_design_system.services import registry as registry_service
from tests import conftest


BlockComponent = components.BlockComponent
ComponentRegistry = registry_service.ComponentRegistry
Context = django_template.Context
DENSITY_COMPACT = table_module.DENSITY_COMPACT
DENSITY_DEFAULT = table_module.DENSITY_DEFAULT
DirectTable = table_module.Table
Table = table_package.Table
Template = django_template.Template
TemplateSyntaxError = django_template.TemplateSyntaxError
discover_app_into_registry = conftest.discover_app_into_registry
mark_safe = safestring.mark_safe


APP_LABEL = "dj_design_system"
BODY_HTML = "<tr><td>Alpha</td><td>1</td></tr>"
CAPTION_TEXT = "Quarterly metrics"
CSS_REL_PATH = "dj_design_system/components/elements/table/table.css"
HEAD_HTML = '<tr><th scope="col">Name</th><th scope="col">Value</th></tr>'
QUALIFIED_TAG = "dds__table"
TABLE_DIR = (
    pathlib.Path(__file__).resolve().parent.parent.parent
    / "dj_design_system"
    / "components"
    / "elements"
    / "table"
)
TEMPLATE_REL_PATH = "dj_design_system/components/elements/table/table.html"


def _render_template(source: str, context_data: dict[str, object] | None = None) -> str:
    """Render a Django template string with design_components loaded."""
    template = Template(template_string=f"{{% load design_components %}}{source}")
    return template.render(context=Context(dict_=context_data or {}))


def _make_table_registry() -> ComponentRegistry:
    """Create a ComponentRegistry populated with dj_design_system built-ins."""
    registry = ComponentRegistry()
    discover_app_into_registry(
        reg=registry,
        app_name=APP_LABEL,
        app_label=APP_LABEL,
    )
    return registry


def _read_table_css() -> str:
    """Read and return the co-located table.css stylesheet."""
    css_path = TABLE_DIR / "table.css"
    assert css_path.is_file()
    return css_path.read_text(encoding="utf-8")


class TestTableExportAndRegistration:
    """Verify package exports, metadata, and registry discovery for Table."""

    def test_exported_from_package_and_module(self) -> None:
        """Verify Table is exported in __init__.py and subclasses BlockComponent."""
        assert Table is DirectTable
        assert issubclass(Table, BlockComponent)

    def test_template_and_media_declarations(self) -> None:
        """Verify template_name and Media.css match the component contract."""
        assert Table.template_name == TEMPLATE_REL_PATH
        assert Table.Media.css == CSS_REL_PATH

    def test_registered_as_dds_table(self) -> None:
        """Verify autodiscovery registers Table under dds__table."""
        registry = _make_table_registry()
        info = registry.get_by_name(name="table", app_label=APP_LABEL)
        assert info.component_class is Table
        assert info.qualified_name == QUALIFIED_TAG
        assert info.template_name == TEMPLATE_REL_PATH
        assert CSS_REL_PATH in info.media.css

    def test_colocated_gallery_and_docs_exist(self) -> None:
        """Verify gallery.py and index.md exist and load cleanly."""
        registry = _make_table_registry()
        info = registry.get_by_name(name="table", app_label=APP_LABEL)
        gallery_cfg = info.gallery_config
        variant_names = [variant.name for variant in gallery_cfg.variants]
        assert "basic" in variant_names
        assert DENSITY_COMPACT in variant_names
        assert (TABLE_DIR / "index.md").is_file()


class TestTableParametersAndContext:
    """Verify parameter validation, slot validation, and get_context shaping."""

    def test_default_parameters_and_context(self) -> None:
        """Verify default caption and density values and context shaping."""
        instance = Table(slots={"body": mark_safe(s=BODY_HTML)})
        context = instance.get_context()
        assert instance.caption == ""
        assert instance.density == DENSITY_DEFAULT
        assert context["has_caption"] is False
        assert context["density"] == DENSITY_DEFAULT
        assert context["slots"]["head"] == ""
        assert context["slots"]["body"] == BODY_HTML

    def test_caption_and_compact_density_context(self) -> None:
        """Verify non-empty caption sets has_caption True and compact density is preserved."""
        instance = Table(
            caption=CAPTION_TEXT,
            density=DENSITY_COMPACT,
            slots={
                "head": mark_safe(s=HEAD_HTML),
                "body": mark_safe(s=BODY_HTML),
            },
        )
        context = instance.get_context()
        assert context["has_caption"] is True
        assert context["caption"] == CAPTION_TEXT
        assert context["density"] == DENSITY_COMPACT
        assert context["slots"]["head"] == HEAD_HTML
        assert context["slots"]["body"] == BODY_HTML

    def test_invalid_density_raises_value_error(self) -> None:
        """Verify an unsupported density choice raises ValueError."""
        with pytest.raises(expected_exception=ValueError, match="Expected one of"):
            Table(
                density="spacious",
                slots={"body": mark_safe(s=BODY_HTML)},
            )

    def test_missing_required_body_slot_raises_value_error(self) -> None:
        """Verify omitting the required body slot raises ValueError."""
        with pytest.raises(expected_exception=ValueError, match="requires slot 'body'"):
            Table(slots={"head": mark_safe(s=HEAD_HTML)})


class TestTableRendering:
    """Verify HTML output when rendering via Python and via template tags."""

    def test_renders_full_table_with_caption_head_and_body(self) -> None:
        """Verify caption, thead, and tbody render inside .dds-table."""
        html = _render_template(
            source=(
                f'{{% {QUALIFIED_TAG} caption="{CAPTION_TEXT}" density="{DENSITY_COMPACT}" %}}'
                f'{{% slot "head" %}}{HEAD_HTML}{{% endslot %}}'
                f'{{% slot "body" %}}{BODY_HTML}{{% endslot %}}'
                f"{{% end{QUALIFIED_TAG} %}}"
            )
        )
        assert f'<div class="dds-table" data-density="{DENSITY_COMPACT}">' in html
        assert f"<caption>{CAPTION_TEXT}</caption>" in html
        assert "<thead>" in html
        assert HEAD_HTML in html
        assert "<tbody>" in html
        assert BODY_HTML in html

    def test_omits_caption_and_thead_when_not_provided(self) -> None:
        """Verify caption and thead elements are omitted when not provided."""
        html = _render_template(
            source=(
                f"{{% {QUALIFIED_TAG} %}}"
                f'{{% slot "body" %}}{BODY_HTML}{{% endslot %}}'
                f"{{% end{QUALIFIED_TAG} %}}"
            )
        )
        assert f'<div class="dds-table" data-density="{DENSITY_DEFAULT}">' in html
        assert "<caption>" not in html
        assert "<thead>" not in html
        assert "<tbody>" in html
        assert BODY_HTML in html

    def test_template_tag_missing_body_slot_raises_syntax_error(self) -> None:
        """Verify template rendering without the body slot raises TemplateSyntaxError."""
        with pytest.raises(
            expected_exception=TemplateSyntaxError,
            match="requires slot 'body'",
        ):
            _render_template(
                source=(
                    f"{{% {QUALIFIED_TAG} %}}"
                    f'{{% slot "head" %}}{HEAD_HTML}{{% endslot %}}'
                    f"{{% end{QUALIFIED_TAG} %}}"
                )
            )

    def test_python_render_produces_expected_markup(self) -> None:
        """Verify calling .render() on a Table instance renders table.html."""
        instance = Table(
            caption=CAPTION_TEXT,
            density=DENSITY_COMPACT,
            slots={
                "head": mark_safe(s=HEAD_HTML),
                "body": mark_safe(s=BODY_HTML),
            },
        )
        html = instance.render()
        assert f'<div class="dds-table" data-density="{DENSITY_COMPACT}">' in html
        assert f"<caption>{CAPTION_TEXT}</caption>" in html
        assert HEAD_HTML in html
        assert BODY_HTML in html


class TestTableStylesheet:
    """Verify CUBE CSS layer, Tier 3 tokens, and styleguide rules in table.css."""

    def test_wrapped_in_layer_blocks_and_sets_root_layout(self) -> None:
        """Verify table.css wraps rules in @layer blocks and sets margin: 0 and overflow-x: auto."""
        css_text = _read_table_css()
        assert "@layer blocks {" in css_text
        assert "margin: 0;" in css_text
        assert "overflow-x: auto;" in css_text

    def test_tier_3_tokens_map_exclusively_to_tier_2_tokens(self) -> None:
        """Verify all --_table-* tokens map to Tier 2 --dds-* tokens and never Tier 1."""
        css_text = _read_table_css()
        assert "--_dds-" not in css_text
        token_defs = re.findall(
            pattern=r"(--_table-[a-z0-9-]+)\s*:\s*([^;]+);",
            string=css_text,
        )
        assert token_defs
        for _, value in token_defs:
            assert value.strip().startswith("var(--dds-")

        for required_domain in (
            "var(--dds-surface-",
            "var(--dds-control-",
            "var(--dds-text-",
            "var(--dds-space-",
        ):
            assert required_domain in css_text

    def test_compact_density_overrides_tier_3_tokens(self) -> None:
        """Verify [data-density='compact'] overrides --_table-* padding tokens."""
        css_text = _read_table_css()
        compact_match = re.search(
            pattern=r"\.dds-table\[data-density='compact'\]\s*\{([^}]+)\}",
            string=css_text,
        )
        assert compact_match is not None
        compact_block = compact_match.group(1)
        assert "--_table-cell-padding-block" in compact_block
        assert "--_table-cell-padding-inline" in compact_block

    def test_no_bem_and_alphabetized_declarations(self) -> None:
        """Verify zero BEM selectors and alphabetized declarations per html-css.md."""
        css_text = _read_table_css()
        bem_matches = re.findall(
            pattern=r"\.[a-z0-9-]+(?:__|--)[a-z0-9-]+",
            string=css_text,
        )
        assert not bem_matches
        assert "!important" not in css_text
        assert '"' not in css_text

        rule_blocks = re.findall(pattern=r"\{([^{}]+)\}", string=css_text)
        assert rule_blocks
        for block in rule_blocks:
            prop_names = re.findall(
                pattern=r"^\s*([a-z0-9_-]+)\s*:",
                string=block,
                flags=re.MULTILINE,
            )
            assert prop_names == sorted(prop_names)
