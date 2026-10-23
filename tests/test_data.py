import dataclasses
from types import SimpleNamespace

import pytest

from dj_design_system.data import (
    ComponentMedia,
    FormFieldRowData,
    NavItemInputData,
    ParamRowData,
    ParamSpecData,
    ParamTableRowData,
    SandboxControlOptionData,
    SlotTableRowData,
)
from dj_design_system.parameters.base import JSONParam, StrParam
from example_project.demo_components.components.button.button import ButtonComponent
from example_project.demo_components.components.card.info_card import InfoCardComponent
from example_project.demo_components.components.rich_button import RichButtonComponent


# ---------------------------------------------------------------------------
# ComponentMedia unit tests
# ---------------------------------------------------------------------------


class TestComponentMedia:
    def test_default_is_empty(self):
        m = ComponentMedia()
        assert m.css == []
        assert m.js == []

    def test_bool_false_when_empty(self):
        assert not ComponentMedia()

    def test_bool_true_with_css(self):
        assert ComponentMedia(css=["a.css"])

    def test_bool_true_with_js(self):
        assert ComponentMedia(js=["a.js"])

    def test_merge_combines_lists(self):
        a = ComponentMedia(css=["a.css"], js=["a.js"])
        b = ComponentMedia(css=["b.css"], js=["b.js"])
        merged = a.merge(b)
        assert merged.css == ["a.css", "b.css"]
        assert merged.js == ["a.js", "b.js"]

    def test_merge_deduplicates(self):
        a = ComponentMedia(css=["shared.css", "a.css"])
        b = ComponentMedia(css=["shared.css", "b.css"])
        merged = a.merge(b)
        assert merged.css == ["shared.css", "a.css", "b.css"]

    def test_merge_self_first(self):
        a = ComponentMedia(css=["parent.css"])
        b = ComponentMedia(css=["child.css"])
        merged = a.merge(b)
        assert merged.css == ["parent.css", "child.css"]

    def test_merge_returns_new_instance(self):
        a = ComponentMedia(css=["a.css"])
        b = ComponentMedia(css=["b.css"])
        merged = a.merge(b)
        assert merged is not a
        assert merged is not b


# ---------------------------------------------------------------------------
# ComponentInfo.media — auto-discovery
# ---------------------------------------------------------------------------


class TestAutoDiscovery:
    def test_finds_colocated_css_and_js(self, registry_with_demo_components):
        """ButtonComponent has button.css and button.js next to it."""
        reg = registry_with_demo_components
        info = reg.get_info(ButtonComponent)
        media = info.media
        assert media.css == ["demo_components/components/button/button.css"]
        assert media.js == ["demo_components/components/button/button.js"]

    def test_no_files_returns_empty_media(self, registry_with_demo_components):
        """InfoCardComponent has no co-located CSS or JS."""
        reg = registry_with_demo_components
        info = reg.get_info(InfoCardComponent)
        media = info.media
        assert media.css == []
        assert media.js == []

    def test_media_is_falsy_when_empty(self, registry_with_demo_components):
        reg = registry_with_demo_components
        info = reg.get_info(InfoCardComponent)
        assert not info.media

    def test_media_is_truthy_when_files_exist(self, registry_with_demo_components):
        reg = registry_with_demo_components
        info = reg.get_info(ButtonComponent)
        assert info.media


# ---------------------------------------------------------------------------
# ComponentInfo.media — explicit Media class + auto-discovery
# ---------------------------------------------------------------------------


