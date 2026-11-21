"""Django system checks for dj-design-system configuration."""

from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from django.apps import apps
from django.conf import settings as django_settings
from django.core import checks

from dj_design_system.config import UNSET, AppSettings, DesignSystemSettings
from dj_design_system.constants import BUILTIN_APP_LABEL, BUILTIN_PREFIX
from dj_design_system.services import config as config_service


_VALID_PREFIX_RE = re.compile(r"^[a-z][a-z0-9_]*$")


def _is_valid_prefix(*, prefix: Any) -> bool:
    return (
        isinstance(prefix, str)
        and bool(_VALID_PREFIX_RE.match(prefix))
        and "__" not in prefix
    )


@checks.register("dj_design_system")
def check_gallery_settings(
    app_configs: Any = None, **kwargs: Any
) -> list[checks.CheckMessage]:
    """Validate DJ_DESIGN_SYSTEM gallery app visibility settings."""
    messages: list[checks.CheckMessage] = []
    raw = getattr(django_settings, "DJ_DESIGN_SYSTEM", None)

    if raw is None:
        raw_include: Any = None
        raw_exclude: Any = ()
    elif isinstance(raw, DesignSystemSettings):
        raw_include = raw.gallery.include_apps
        raw_exclude = raw.gallery.exclude_apps
    elif isinstance(raw, Mapping):
        raw_include = raw.get("GALLERY_INCLUDE_APPS", None)
        raw_exclude = raw.get("GALLERY_EXCLUDE_APPS", ())
    else:
        return messages

    if raw_include is not None and not isinstance(
        raw_include, (list, tuple, set, frozenset)
    ):
        messages.append(
            checks.Error(
                "Gallery include_apps must be a list, tuple, or set of app labels (or None).",
                hint="Set GallerySettings(include_apps=(...)) or leave it as None.",
                id="dj_design_system.E001",
            )
        )
        return messages

    if raw_exclude is not None and not isinstance(
        raw_exclude, (list, tuple, set, frozenset)
    ):
        messages.append(
            checks.Error(
                "Gallery exclude_apps must be a list, tuple, or set of app labels.",
                hint="Set GallerySettings(exclude_apps=(...)) to a sequence of app labels.",
                id="dj_design_system.E002",
            )
        )
        return messages

    include = set(raw_include) if raw_include is not None else set()
    exclude = set(raw_exclude) if raw_exclude is not None else set()

    overlap = include & exclude
    if overlap:
        messages.append(
            checks.Error(
                f"The following app(s) appear in both include_apps and exclude_apps: {', '.join(sorted(overlap))}.",
                hint="Remove the overlapping app(s) from either include_apps or exclude_apps.",
                id="dj_design_system.E003",
            )
        )

    if raw_include is not None and exclude:
        messages.append(
            checks.Warning(
                "Both include_apps and exclude_apps are defined. When include_apps is set, exclude_apps is ignored.",
                hint="Use include_apps alone to restrict visible apps.",
                id="dj_design_system.W001",
            )
        )

    installed_apps = {app.label for app in apps.get_app_configs()} | {BUILTIN_APP_LABEL}
    for app_label in sorted((include | exclude) - installed_apps):
        messages.append(
            checks.Warning(
                f"App '{app_label}' configured in gallery settings is not in INSTALLED_APPS.",
                hint="Check for typos or ensure the app is added to INSTALLED_APPS.",
                id="dj_design_system.W002",
            )
        )

    return messages


