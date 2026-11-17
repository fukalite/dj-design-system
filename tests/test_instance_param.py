from decimal import Decimal

import pytest
from django.core.paginator import Page, Paginator

from dj_design_system.components import TagComponent
from dj_design_system.parameters import InstanceParam


def make_page(number: int = 1) -> Page:
    return Paginator(list(range(50)), 10).page(number)


class TestInstanceParamConstruction:
    def test_accepts_a_class(self):
        param = InstanceParam(Page)
        assert param.type is Page

    def test_resolves_a_dotted_path_lazily(self):
        param = InstanceParam("django.core.paginator.Page")
        assert param.type is Page

    def test_accepts_a_tuple_of_classes_and_paths(self):
        param = InstanceParam((int, "decimal.Decimal"))
        assert param.type == (int, Decimal)

    @pytest.mark.parametrize("bad", [1, None, ()])
    def test_rejects_anything_else(self, bad):
        with pytest.raises(TypeError, match="InstanceParam expects"):
            InstanceParam(bad)

    def test_tuple_item_that_is_not_a_class_or_path_raises(self):
        param = InstanceParam((int, 3))
        with pytest.raises(TypeError, match="got 3"):
            param.type

    def test_path_to_a_non_class_raises(self):
        param = InstanceParam("django.core.paginator.Paginator.page")
        with pytest.raises((TypeError, ImportError)):
            param.type

    def test_default_is_validated(self):
        with pytest.raises(TypeError, match="Expected Page but got str"):
            InstanceParam(Page, required=False, default="nope")


class TestInstanceParamValidation:
    def test_accepts_an_instance(self):
        InstanceParam(Page).validate(make_page())

    def test_accepts_a_subclass_instance(self):
        class MyPage(Page):
            pass

        InstanceParam(Page).validate(MyPage([], 1, Paginator([], 10)))

    def test_wrong_type_names_expected_and_actual(self):
        with pytest.raises(TypeError, match="Expected Page but got list"):
            InstanceParam(Page).validate([1, 2])

    def test_tuple_error_lists_every_type(self):
        with pytest.raises(TypeError, match=r"Expected int \| Decimal but got str"):
            InstanceParam((int, Decimal)).validate("1")

    def test_none_allowed_when_optional(self):
        InstanceParam(Page, required=False).validate(None)

    def test_none_rejected_when_required(self):
        with pytest.raises(TypeError, match="Expected Page but got NoneType"):
            InstanceParam(Page).validate(None)


class TestInstanceParamDocs:
    def test_docstring_names_the_class(self):
        class Comp(TagComponent):
            page = InstanceParam(Page, "The page.")

        param = Comp.get_params()["page"]
        assert param.docstring() == "page: Page - The page."

    def test_str_names_the_class(self):
        class Comp(TagComponent):
            page = InstanceParam("django.core.paginator.Page")

        assert str(Comp.get_params()["page"]) == "<InstanceParam page of type Page>"


class TestInstanceParamInComponent:
    def test_component_receives_the_object(self):
        class PageInfo(TagComponent):
            template_format_str = "<p>{page_label}</p>"
            page = InstanceParam(Page)

            def get_context(self):
                context = super().get_context()
                context["page_label"] = (
                    f"{self.page.number} of {self.page.paginator.num_pages}"
                )
                return context

        assert PageInfo(page=make_page(2)).render() == "<p>2 of 5</p>"

    def test_component_rejects_wrong_type(self):
        class PageInfo(TagComponent):
            template_format_str = "<p></p>"
            page = InstanceParam(Page)

        with pytest.raises(TypeError, match="Expected Page"):
            PageInfo(page="2")
