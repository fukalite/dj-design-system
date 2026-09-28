"""Tests for the migrate_gallery_configs management command and AST transformer."""

from io import StringIO
from pathlib import Path

import pytest
from django.core.management import CommandError, call_command

from dj_design_system.management.commands.migrate_gallery_configs import (
    migrate_source,
)


class TestMigrateSourceAST:
    """Unit tests for AST-based source code migration."""

    def test_migrate_source_basic_and_maximal(self):
        source = """
basic_kwargs = {
    "label": "Click me",
}

maximal_kwargs = {
    "label": "Save Changes",
    "theme": "primary",
}
"""
        new_source, modified = migrate_source(source)
        assert modified is True
        assert (
            "from dj_design_system.gallery import GalleryConfig, Variant" in new_source
        )
        assert "config = GalleryConfig(" in new_source
        assert "name='basic'" in new_source or 'name="basic"' in new_source
        assert "name='maximal'" in new_source or 'name="maximal"' in new_source
        # Legacy variables removed by default
        assert "basic_kwargs =" not in new_source
        assert "maximal_kwargs =" not in new_source

    def test_migrate_source_preserves_imports_and_gallery_parameter(self):
        source = """
from dj_design_system.data import GalleryParameter

basic_kwargs = {"title": "Hello"}
maximal_kwargs = {
    "title": "World",
    "param": GalleryParameter(value=123, code="special"),
}
"""
        new_source, modified = migrate_source(source)
        assert modified is True
        assert "from dj_design_system.data import GalleryParameter" in new_source
        assert (
            "from dj_design_system.gallery import GalleryConfig, Variant" in new_source
        )
        assert (
            "GalleryParameter(value=123, code='special')" in new_source
            or 'GalleryParameter(value=123, code="special")' in new_source
        )

    def test_migrate_source_already_has_config_returns_false(self):
        source = """
from dj_design_system.gallery import GalleryConfig, Variant

config = GalleryConfig(variants=[Variant(name="default")])
"""
        new_source, modified = migrate_source(source)
        assert modified is False
        assert new_source == source

    def test_migrate_source_no_kwargs_returns_false(self):
        source = """
def helper():
    return 42
"""
        new_source, modified = migrate_source(source)
        assert modified is False

    def test_migrate_source_keep_legacy(self):
        source = """
basic_kwargs = {"a": 1}
maximal_kwargs = {"b": 2}
"""
        new_source, modified = migrate_source(source, keep_legacy=True)
        assert modified is True
        assert (
            "basic_kwargs = {'a': 1}" in new_source
            or 'basic_kwargs = {"a": 1}' in new_source
        )
        assert "config = GalleryConfig(" in new_source


class TestMigrateGalleryConfigsCommand:
    """Integration tests for the migrate_gallery_configs management command."""

    def test_command_dry_run_does_not_modify_file(self, tmp_path: Path):
        test_file = tmp_path / "button_gallery.py"
        test_file.write_text('basic_kwargs = {"text": "Click"}', encoding="utf-8")

        out = StringIO()
        call_command("migrate_gallery_configs", str(tmp_path), dry_run=True, stdout=out)

        output = out.getvalue()
        assert "Would migrate" in output
        assert 'basic_kwargs = {"text": "Click"}' in test_file.read_text(
            encoding="utf-8"
        )

    def test_command_modifies_file(self, tmp_path: Path):
        test_file = tmp_path / "badge_gallery.py"
        test_file.write_text(
            'basic_kwargs = {"text": "New"}\nmaximal_kwargs = {"text": "Unread", "theme": "danger"}',
            encoding="utf-8",
        )

        out = StringIO()
        call_command("migrate_gallery_configs", str(tmp_path), stdout=out)

        output = out.getvalue()
        assert "Migrated" in output
        content = test_file.read_text(encoding="utf-8")
        assert "config = GalleryConfig(" in content
        assert "basic_kwargs =" not in content

    def test_command_check_fails_on_unmigrated(self, tmp_path: Path):
        test_file = tmp_path / "alert_gallery.py"
        test_file.write_text('basic_kwargs = {"msg": "Warning"}', encoding="utf-8")

        err = StringIO()
        with pytest.raises(CommandError, match="Found 1 unmigrated gallery file"):
            call_command(
                "migrate_gallery_configs", str(tmp_path), check=True, stderr=err
            )
        assert "Found 1 unmigrated gallery file" in err.getvalue()

    def test_command_check_succeeds_when_clean(self, tmp_path: Path):
        test_file = tmp_path / "clean_gallery.py"
        test_file.write_text(
            "from dj_design_system.gallery import GalleryConfig\nconfig = GalleryConfig()",
            encoding="utf-8",
        )

        out = StringIO()
        call_command("migrate_gallery_configs", str(tmp_path), check=True, stdout=out)
        assert "All gallery files are up to date" in out.getvalue()