def _check_theme_integrity(
    *,
    config: DesignSystemSettings,
    messages: list[checks.CheckMessage],
) -> None:
    for slug, theme in config.themes.items():
        if theme.value != slug:
            messages.append(
                checks.Error(
                    f"Theme key '{slug}' does not match Theme.value '{theme.value}'.",
                    hint="Omit Theme.value or set it to match its mapping key.",
                    id="dj_design_system.E012",
                )
            )
        if (
            isinstance(theme.canvas_background, str)
            and theme.canvas_background not in config.canvas.backgrounds
        ):
            messages.append(
                checks.Warning(
                    f"Theme '{slug}' references unknown canvas_background '{theme.canvas_background}'.",
                    hint="Add the slug to CanvasSettings.backgrounds or pass a CanvasBackground instance.",
                    id="dj_design_system.W005",
                )
            )
        if (
            theme.dark_mode is not None
            and isinstance(theme.dark_mode.canvas_background, str)
            and theme.dark_mode.canvas_background not in config.canvas.backgrounds
        ):
            messages.append(
                checks.Warning(
                    f"Theme '{slug}' dark_mode references unknown canvas_background '{theme.dark_mode.canvas_background}'.",
                    hint="Add the slug to CanvasSettings.backgrounds or pass a CanvasBackground instance.",
                    id="dj_design_system.W005",
                )
            )

    for slug, theme in config.gallery.ui_themes.items():
        if theme.value != slug:
            messages.append(
                checks.Error(
                    f"UI theme key '{slug}' does not match Theme.value '{theme.value}'.",
                    hint="Omit Theme.value or set it to match its mapping key.",
                    id="dj_design_system.E012",
                )
            )

    if not config.themes or config.default_theme not in config.themes:
        messages.append(
            checks.Warning(
                f"default_theme '{config.default_theme}' is not present in themes.",
                hint="Set default_theme to a key defined in DesignSystemSettings.themes.",
                id="dj_design_system.W004",
            )
        )

    if (
        not config.gallery.ui_themes
        or config.gallery.default_ui_theme not in config.gallery.ui_themes
    ):
        messages.append(
            checks.Warning(
                f"default_ui_theme '{config.gallery.default_ui_theme}' is not present in gallery.ui_themes.",
                hint="Set GallerySettings.default_ui_theme to a key defined in gallery.ui_themes.",
                id="dj_design_system.W004",
            )
        )

    if (
        not config.canvas.backgrounds
        or config.canvas.default_background not in config.canvas.backgrounds
    ):
        messages.append(
            checks.Warning(
                f"default_background '{config.canvas.default_background}' is not present in canvas.backgrounds.",
                hint="Set CanvasSettings.default_background to a key defined in canvas.backgrounds.",
                id="dj_design_system.W004",
            )
        )


def _check_app_settings(
    *,
    config: DesignSystemSettings,
    installed_configs: Mapping[str, Any],
    messages: list[checks.CheckMessage],
) -> None:
    installed_labels = set(installed_configs.keys()) | {BUILTIN_APP_LABEL}

    builtin_override = config.apps.get(BUILTIN_APP_LABEL)
    if builtin_override is not None and (
        builtin_override.prefix is not UNSET
        or builtin_override.flatten is not UNSET
        or builtin_override.short_names is not UNSET
    ):
        messages.append(
            checks.Error(
                f"DJ_DESIGN_SYSTEM.apps['{BUILTIN_APP_LABEL}'] cannot override prefix, flatten, or short_names.",
                hint="Remove prefix, flatten, and short_names from apps['dj_design_system'].",
                id="dj_design_system.E011",
            )
        )

    for unknown_app in sorted(set(config.apps.keys()) - installed_labels):
        messages.append(
            checks.Warning(
                f"App '{unknown_app}' in DJ_DESIGN_SYSTEM.apps is not in INSTALLED_APPS.",
                hint="Check for typos or add the app to INSTALLED_APPS.",
                id="dj_design_system.W003",
            )
        )

    all_labels = sorted(set(installed_configs.keys()) | set(config.apps.keys()))
    prefix_owners: dict[str, list[str]] = {}
    promoted_slug_owners: dict[str, list[tuple[str, str]]] = {}

    for app_label in all_labels:
        resolved = config_service.get_app_settings(app_label=app_label)
        is_installed = app_label in installed_configs

        if app_label != BUILTIN_APP_LABEL and resolved.prefix is not None:
            if not _is_valid_prefix(prefix=resolved.prefix):
                messages.append(
                    checks.Error(
                        f"App '{app_label}' has invalid component prefix '{resolved.prefix}'.",
                        hint="Use lowercase letters, digits, and single underscores, starting with a letter and containing no '__'.",
                        id="dj_design_system.E004",
                    )
                )
            elif resolved.prefix == BUILTIN_PREFIX:
                messages.append(
                    checks.Error(
                        f"App '{app_label}' cannot use the reserved whole-app prefix '{BUILTIN_PREFIX}'.",
                        hint="Choose a unique app prefix, or configure DirectorySettings(prefix='dds') on a subfolder to shadow built-ins.",
                        id="dj_design_system.E005",
                    )
                )
            elif is_installed:
                prefix_owners.setdefault(resolved.prefix, []).append(app_label)
        elif app_label != BUILTIN_APP_LABEL and is_installed:
            app_path = getattr(installed_configs[app_label], "path", None)
            if app_path and (Path(app_path) / "components").is_dir():
                prefix_owners.setdefault(app_label, []).append(app_label)

        for dir_path, dir_cfg in resolved.directories.items():
            if dir_cfg.prefix is not None and not _is_valid_prefix(
                prefix=dir_cfg.prefix
            ):
                messages.append(
                    checks.Error(
                        f"Directory '{dir_path}' in app '{app_label}' has invalid prefix '{dir_cfg.prefix}'.",
                        hint="Use lowercase letters, digits, and single underscores, starting with a letter and containing no '__'.",
                        id="dj_design_system.E004",
                    )
                )

        if resolved.themes is not None:
            if len(resolved.themes) == 0:
                messages.append(
                    checks.Warning(
                        f"App '{app_label}' configures an empty themes allowlist.",
                        hint="Specify at least one theme slug or set themes=None to allow all project themes.",
                        id="dj_design_system.W006",
                    )
                )
            else:
                for theme_slug in resolved.themes:
                    if theme_slug not in config.themes:
                        messages.append(
                            checks.Warning(
                                f"App '{app_label}' references unknown theme '{theme_slug}'.",
                                hint="Define the theme in DesignSystemSettings.themes or remove it from AppSettings.themes.",
                                id="dj_design_system.W006",
                            )
                        )

        promoted_paths = sorted(
            path for path, cfg in resolved.directories.items() if cfg.promote_to_app
        )
        for idx, path in enumerate(promoted_paths):
            slug = path.split(".")[-1]
            promoted_slug_owners.setdefault(slug, []).append((app_label, path))
            if slug in installed_labels:
                messages.append(
                    checks.Error(
                        f"Promoted directory '{path}' in app '{app_label}' collides with installed app label '{slug}'.",
                        hint="Rename the directory or disable promote_to_app to avoid gallery URL collisions.",
                        id="dj_design_system.E013",
                    )
                )
            for other in promoted_paths[idx + 1 :]:
                if other.startswith(f"{path}."):
                    messages.append(
                        checks.Error(
                            f"Promoted directory '{other}' is nested inside promoted parent '{path}' in app '{app_label}'.",
                            hint="Only promote one level of a directory hierarchy.",
                            id="dj_design_system.E013",
                        )
                    )

        if is_installed and resolved.directories:
            app_path = getattr(installed_configs[app_label], "path", None)
            if app_path:
                components_root = Path(app_path) / "components"
                for dir_path in sorted(resolved.directories.keys()):
                    target = components_root.joinpath(*dir_path.split("."))
                    if not target.is_dir():
                        messages.append(
                            checks.Warning(
                                f"Configured directory '{dir_path}' in app '{app_label}' does not exist under '{components_root}'.",
                                hint="Verify the dotted path matches a subfolder under the app's components/ directory.",
                                id="dj_design_system.W007",
                            )
                        )

    for prefix, owners in sorted(prefix_owners.items()):
        if len(owners) > 1:
            messages.append(
                checks.Error(
                    f"Duplicate component prefix '{prefix}' configured for apps: {', '.join(sorted(owners))}.",
                    hint="Override AppSettings(prefix=...) in DJ_DESIGN_SYSTEM.apps for one of the conflicting apps.",
                    id="dj_design_system.E006",
                )
            )

    for slug, promoted_owners in sorted(promoted_slug_owners.items()):
        if len(promoted_owners) > 1:
            formatted = ", ".join(f"{app}:{path}" for app, path in promoted_owners)
            messages.append(
                checks.Error(
                    f"Promoted directory slug '{slug}' collides across: {formatted}.",
                    hint="Ensure every promoted directory uses a unique final path segment.",
                    id="dj_design_system.E013",
                )
            )


