"""Tests for dds_navigation__pagination (contrib.navigation)."""

import pytest
from django.core.paginator import Paginator
from django.http import QueryDict
from django.template import Context, Template

from dj_design_system import component_registry
from dj_design_system.contrib.navigation.components.pagination.pagination import (
    PaginationComponent,
)


def page(count: int, number: int, per_page: int = 10):
    return Paginator(range(count), per_page).page(number)


def render(template: str, **context) -> str:
    return Template("{% load design_components %}" + template).render(Context(context))


class TestRegistration:
    def test_registered_under_the_contrib_prefix(self):
        info = component_registry.get_info(PaginationComponent)
        assert info.qualified_name == "dds_navigation__pagination"
        assert info.app_label == "dds_navigation"
        assert info.qualified_only

    def test_has_no_short_tag(self):
        with pytest.raises(Exception, match="Invalid block tag"):
            render("{% pagination p %}", p=page(50, 1))


class TestLinks:
    def test_numbered_links_and_current_page(self):
        html = PaginationComponent(page=page(50, 2)).render()
        for number in range(1, 6):
            assert f'href="?page={number}"' in html
        assert 'href="?page=2" aria-current="page"' in html

    def test_previous_and_next(self):
        html = PaginationComponent(page=page(50, 3)).render()
        assert '<a href="?page=2" rel="prev">Previous</a>' in html
        assert '<a href="?page=4" rel="next">Next</a>' in html

    def test_first_page_disables_previous(self):
        html = PaginationComponent(page=page(50, 1)).render()
        assert '<span aria-disabled="true">Previous</span>' in html
        assert 'rel="next"' in html

    def test_last_page_disables_next(self):
        html = PaginationComponent(page=page(50, 5)).render()
        assert '<span aria-disabled="true">Next</span>' in html

    def test_long_range_is_elided(self):
        html = PaginationComponent(page=page(500, 25), on_each_side=1).render()
        assert html.count("<span>…</span>") == 2
        assert 'href="?page=24"' in html and 'href="?page=26"' in html
        assert 'href="?page=10"' not in html
        assert 'href="?page=1"' in html and 'href="?page=50"' in html

    def test_on_ends_controls_the_edges(self):
        html = PaginationComponent(page=page(500, 25), on_ends=2).render()
        assert 'href="?page=2"' in html and 'href="?page=49"' in html


class TestQueryString:
    def test_keeps_querydict_params_and_replaces_page(self):
        query = QueryDict("q=report&tag=a&tag=b&page=9")
        html = PaginationComponent(page=page(50, 2), query=query).render()
        assert 'href="?q=report&amp;tag=a&amp;tag=b&amp;page=3"' in html
        assert "page=9" not in html

    def test_does_not_mutate_the_querydict(self):
        query = QueryDict("page=9")
        PaginationComponent(page=page(50, 2), query=query).render()
        assert query["page"] == "9"

    def test_accepts_a_plain_dict(self):
        html = PaginationComponent(
            page=page(50, 2), query={"q": "x", "tag": ["a", "b"]}
        ).render()
        assert 'href="?q=x&amp;tag=a&amp;tag=b&amp;page=3"' in html

    def test_custom_page_param(self):
        html = PaginationComponent(page=page(50, 2), page_param="p").render()
        assert 'href="?p=3"' in html


class TestSinglePage:
    def test_hidden_by_default(self):
        assert PaginationComponent(page=page(5, 1)).render().strip() == ""

    def test_can_be_shown(self):
        html = PaginationComponent(page=page(5, 1), hide_single_page=False).render()
        assert 'aria-current="page"' in html


class TestMarkup:
    def test_nav_landmark_with_label(self):
        html = PaginationComponent(page=page(50, 1), label="Results pages").render()
        assert '<nav aria-label="Results pages">' in html

    def test_unstyled(self):
        html = PaginationComponent(page=page(50, 1)).render()
        assert "class=" not in html
        assert "<style" not in html

    def test_rejects_a_non_page(self):
        with pytest.raises(TypeError, match="Expected Page"):
            PaginationComponent(page=[1, 2, 3])


class TestTemplateTag:
    def test_positional_page_and_request_get(self):
        html = render(
            "{% dds_navigation__pagination p query=q %}",
            p=page(50, 2),
            q=QueryDict("q=a"),
        )
        assert 'href="?q=a&amp;page=3" rel="next"' in html


@pytest.mark.django_db
class TestGallery:
    def test_component_page_renders(self, client):
        response = client.get("/dds/dds_navigation/pagination/")
        assert response.status_code == 200
        html = response.content.decode()
        assert "dds_navigation__pagination" in html
        assert "page_obj" in html  # GalleryParameter code, not the object

    @pytest.mark.parametrize("variant", ["basic", "maximal", "first_page"])
    def test_variant_canvases_render_the_sample_page(self, client, variant):
        response = client.get(
            "/dds/_canvas/?component=dds_navigation__pagination"
            f"&_dds_variant={variant}&_dds_mode=basic"
        )
        assert response.status_code == 200
        assert 'aria-current="page"' in response.content.decode()

    def test_maximal_canvas_keeps_the_sample_query(self, client):
        response = client.get(
            "/dds/_canvas/?component=dds_navigation__pagination"
            "&_dds_variant=maximal&_dds_mode=basic"
        )
        assert "q=report&amp;sort=-date&amp;page=24" in response.content.decode()