class TestMediaClassOverride:
    def _make_info(
        self,
        component_class,
        name="test_component",
        app_label="testapp",
        relative_path="",
    ):
        from dj_design_system.data import ComponentInfo

        return ComponentInfo(
            component_class=component_class,
            name=name,
            app_label=app_label,
            relative_path=relative_path,
        )

    def test_media_class_list_stored_verbatim(self):
        from dj_design_system.components import TagComponent

        class MyComponent(TagComponent):
            class Media:
                css = ["testapp/components/my.css"]
                js = ["testapp/components/my.js"]

        info = self._make_info(MyComponent)
        assert info.media.css == ["testapp/components/my.css"]
        assert info.media.js == ["testapp/components/my.js"]

    def test_media_class_single_string_normalised(self):
        from dj_design_system.components import TagComponent

        class MyComponent(TagComponent):
            class Media:
                css = "testapp/components/my.css"

        info = self._make_info(MyComponent)
        assert info.media.css == ["testapp/components/my.css"]

    def test_media_class_no_colocated_files(self):
        """A component with a Media class but no co-located files returns only
        the explicit Media entries."""
        from dj_design_system.components import TagComponent

        class ExplicitMediaComponent(TagComponent):
            class Media:
                css = ["explicit/path.css"]

        info = self._make_info(ExplicitMediaComponent)
        media = info.media
        assert media.css == ["explicit/path.css"]

    def test_media_class_merges_with_autodiscovery(self, registry_with_demo_components):
        """A component with both an explicit Media class and co-located files
        should include entries from both sources.

        RichButtonComponent declares ``Media.css = ["demo_components/components/rich_button_extras.css"]``
        and also has a co-located ``rich_button.css`` file. Both should appear
        in the merged result, with explicit entries first.
        """
        reg = registry_with_demo_components
        info = reg.get_info(RichButtonComponent)
        media = info.media
        assert any(p.endswith("rich_button_extras.css") for p in media.css)
        assert any(p.endswith("rich_button.css") for p in media.css)
        # Explicit entry appears before auto-discovered entry.
        extras_idx = next(
            i for i, p in enumerate(media.css) if p.endswith("rich_button_extras.css")
        )
        auto_idx = next(
            i
            for i, p in enumerate(media.css)
            if p.endswith("rich_button.css")
            and not p.endswith("rich_button_extras.css")
        )
        assert extras_idx < auto_idx

    def test_mro_merge_parent_first(self):
        from dj_design_system.components import TagComponent

        class ParentComponent(TagComponent):
            class Media:
                css = ["testapp/components/parent.css"]

        class ChildComponent(ParentComponent):
            class Media:
                css = ["testapp/components/child.css"]

        info = self._make_info(ChildComponent)
        assert info.media.css == [
            "testapp/components/parent.css",
            "testapp/components/child.css",
        ]

    def test_mro_merge_deduplicates(self):
        from dj_design_system.components import TagComponent

        class ParentComponent(TagComponent):
            class Media:
                css = ["testapp/components/shared.css", "testapp/components/parent.css"]

        class ChildComponent(ParentComponent):
            class Media:
                css = ["testapp/components/shared.css", "testapp/components/child.css"]

        info = self._make_info(ChildComponent)
        assert info.media.css == [
            "testapp/components/shared.css",
            "testapp/components/parent.css",
            "testapp/components/child.css",
        ]

    def test_parent_only_media_inherited_by_child(self):
        """Child without its own Media still inherits via the MRO merge."""
        from dj_design_system.components import TagComponent

        class ParentComponent(TagComponent):
            class Media:
                css = ["testapp/components/parent.css"]

        class ChildComponent(ParentComponent):
            pass

        info = self._make_info(ChildComponent)
        assert info.media.css == ["testapp/components/parent.css"]


# ---------------------------------------------------------------------------
# ComponentInfo.template_name
# ---------------------------------------------------------------------------


class TestTemplateName:
    def test_returns_none_when_not_set(self, registry_with_demo_components):
        """A component without an HTML template has template_name of None."""
        reg = registry_with_demo_components
        from example_project.demo_components.components.alert import AlertComponent

        info = reg.get_info(AlertComponent)
        assert info.template_name is None

    def test_returns_template_name_for_html_component(
        self, registry_with_demo_components
    ):
        """ButtonComponent has a co-located button.html — template_name should be set."""
        reg = registry_with_demo_components
        info = reg.get_info(ButtonComponent)
        assert info.template_name == "demo_components/components/button/button.html"

    def test_template_name_matches_class_attribute(self, registry_with_demo_components):
        """ComponentInfo.template_name reads from the class's _template_name attribute."""
        reg = registry_with_demo_components
        info = reg.get_info(ButtonComponent)
        assert info.template_name == ButtonComponent._template_name


# ---------------------------------------------------------------------------


class TestGetMedia:
    def test_get_media_delegates_to_registry(self, registry_with_demo_components):
        from dj_design_system import component_registry

        reg = registry_with_demo_components

        # Temporarily swap the global registry so get_media() can resolve.
        original = component_registry._components[:]
        component_registry._components = reg._components

        try:
            media = ButtonComponent.get_media()
            assert media.css == ["demo_components/components/button/button.css"]
            assert media.js == ["demo_components/components/button/button.js"]
        finally:
            component_registry._components = original


# ---------------------------------------------------------------------------
# ComponentInfo.gallery_basic_kwargs
# ---------------------------------------------------------------------------