@checks.register("dj_design_system")
def check_design_system_settings(
    app_configs: Any = None, **kwargs: Any
) -> list[checks.CheckMessage]:
    """Validate typed DesignSystemSettings, devolved AppConfig defaults, and cross-references."""
    messages: list[checks.CheckMessage] = []
    raw = getattr(django_settings, "DJ_DESIGN_SYSTEM", None)

    if raw is not None and not isinstance(raw, (DesignSystemSettings, Mapping)):
        messages.append(
            checks.Error(
                f"settings.DJ_DESIGN_SYSTEM must be a DesignSystemSettings instance, mapping, or None; got {type(raw).__name__}.",
                hint="Assign DesignSystemSettings(...) to DJ_DESIGN_SYSTEM in settings.py.",
                id="dj_design_system.E009",
            )
        )
        return messages

    installed_configs = {app.label: app for app in apps.get_app_configs()}
    for app_label, app_cfg in sorted(installed_configs.items()):
        declared = getattr(app_cfg, "design_system", None)
        if declared is not None and not isinstance(declared, AppSettings):
            messages.append(
                checks.Error(
                    f"AppConfig '{app_label}.design_system' must be an AppSettings instance or None; got {type(declared).__name__}.",
                    hint="Set design_system = AppSettings(...) on your AppConfig subclass.",
                    id="dj_design_system.E010",
                )
            )

    try:
        config = config_service.get_config()
    except (TypeError, ValueError) as exc:
        messages.append(
            checks.Error(
                f"Invalid settings.DJ_DESIGN_SYSTEM configuration: {exc}",
                hint="Fix the invalid value in settings.DJ_DESIGN_SYSTEM.",
                id="dj_design_system.E009",
            )
        )
        return messages

    _check_theme_integrity(config=config, messages=messages)
    _check_app_settings(
        config=config,
        installed_configs=installed_configs,
        messages=messages,
    )
    return messages
