"""Tests for dj_design_system.contrib.django_admin."""

import re
from types import SimpleNamespace
from unittest import mock

import pytest
from django.apps import apps
from django.contrib.admin import AdminSite
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator

from dj_design_system import component_registry
from dj_design_system.contrib.checks import check_contrib_requirements
from dj_design_system.contrib.django_admin.checks import check_installed_before_admin
from dj_design_system.contrib.django_admin.components.pagination.pagination import (
    AdminPaginationComponent,
)
from dj_design_system.contrib.django_admin.sites import (
    DesignSystemAdminSite,
    uses_design_system,
)
from dj_design_system.contrib.navigation.components.pagination.pagination import (
    PaginationComponent,
)


User = get_user_model()


class TestApp:
    def test_label_and_prefix(self):
        config = apps.get_app_config("dds_django_admin")
        assert config.dds_component_prefix == "dds_admin"

    def test_requires_navigation_and_admin(self):
        requires = apps.get_app_config("dds_django_admin").requires
        assert "dj_design_system.contrib.navigation" in requires
        assert "django.contrib.admin" in requires

    def test_checks_pass_with_test_settings(self):
        assert check_installed_before_admin() == []
        assert check_contrib_requirements() == []

    def test_e008_when_installed_after_the_admin(self):
        configs = [
            SimpleNamespace(name="django.contrib.admin"),
            SimpleNamespace(name="dj_design_system.contrib.django_admin"),
        ]
        with mock.patch(
            "dj_design_system.contrib.django_admin.checks.apps.get_app_configs",
            return_value=configs,
        ):
            messages = check_installed_before_admin()
        assert [m.id for m in messages] == ["dj_design_system.E008"]


class TestSites:
    def test_design_system_site_opts_in(self):
        assert uses_design_system(DesignSystemAdminSite())

    def test_stock_sites_do_not(self):
        assert not uses_design_system(AdminSite())
        assert not uses_design_system(None)


class TestAdminPaginationComponent:
    def page(self, count=500, number=3):
        return Paginator(range(count), 100).page(number)

    def test_registered_as_dds_admin_pagination(self):
        info = component_registry.get_info(AdminPaginationComponent)
        assert info.qualified_name == "dds_admin__pagination"

    def test_subclasses_the_generic_component(self):
        assert issubclass(AdminPaginationComponent, PaginationComponent)

    def test_uses_admin_markup_with_previous_and_next(self):
        html = AdminPaginationComponent(page=self.page(), summary="500 books").render()
        assert '<nav class="paginator" aria-label="Pagination">' in html
        assert '<a role="button" href="" aria-current="page">3</a>' in html
        assert 'href="?page=2" rel="prev"' in html
        assert 'href="?page=4" rel="next"' in html
        assert "500 books" in html

    def test_single_page_shows_only_the_summary(self):
        html = AdminPaginationComponent(
            page=self.page(count=5, number=1), summary="5 books"
        ).render()
        assert "<ul>" not in html
        assert "5 books" in html

    def test_show_all_link(self):
        html = AdminPaginationComponent(page=self.page(), show_all_url="?all=").render()
        assert '<a href="?all=" class="showall">Show all</a>' in html


def links(html: str) -> list[str]:
    # Django 5.2 wraps the stock paginator in <p>, 6.0+ in <nav>.
    nav = re.search(r'<(nav|p) class="paginator".*?</\1>', html, re.S)
    assert nav, "no paginator in page"
    return re.findall(r'href="([^"]*)"', nav.group(0))


@pytest.mark.django_db
class TestPerSiteToggle:
    @pytest.fixture()
    def admin_client(self, client, settings):
        settings.ROOT_URLCONF = "tests.admin_urls"
        for i in range(5):
            User.objects.create_user(username=f"user{i}")
        admin = User.objects.create_superuser("root", "root@example.com", "pw")
        client.force_login(admin)
        return client

    def get(self, client, site, query=""):
        response = client.get(f"/{site}/auth/user/{query}")
        assert response.status_code == 200
        return response.content.decode()

    def test_stock_site_renders_django_pagination(self, admin_client):
        html = self.get(admin_client, "stock-admin")
        assert 'class="paginator"' in html  # Django's own template
        assert 'aria-label="Pagination users"' not in html
        assert 'rel="next"' not in html

    def test_design_system_site_renders_the_component(self, admin_client):
        html = self.get(admin_client, "dds-admin", "?p=2")
        assert '<nav class="paginator" aria-label="Pagination users">' in html
        assert 'rel="prev"' in html and 'rel="next"' in html
        assert "6 users" in html

    def test_links_keep_filters_search_and_ordering(self, admin_client):
        html = self.get(admin_client, "dds-admin", "?is_staff__exact=0&o=1&p=2")
        hrefs = [h for h in links(html) if h]
        assert hrefs
        for href in hrefs:
            if "all=" in href:
                continue
            assert "is_staff__exact=0" in href and "o=1" in href

    @pytest.mark.parametrize("number", [1, 2, 3])
    def test_page_numbers_match_the_stock_site(self, admin_client, number):
        for i in range(5, 30):
            User.objects.create_user(username=f"user{i}")
        stock = self.get(admin_client, "stock-admin", f"?p={number}")
        dds = self.get(admin_client, "dds-admin", f"?p={number}")
        stock_pages = [h for h in links(stock) if h and "all=" not in h]
        dds_pages = [h for h in links(dds) if h and "all=" not in h]
        # Same numbered links; ours adds Previous/Next, which repeat a number.
        assert set(dds_pages) == set(stock_pages)

    def test_show_all_hides_the_links(self, admin_client):
        html = self.get(admin_client, "dds-admin", "?all=")
        assert "<ul>" not in re.search(
            r'<nav class="paginator".*?</nav>', html, re.S
        ).group(0)
        assert "6 users" in html
