"""Management command to generate typed ``DesignSystemSettings`` from legacy dict settings."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from django.conf import settings as django_settings
from django.core.management.base import BaseCommand, CommandError, CommandParser

from dj_design_system.config import DesignSystemSettings
from dj_design_system.services import config as config_service
from dj_design_system.services import settings_migration as settings_migration_service


class Command(BaseCommand):
    """Print migrated ``DesignSystemSettings`` and optional ``AppConfig`` snippets to stdout."""

    help = "Generate typed DesignSystemSettings (and optional AppConfig.design_system snippets) from settings.DJ_DESIGN_SYSTEM."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--split-apps",
            action="store_true",
            help="Emit AppConfig.design_system snippets for local project apps and keep third-party apps in DesignSystemSettings.apps.",
        )
        parser.add_argument(
            "--app",
            action="append",
            dest="apps",
            default=[],
            help="Emit migration snippet(s) for specific app label(s) only (repeatable).",
        )
        parser.add_argument(
            "--check",
            action="store_true",
            help="Exit non-zero if DJ_DESIGN_SYSTEM still uses legacy dict syntax, COMPONENT_NAMESPACES, or unresolved # MANUAL: expressions.",
        )
        parser.add_argument(
            "--no-format",
            action="store_true",
            help="Do not pipe generated Python code through `ruff format -`.",
        )
        parser.add_argument(
            "--include-defaults",
            action="store_true",
            help="Include default-valued fields explicitly in generated dataclasses.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        raw = getattr(django_settings, "DJ_DESIGN_SYSTEM", None)
        split_apps: bool = bool(options["split_apps"])
        selected_apps: list[str] = list(options["apps"] or [])
        check_mode: bool = bool(options["check"])
        format_with_ruff: bool = not bool(options["no_format"])
        include_defaults: bool = bool(options["include_defaults"])

        if check_mode:
            issues = settings_migration_service.check_migration_status(raw=raw)
            if issues:
                raise CommandError("\n".join(issues))
            self.stdout.write("DJ_DESIGN_SYSTEM is migrated and clean.")
            return

        if raw is None:
            resolved = DesignSystemSettings()
            ast_hints: list[str] = []
        elif isinstance(raw, DesignSystemSettings):
            resolved = raw
            ast_hints = []
        elif isinstance(raw, Mapping):
            resolved = config_service.adapt_legacy_settings(raw=raw)
            ast_hints = settings_migration_service.inspect_active_settings_module()
        else:
            raise CommandError(
                f"settings.DJ_DESIGN_SYSTEM has unsupported type {type(raw).__name__}."
            )

        project_root = settings_migration_service.resolve_project_root()

        if selected_apps:
            for app_label in selected_apps:
                app_cfg = resolved.apps.get(app_label)
                if app_cfg is None:
                    raise CommandError(
                        f"App '{app_label}' has no per-app configuration in DJ_DESIGN_SYSTEM."
                    )
                classification = settings_migration_service.classify_app(
                    app_label=app_label,
                    project_root=project_root,
                )
                snippet = settings_migration_service.render_app_settings_snippet(
                    app_label=app_label,
                    app_settings=app_cfg,
                    classification=classification,
                    include_defaults=include_defaults,
                    format_with_ruff=format_with_ruff,
                )
                self.stdout.write(
                    f"# --- {app_label} ({classification.app_name}/apps.py) ---\n"
                )
                self.stdout.write(snippet)
            return

        local_apps: list[tuple[str, settings_migration_service.AppClassification]] = []
        if split_apps:
            for app_label in sorted(resolved.apps):
                classification = settings_migration_service.classify_app(
                    app_label=app_label,
                    project_root=project_root,
                )
                if classification.is_local:
                    local_apps.append((app_label, classification))

        excluded_apps = {label for label, _ in local_apps}
        project_snippet = settings_migration_service.render_project_settings(
            config=resolved,
            include_defaults=include_defaults,
            format_with_ruff=format_with_ruff,
            ast_hints=ast_hints,
            excluded_apps=excluded_apps,
        )
        self.stdout.write("# --- settings.py ---\n")
        self.stdout.write(project_snippet)

        for app_label, classification in local_apps:
            app_snippet = settings_migration_service.render_app_settings_snippet(
                app_label=app_label,
                app_settings=resolved.apps[app_label],
                classification=classification,
                include_defaults=include_defaults,
                format_with_ruff=format_with_ruff,
            )
            self.stdout.write(
                f"\n# --- {app_label} ({classification.app_name}/apps.py) ---\n"
            )
            self.stdout.write(app_snippet)
