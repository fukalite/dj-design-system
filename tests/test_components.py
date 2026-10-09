import pytest
from django.test import override_settings

from dj_design_system.components import TagComponent
from dj_design_system.parameters.base import StrParam


# ---------------------------------------------------------------------------
# Helpers – minimal concrete component for constraint testing.
# ---------------------------------------------------------------------------


class TwoParamComponent(TagComponent):
    """Component with two optional params for constraint testing."""

    template_format_str = "<div>{foo}{bar}</div>"
    foo = StrParam("Foo param", required=False)
    bar = StrParam("Bar param", required=False)
    baz = StrParam("Baz param", required=False)


def test_tag_component_cannot_define_slots():
    with pytest.raises(
        ValueError, match="InvalidTag is a TagComponent and cannot define slots in Meta"
    ):

        class InvalidTag(TagComponent):
            class Meta:
                slots = {"content": None}

        _ = InvalidTag


# ---------------------------------------------------------------------------
# Meta.mutually_exclusive
# ---------------------------------------------------------------------------


class TestMutuallyExclusive:
    def test_raises_when_both_params_set(self):
        class ExclusiveComponent(TwoParamComponent):
            class Meta:
                mutually_exclusive = [("foo", "bar")]

        with pytest.raises(ValueError, match="'foo' and 'bar' cannot both be set"):
            ExclusiveComponent(foo="a", bar="b")

    def test_does_not_raise_when_only_first_set(self):
        class ExclusiveComponent(TwoParamComponent):
            class Meta:
                mutually_exclusive = [("foo", "bar")]

        ExclusiveComponent(foo="a")  # should not raise

    def test_does_not_raise_when_only_second_set(self):
        class ExclusiveComponent(TwoParamComponent):
            class Meta:
                mutually_exclusive = [("foo", "bar")]

        ExclusiveComponent(bar="b")  # should not raise

    def test_does_not_raise_when_neither_set(self):
        class ExclusiveComponent(TwoParamComponent):
            class Meta:
                mutually_exclusive = [("foo", "bar")]

        ExclusiveComponent()  # should not raise

    def test_multiple_pairs_all_checked(self):
        """All pairs in mutually_exclusive are enforced independently."""

        class ExclusiveComponent(TwoParamComponent):
            class Meta:
                mutually_exclusive = [("foo", "bar"), ("foo", "baz")]

        with pytest.raises(ValueError, match="'foo' and 'baz' cannot both be set"):
            ExclusiveComponent(foo="a", baz="c")

    def test_unknown_param_name_raises_at_class_definition(self):
        with pytest.raises(
            ValueError, match="mutually_exclusive references unknown param 'missing'"
        ):

            class BadComponent(TwoParamComponent):
                class Meta:
                    mutually_exclusive = [("foo", "missing")]


# ---------------------------------------------------------------------------
# Meta.requires
# ---------------------------------------------------------------------------


class TestRequires:
    def test_raises_when_dependent_set_without_dependency(self):
        class RequiresComponent(TwoParamComponent):
            class Meta:
                requires = [("bar", "foo")]

        with pytest.raises(ValueError, match="'bar' requires 'foo' to also be set"):
            RequiresComponent(bar="b")

    def test_does_not_raise_when_both_set(self):
        class RequiresComponent(TwoParamComponent):
            class Meta:
                requires = [("bar", "foo")]

        RequiresComponent(bar="b", foo="a")  # should not raise

    def test_does_not_raise_when_neither_set(self):
        class RequiresComponent(TwoParamComponent):
            class Meta:
                requires = [("bar", "foo")]

        RequiresComponent()  # should not raise

    def test_does_not_raise_when_only_dependency_set(self):
        """Setting the dependency alone (without the dependent) is always valid."""

        class RequiresComponent(TwoParamComponent):
            class Meta:
                requires = [("bar", "foo")]

        RequiresComponent(foo="a")  # should not raise

    def test_multiple_requires_all_checked(self):
        class RequiresComponent(TwoParamComponent):
            class Meta:
                requires = [("bar", "foo"), ("baz", "foo")]

        with pytest.raises(ValueError, match="'baz' requires 'foo' to also be set"):
            RequiresComponent(baz="c")

    def test_unknown_param_name_raises_at_class_definition(self):
        with pytest.raises(
            ValueError, match="requires references unknown param 'missing'"
        ):

            class BadComponent(TwoParamComponent):
                class Meta:
                    requires = [("foo", "missing")]


# ---------------------------------------------------------------------------
# Interaction with validate_params override hook
# ---------------------------------------------------------------------------