class TestGalleryKwargs:
    def test_gallery_kwargs_lazy_loading(self, registry_with_demo_components):
        """Test that gallery_basic_kwargs are lazily loaded."""
        from example_project.demo_components.components.button.button import (
            ButtonComponent,
        )

        reg = registry_with_demo_components
        info = reg.get_info(ButtonComponent)

        # Accessing the property should compute it
        assert isinstance(info.gallery_basic_kwargs, dict)
        assert isinstance(info.gallery_maximal_kwargs, dict)

        # It should cache the result on the instance, not the class
        assert not hasattr(ButtonComponent, "_gallery_kwargs")
        assert "_gallery_kwargs" in info.__dict__


class TestParamRowData:
    def test_param_spec_and_row_are_frozen_and_do_not_mutate_base_param(self):
        str_param = StrParam("Label text", default="Click", required=True)
        json_param = JSONParam("Payload")

        spec_str = ParamSpecData.from_param(str_param)
        spec_json = ParamSpecData.from_param(json_param)

        assert "type_name" not in str_param.__dict__
        assert "type_name" not in json_param.__dict__
        assert spec_str.type_name == "str"
        assert spec_str.description == "Label text"
        assert spec_str.default == "Click"
        assert spec_str.required is True
        assert (
            "dict | list | str | int | float | bool | NoneType" in spec_json.type_name
        )

        row = ParamRowData(name="label", spec=spec_str, field="<input>")
        assert row.name == "label"
        assert row["name"] == "label"
        assert "name" in row
        assert "spec" in row
        assert "field" in row
        assert row.get("name") == "label"
        assert row.get("missing", "fallback") == "fallback"

        with pytest.raises(dataclasses.FrozenInstanceError):
            row.name = "mutated"  # type: ignore[misc]
        with pytest.raises(dataclasses.FrozenInstanceError):
            spec_str.type_name = "int"  # type: ignore[misc]


class TestDomainDataNormalisers:
    def test_sandbox_control_option_data_normalises_strings_tuples_dicts_and_objects(
        self,
    ):
        from_str = SandboxControlOptionData.from_raw("dark")
        assert from_str.value == "dark"
        assert from_str.label == "Dark"

        from_tuple = SandboxControlOptionData.from_raw(("768", "Tablet — 768px"))
        assert from_tuple.value == "768"
        assert from_tuple.label == "Tablet — 768px"

        from_dict = SandboxControlOptionData.from_raw(
            {"name": "primary", "label": "Primary"},
            base_url="/dds/button/",
            is_variant=True,
        )
        assert from_dict.name == "primary"
        assert from_dict.label == "Primary"
        assert from_dict.href == "/dds/button/?variant=primary"

        from_obj = SandboxControlOptionData.from_raw(
            SimpleNamespace(value="125%", label="125%"),
            is_zoom=True,
        )
        assert from_obj.value == "125"
        assert from_obj.label == "125%"

    def test_form_field_row_data_normalises_dicts_and_param_row_data(self):
        spec = ParamSpecData(description="Button label", required=True, type_name="str")
        row = ParamRowData(name="label", spec=spec, field="<input id='id_label'>")
        normalised = FormFieldRowData.from_raw(row)
        assert normalised.name == "label"
        assert normalised.description == "Button label"
        assert normalised.required is True
        assert normalised.has_field_html is True
        assert normalised["name"] == "label"

    def test_param_and_slot_table_row_data_normalise_tuples_and_dicts(self):
        param_row = ParamTableRowData.from_raw(
            (
                "variant",
                StrParam(
                    "Visual style",
                    default="primary",
                    choices=["primary", "secondary"],
                ),
            )
        )
        assert param_row.name == "variant"
        assert param_row.type_name == "str"
        assert param_row.default_display == "primary"
        assert param_row.choices == ["primary", "secondary"]
        assert param_row["name"] == "variant"

        slot_row = SlotTableRowData.from_raw(
            {"name": "header", "required": True, "description": "Card header"}
        )
        assert slot_row.name == "header"
        assert slot_row.required is True
        assert slot_row.required_label == "Required"
        assert slot_row["description"] == "Card header"

    def test_nav_item_input_data_normalises_nav_nodes_and_dicts(self):
        item = NavItemInputData.from_raw(
            {
                "name": "Buttons",
                "href": "/dds/buttons/",
                "type": "folder",
                "children": [{"label": "Button"}],
            },
            default_label_from_name=True,
        )
        assert item.label == "Buttons"
        assert item.url == "/dds/buttons/"
        assert item.node_type == "folder"
        assert len(item.children) == 1
