"""Tests for navigation and search index caching, and HTMX execution skipping."""

from unittest.mock import patch

from django.test import RequestFactory

from dj_design_system.services.navigation import (
    _build_navigation,
    _collect_search_entries,
    build_navigation,
    build_search_index,
    clear_navigation_cache,
)
from dj_design_system.views import get_base_context


class TestNavigationCaching:
    """Test caching behavior of build_navigation and build_search_index."""

    def test_build_navigation_is_cached(self):
        """Calling build_navigation multiple times caches and only builds once."""
        clear_navigation_cache()
        with patch(
            "dj_design_system.services.navigation._build_navigation",
            wraps=_build_navigation,
        ) as mock_builder:
            tree1 = build_navigation()
            tree2 = build_navigation()

            assert tree1 is tree2
            assert mock_builder.call_count == 1

    def test_clear_navigation_cache_resets(self):
        """clear_navigation_cache resets the cached navigation tree."""
        clear_navigation_cache()
        with patch(
            "dj_design_system.services.navigation._build_navigation",
            wraps=_build_navigation,
        ) as mock_builder:
            build_navigation()
            assert mock_builder.call_count == 1

            clear_navigation_cache()
            build_navigation()
            assert mock_builder.call_count == 2

    def test_build_search_index_is_cached(self):
        """build_search_index caches results for the same navigation tree."""
        clear_navigation_cache()
        tree = build_navigation()
        with patch(
            "dj_design_system.services.navigation._collect_search_entries",
            wraps=_collect_search_entries,
        ) as mock_collector:
            index1 = build_search_index(tree)
            first_count = mock_collector.call_count
            assert first_count > 0

            index2 = build_search_index(tree)
            assert index1 is index2
            assert mock_collector.call_count == first_count

    def test_get_base_context_skips_search_index_on_htmx(self):
        """get_base_context skips building search index when request is an HTMX request."""
        rf = RequestFactory()
        request = rf.get("/gallery/", HTTP_HX_REQUEST="true")

        with patch(
            "dj_design_system.views.build_search_index",
        ) as mock_search_index:
            context = get_base_context(request)
            assert mock_search_index.call_count == 0
            assert context["search_index"] == []

    def test_get_base_context_builds_search_index_on_standard_request(self):
        """get_base_context includes search index on standard non-HTMX request."""
        rf = RequestFactory()
        request = rf.get("/gallery/")

        context = get_base_context(request)
        assert isinstance(context["search_index"], list)
        assert len(context["search_index"]) > 0
