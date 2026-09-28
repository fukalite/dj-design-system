"""Management command to migrate legacy gallery configuration files to modern GalleryConfig."""

from __future__ import annotations

import ast
import shutil
import subprocess
from pathlib import Path

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError


def migrate_source(source: str, keep_legacy: bool = False) -> tuple[str, bool]:
    """Parse python source code and transform basic_kwargs / maximal_kwargs into GalleryConfig.

    Returns:
        tuple of (transformed_source, modified_boolean)
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return source, False

    has_config = False
    basic_val = None
    max_val = None
    other_stmts = []

    for stmt in tree.body:
        if isinstance(stmt, ast.Assign):
            is_legacy = False
            for target in stmt.targets:
                if isinstance(target, ast.Name):
                    if target.id == "config":
                        has_config = True
                    elif target.id == "basic_kwargs":
                        basic_val = stmt.value
                        is_legacy = True
                    elif target.id == "maximal_kwargs":
                        max_val = stmt.value
                        is_legacy = True
            if is_legacy and not keep_legacy:
                continue
        other_stmts.append(stmt)

    if has_config or (basic_val is None and max_val is None):
        return source, False

    has_gallery_import = False
    for stmt in other_stmts:
        if (
            isinstance(stmt, ast.ImportFrom)
            and stmt.module == "dj_design_system.gallery"
        ):
            has_gallery_import = True
            imported_names = {alias.name for alias in stmt.names}
            if "GalleryConfig" not in imported_names:
                stmt.names.append(ast.alias(name="GalleryConfig"))
            if "Variant" not in imported_names:
                stmt.names.append(ast.alias(name="Variant"))

    import_gallery_stmts = []
    if not has_gallery_import:
        import_gallery_stmts.append(
            ast.ImportFrom(
                module="dj_design_system.gallery",
                names=[ast.alias(name="GalleryConfig"), ast.alias(name="Variant")],
                level=0,
            )
        )

    variants: list[ast.expr] = []
    if basic_val is not None:
        variants.append(
            ast.Call(
                func=ast.Name(id="Variant", ctx=ast.Load()),
                args=[],
                keywords=[
                    ast.keyword(arg="name", value=ast.Constant(value="basic")),
                    ast.keyword(arg="kwargs", value=basic_val),
                ],
            )
        )
    if max_val is not None:
        variants.append(
            ast.Call(
                func=ast.Name(id="Variant", ctx=ast.Load()),
                args=[],
                keywords=[
                    ast.keyword(arg="name", value=ast.Constant(value="maximal")),
                    ast.keyword(arg="kwargs", value=max_val),
                ],
            )
        )

    config_assign = ast.Assign(
        targets=[ast.Name(id="config", ctx=ast.Store())],
        value=ast.Call(
            func=ast.Name(id="GalleryConfig", ctx=ast.Load()),
            args=[],
            keywords=[
                ast.keyword(
                    arg="variants",
                    value=ast.List(elts=variants, ctx=ast.Load()),
                )
            ],
        ),
    )

    new_tree = ast.Module(
        body=import_gallery_stmts + other_stmts + [config_assign],
        type_ignores=[],
    )
    ast.fix_missing_locations(new_tree)
    unparsed = ast.unparse(new_tree)

    formatted = _format_code(unparsed)
    return formatted, True


def _format_code(code: str) -> str:
    """Format Python code using ruff if available, else return input with newline."""
    ruff_bin = shutil.which("ruff")
    if ruff_bin:
        try:
            res = subprocess.run(
                [ruff_bin, "format", "-"],
                input=code,
                text=True,
                capture_output=True,
                check=True,
            )
            return res.stdout
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
    return code if code.endswith("\n") else code + "\n"


class Command(BaseCommand):
    help = "Migrate legacy gallery configuration files (*_gallery.py) to modern GalleryConfig exports."

    def add_arguments(self, parser):
        parser.add_argument(
            "paths",
            nargs="*",
            type=str,
            help="File or directory paths to migrate. Defaults to all installed apps.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what files would be modified without writing changes.",
        )
        parser.add_argument(
            "--check",
            action="store_true",
            help="Exit with non-zero status if unmigrated gallery files exist.",
        )
        parser.add_argument(
            "--keep-legacy",
            action="store_true",
            help="Keep legacy basic_kwargs and maximal_kwargs variables in addition to config.",
        )

    def _find_candidate_files(self, paths: list[str]) -> list[Path]:
        files: list[Path] = []
        if paths:
            for p in paths:
                path = Path(p)
                if path.is_file() and path.suffix == ".py":
                    files.append(path)
                elif path.is_dir():
                    files.extend(path.rglob("*gallery*.py"))
                    files.extend(path.rglob("gallery.py"))
        else:
            for app_config in apps.get_app_configs():
                app_path = Path(app_config.path)
                if app_path.exists() and "site-packages" not in str(app_path):
                    files.extend(app_path.rglob("*gallery*.py"))
                    files.extend(app_path.rglob("gallery.py"))
        return sorted(list(dict.fromkeys(files)))

    def handle(self, *args, **options):
        candidate_files = self._find_candidate_files(options.get("paths", []))
        migrated_count = 0
        unmigrated_files: list[Path] = []

        for file_path in candidate_files:
            # Skip dj_design_system's own internal gallery.py
            if file_path.name == "gallery.py" and "dj_design_system" in str(file_path):
                continue

            try:
                content = file_path.read_text(encoding="utf-8")
            except OSError as err:
                self.stderr.write(f"Could not read {file_path}: {err}")
                continue

            new_content, modified = migrate_source(
                content, keep_legacy=options.get("keep_legacy", False)
            )
            if modified:
                unmigrated_files.append(file_path)
                if options.get("dry_run"):
                    self.stdout.write(f"Would migrate: {file_path}")
                elif not options.get("check"):
                    file_path.write_text(new_content, encoding="utf-8")
                    self.stdout.write(self.style.SUCCESS(f"Migrated: {file_path}"))
                    migrated_count += 1

        if options.get("check"):
            if unmigrated_files:
                self.stderr.write(
                    self.style.ERROR(
                        f"Found {len(unmigrated_files)} unmigrated gallery file(s):"
                    )
                )
                for f in unmigrated_files:
                    self.stderr.write(f"  - {f}")
                raise CommandError(
                    f"Found {len(unmigrated_files)} unmigrated gallery file(s)."
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS("All gallery files are up to date.")
                )
                return

        if options.get("dry_run"):
            self.stdout.write(
                f"Dry run complete. {len(unmigrated_files)} file(s) would be migrated."
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Migration complete. {migrated_count} file(s) migrated."
                )
            )