class TestConstraintsAndValidateParamsHook:
    def test_meta_constraints_checked_before_validate_params_hook(self):
        """Meta constraints fire before validate_params so the hook sees a valid state."""
        calls = []

        class OrderedComponent(TwoParamComponent):
            class Meta:
                mutually_exclusive = [("foo", "bar")]

            def validate_params(self):
                calls.append("validate_params")

        # Valid instantiation — validate_params should run.
        OrderedComponent(foo="a")
        assert calls == ["validate_params"]

        # Invalid instantiation — ValueError from Meta constraint fires first.
        calls.clear()
        with pytest.raises(ValueError):
            OrderedComponent(foo="a", bar="b")
        assert calls == []  # validate_params was never reached

    def test_validate_params_hook_still_runs_when_constraints_pass(self):
        class StrictComponent(TwoParamComponent):
            class Meta:
                mutually_exclusive = [("foo", "bar")]

            def validate_params(self):
                raise ValueError("hook fired")

        with pytest.raises(ValueError, match="hook fired"):
            StrictComponent(foo="a")


# ---------------------------------------------------------------------------
# description property and docstring() class method
# ---------------------------------------------------------------------------


class TestComponentIntrospection:
    def test_description_returns_docstring(self):
        class DocumentedComponent(TagComponent):
            """This is the component description."""

            template_format_str = "<div></div>"

        assert DocumentedComponent().description == "This is the component description."

    def test_description_none_when_no_docstring(self):
        class UndocumentedComponent(TagComponent):
            template_format_str = "<div></div>"

        assert UndocumentedComponent().description is None

    def test_class_docstring_contains_class_doc_and_params(self):
        from dj_design_system.parameters.base import StrParam

        class DocComponent(TagComponent):
            """My component."""

            label = StrParam("The label")
            template_format_str = "<div>{label}</div>"

        result = DocComponent.docstring()
        assert "My component." in result
        assert "label" in result


class TestComponentThemes:
    def test_available_themes_from_meta(self):
        class ThemeComponent(TwoParamComponent):
            class Meta:
                available_themes = ["dark"]

        assert ThemeComponent.get_available_themes() == ["dark"]

    @override_settings(
        DJ_DESIGN_SYSTEM={"APP_THEMES": {"tests": ["default", "custom"]}}
    )
    def test_available_themes_from_app_settings(self):
        class AppThemeComponent(TwoParamComponent):
            pass

        AppThemeComponent.get_app_label = classmethod(lambda cls: "tests")
        assert AppThemeComponent.get_available_themes() == ["default", "custom"]

    def test_available_themes_fallback_to_all(self):
        class FallbackComponent(TwoParamComponent):
            pass

        FallbackComponent.get_app_label = classmethod(lambda cls: "nonexistent")

        from dj_design_system.settings import get_themes

        all_themes = [t.value for t in get_themes()]
        assert FallbackComponent.get_available_themes() == all_themes


class TestComponentHtmlAttributes:
    def test_component_attrs(self):
        from dj_design_system.components import TagComponent
        from dj_design_system.parameters import BoolParam, StrParam

        class AttrComponent(TagComponent):
            variant = StrParam("Variant", attr="data-variant", required=False)
            expanded = BoolParam("Expanded", attr="aria-expanded", required=False)
            disabled = BoolParam(
                "Disabled", attr="disabled", attr_style="boolean", required=False
            )

            template_format_str = "<div {attrs}></div>"

        # Test string and boolean attrs
        comp = AttrComponent(variant="primary", expanded=False, disabled=True)
        ctx = comp.get_context()
        assert ctx["variant_attr"] == 'data-variant="primary"'
        assert ctx["expanded_attr"] == 'aria-expanded="false"'
        assert ctx["disabled_attr"] == "disabled"
        assert 'data-variant="primary"' in ctx["attrs"]
        assert 'aria-expanded="false"' in ctx["attrs"]
        assert "disabled" in ctx["attrs"]

        # Test defaults and not-set
        comp2 = AttrComponent()
        ctx2 = comp2.get_context()
        # Should not be in attrs because they are not set and have no default
        assert "variant_attr" not in ctx2
        assert "attrs" in ctx2 and ctx2["attrs"] == ""


