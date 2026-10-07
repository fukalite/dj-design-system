"""Tests for the media service."""

import pytest
from django.templatetags.static import static

from dj_design_system.services import media as media_service


class TestResolveAssetUrl:
    """External URLs pass through unchanged; local paths go through ``static()`` (#166)."""

    @pytest.mark.parametrize(
        "url",
        [
            "http://cdn.example.com/app.css",
            "https://cdn.example.com/app.css",
            "//cdn.example.com/app.css",
            "HTTPS://cdn.example.com/app.css",
            "Http://cdn.example.com/app.css",
            "https://fonts.googleapis.com/css2?family=Inter&display=swap",
        ],
    )
    def test_external_url_unchanged(self, url):
        assert media_service.resolve_asset_url(path=url) == url

    @pytest.mark.parametrize(
        "path",
        [
            "myapp/app.css",
            "myapp/http/app.css",
            "https-assets/app.css",
        ],
    )
    def test_local_path_resolved_via_static(self, path):
        assert media_service.resolve_asset_url(path=path) == static(path)