class TestGetParamsCache:
    def test_caches_params_per_class_without_inheritance_leakage(self):
        from dj_design_system.components import TagComponent
        from dj_design_system.parameters import StrParam

        class ParentComp(TagComponent):
            parent_param = StrParam("Parent")
            template_format_str = "<div></div>"

        class ChildComp(ParentComp):
            child_param = StrParam("Child")

        assert set(ParentComp.get_params().keys()) == {"parent_param"}
        assert set(ChildComp.get_params().keys()) == {"parent_param", "child_param"}
        assert "_cached_params" in ParentComp.__dict__
        assert "_cached_params" in ChildComp.__dict__
        assert (
            ParentComp.__dict__["_cached_params"]
            is not ChildComp.__dict__["_cached_params"]
        )

    def test_mutating_returned_dict_does_not_corrupt_cache(self):
        params = TwoParamComponent.get_params()
        params["injected"] = None
        assert "injected" not in TwoParamComponent.get_params()


class TestBaseComponentKwargValidation:
    """Verify BaseComponent.__init__ rejects undeclared keyword arguments."""

    def test_unknown_kwarg_raises_type_error(self) -> None:
        with pytest.raises(
            TypeError,
            match="TwoParamComponent\\(\\) got an unexpected keyword argument 'unknown_param'",
        ):
            TwoParamComponent(foo="ok", unknown_param="bad")

    def test_declared_kwargs_accepted(self) -> None:
        comp = TwoParamComponent(foo="alpha", bar="beta")
        assert comp.foo == "alpha"
        assert comp.bar == "beta"


class TestBlockComponentSafeStringAndTemplateFallback:
    """Verify BlockComponent.__init__ normalises content/slots and render() falls back to template_name."""

    def test_block_component_normalizes_content_to_safestring(self) -> None:
        from django.utils.safestring import SafeString, mark_safe

        from dj_design_system.components import BlockComponent

        class SampleBlock(BlockComponent):
            template_format_str = "<div>{content}</div>"

        safe_comp = SampleBlock(content=mark_safe("<span>Hi</span>"))
        assert isinstance(safe_comp.content, SafeString)
        assert safe_comp.content == "<span>Hi</span>"

        plain_comp = SampleBlock(content="<script>evil()</script>")
        assert isinstance(plain_comp.content, SafeString)
        assert plain_comp.content == "&lt;script&gt;evil()&lt;/script&gt;"

        empty_comp = SampleBlock()
        assert isinstance(empty_comp.content, SafeString)
        assert empty_comp.content == ""

    def test_slotted_block_component_normalizes_slots_and_exposes_slots_dict(
        self,
    ) -> None:
        from django.utils.safestring import SafeString, mark_safe

        from dj_design_system.components import BlockComponent
        from dj_design_system.slots import Slot

        class SlottedSample(BlockComponent):
            template_format_str = "<div>{header}</div>"

            class Meta:
                slots = {"header": Slot(required=False)}

        comp = SlottedSample(
            content=mark_safe("<p>Body</p>"),
            slots={"header": mark_safe("<h1>Header</h1>")},
        )
        assert isinstance(comp.slots["header"], SafeString)
        assert isinstance(comp.content, SafeString)
        ctx = comp.get_context()
        assert ctx["slots"] == comp.slots
        assert ctx["header"] == "<h1>Header</h1>"
        assert ctx["content"] == "<p>Body</p>"

        unsafe_comp = SlottedSample(
            slots={"header": "<img src=x onerror=alert(1)>"},
        )
        assert isinstance(unsafe_comp.slots["header"], SafeString)
        assert unsafe_comp.slots["header"] == "&lt;img src=x onerror=alert(1)&gt;"

        falsy_comp = SlottedSample(
            slots={"header": 0},  # type: ignore[dict-item]
        )
        assert falsy_comp.slots["header"] == "0"

    def test_render_falls_back_to_explicit_template_name_without_private_attr(
        self,
    ) -> None:
        class UnboundTemplateComp(TagComponent):
            template_name = "dj_design_system/components/elements/badge/badge.html"
            label = StrParam("Label", default="Badge")

        comp = UnboundTemplateComp(label="Unbound")
        assert "_template_name" not in UnboundTemplateComp.__dict__
        rendered = comp.render()
        assert "Unbound" in rendered

    def test_resolve_colocated_template_derives_path_from_module(
        self,
    ) -> None:
        import inspect
        from pathlib import Path
        from unittest.mock import patch

        from dj_design_system.components.elements.badge import badge as badge_module
        from dj_design_system.services.component import resolve_colocated_template

        badge_py = Path(badge_module.__file__).resolve()

        class StandaloneBadge(TagComponent):
            __module__ = "dj_design_system.components.elements.badge.badge"
            label = StrParam("Label", default="Standalone")

            class Meta:
                name = "badge"

        with patch.object(inspect, "getfile", return_value=str(badge_py)):
            resolved = resolve_colocated_template(StandaloneBadge)

        assert resolved == "dj_design_system/components/elements/badge/badge.html"
