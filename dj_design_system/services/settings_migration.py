"""Code-generation, AST inspection, and app-classification service for ``migrate_dds_settings``."""

from __future__ import annotations

import ast
import importlib.util
import os
import shutil
import subprocess
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from django.apps import AppConfig, apps
from django.conf import settings as django_settings

from dj_design_system.config import (
    DDS_DEFAULT_CANVAS_BACKGROUNDS,
    DDS_DEFAULT_DOC_VARIANTS,
    DDS_DEFAULT_NAV_ORDER,
    DDS_DEFAULT_THEMES,
    DDS_DEFAULT_UI_THEMES,
    UNSET,
    AppSettings,
    CanvasBackground,
    CanvasSettings,
    DarkModeConfig,
    DesignSystemSettings,
    DirectorySettings,
    DocVariantConfig,
    GallerySettings,
    Theme,
)
from dj_design_system.constants import BUILTIN_APP_LABEL
from dj_design_system.types import NodeType


_EXCLUDED_DIR_SEGMENTS: frozenset[str] = frozenset(
    {
        ".venv",
        "venv",
        "env",
        "site-packages",
        "dist-packages",
        ".tox",
        ".nox",
        "node_modules",
    }
)

_SAFE_CALL_NAMES: frozenset[str] = frozenset(
    {
        "DesignSystemSettings",
        "GallerySettings",
        "CanvasSettings",
        "AppSettings",
        "DirectorySettings",
        "Theme",
        "DarkModeConfig",
        "CanvasBackground",
        "DocVariantConfig",
        "FlattenStrategy",
        "NodeType",
        "DocVariantStrategy",
        "tuple",
        "list",
        "dict",
        "set",
        "frozenset",
    }
)


@dataclass(frozen=True)
class AppClassification:
    """Classification metadata for an app when generating ``--split-apps`` output."""

    app_label: str
    app_name: str
    app_path: Path | None
    is_local: bool
    has_apps_py: bool
    uses_default_app_config: bool
    already_has_design_system: bool
    config_class_name: str


def resolve_project_root() -> Path | None:
    """Resolve the project root directory from ``settings.BASE_DIR`` or ``DJANGO_SETTINGS_MODULE``."""
    base_dir = getattr(django_settings, "BASE_DIR", None)
    if base_dir is not None:
        return Path(base_dir).resolve()
    module_name = os.environ.get("DJANGO_SETTINGS_MODULE")
    if module_name:
        spec = importlib.util.find_spec(module_name)
        if spec and spec.origin:
            return Path(spec.origin).resolve().parent.parent
    return None


def classify_app(
    *,
    app_label: str,
    project_root: Path | None,
) -> AppClassification:
    """Determine whether *app_label* is a local project app safe for ``--split-apps``."""
    try:
        app_config = apps.get_app_config(app_label)
    except LookupError:
        return AppClassification(
            app_label=app_label,
            app_name=app_label,
            app_path=None,
            is_local=False,
            has_apps_py=False,
            uses_default_app_config=False,
            already_has_design_system=False,
            config_class_name=f"{app_label.title().replace('_', '')}Config",
        )

    app_name = str(getattr(app_config, "name", app_label))
    raw_path = getattr(app_config, "path", None)
    resolved_path = Path(raw_path).resolve() if raw_path else None
    has_apps_py = bool(resolved_path and (resolved_path / "apps.py").exists())
    uses_default = type(app_config) is AppConfig
    already_has_ds = getattr(app_config, "design_system", None) is not None
    default_cls_name = f"{app_label.title().replace('_', '')}Config"
    config_class_name = default_cls_name if uses_default else type(app_config).__name__

    is_local = False
    if (
        app_label != BUILTIN_APP_LABEL
        and not app_name.startswith("django.")
        and project_root is not None
        and resolved_path is not None
    ):
        resolved_root = project_root.resolve()
        if resolved_path.is_relative_to(resolved_root):
            rel_parts = resolved_path.relative_to(resolved_root).parts
            if not any(part in _EXCLUDED_DIR_SEGMENTS for part in rel_parts):
                is_local = True

    return AppClassification(
        app_label=app_label,
        app_name=app_name,
        app_path=resolved_path,
        is_local=is_local,
        has_apps_py=has_apps_py,
        uses_default_app_config=uses_default,
        already_has_design_system=already_has_ds,
        config_class_name=config_class_name,
    )


def _call_name(node: ast.Call) -> str:
    if isinstance(node.func, ast.Name):
        return node.func.id
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    return ""


def _record_unique_hint(*, hints: list[str], seen: set[str], message: str) -> None:
    if message not in seen:
        seen.add(message)
        hints.append(message)


def inspect_settings_source(*, source: str) -> list[str]:
    """Inspect a settings module's Python source via AST and return ``# MANUAL:`` hint lines."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return [
            "AST could not parse settings module source; verify migration manually."
        ]

    target_value: ast.expr | None = None
    for stmt in tree.body:
        if isinstance(stmt, ast.Assign):
            for target in stmt.targets:
                if isinstance(target, ast.Name) and target.id == "DJ_DESIGN_SYSTEM":
                    target_value = stmt.value
        elif (
            isinstance(stmt, ast.AnnAssign)
            and isinstance(stmt.target, ast.Name)
            and stmt.target.id == "DJ_DESIGN_SYSTEM"
            and stmt.value is not None
        ):
            target_value = stmt.value

    if target_value is None:
        return [
            "AST could not locate a top-level DJ_DESIGN_SYSTEM assignment; verify dynamic or split settings manually."
        ]

    hints: list[str] = []
    seen: set[str] = set()

    for node in ast.walk(target_value):
        if isinstance(node, ast.Dict):
            for key, val in zip(node.keys, node.values):
                if key is None:
                    unpacked = ast.unparse(val)
                    _record_unique_hint(
                        hints=hints,
                        seen=seen,
                        message=(
                            f"Detected dict unpacking (**{unpacked}); consider inheriting with .replace(...) instead."
                        ),
                    )
        elif isinstance(node, ast.Lambda):
            _record_unique_hint(
                hints=hints,
                seen=seen,
                message=(
                    f"Callable (lambda) detected ({ast.unparse(node)}); copy or reference a named function manually."
                ),
            )
        elif isinstance(node, ast.Name) and node.id == "BASE_DIR":
            _record_unique_hint(
                hints=hints,
                seen=seen,
                message="BASE_DIR-derived path detected; verify path expression manually.",
            )
        elif isinstance(node, ast.IfExp):
            _record_unique_hint(
                hints=hints,
                seen=seen,
                message=(
                    f"Dynamic expression detected ({ast.unparse(node)}); preserve conditional logic manually."
                ),
            )
        elif isinstance(node, ast.Call):
            name = _call_name(node)
            if name == "partial":
                _record_unique_hint(
                    hints=hints,
                    seen=seen,
                    message=(
                        f"Callable (functools.partial) detected ({ast.unparse(node)}); preserve callable manually."
                    ),
                )
            elif name not in _SAFE_CALL_NAMES:
                _record_unique_hint(
                    hints=hints,
                    seen=seen,
                    message=(
                        f"Dynamic expression detected ({ast.unparse(node)}); verify runtime evaluation manually."
                    ),
                )
        elif (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == "os"
            and node.attr == "environ"
        ):
            _record_unique_hint(
                hints=hints,
                seen=seen,
                message=(
                    "Dynamic expression detected (os.environ); preserve environment lookup manually."
                ),
            )

    return hints


def check_migration_status(*, raw: Any) -> list[str]:
    """Return blocking migration issues for ``manage.py migrate_dds_settings --check``."""
    issues: list[str] = []
    if isinstance(raw, Mapping):
        issues.append("settings.DJ_DESIGN_SYSTEM uses deprecated legacy dict syntax.")
        if raw.get("COMPONENT_NAMESPACES"):
            issues.append(
                "DJ_DESIGN_SYSTEM['COMPONENT_NAMESPACES'] is still configured."
            )
        for hint in inspect_active_settings_module():
            issues.append(f"# MANUAL: {hint}")
    elif raw is not None and not isinstance(raw, DesignSystemSettings):
        issues.append(
            f"settings.DJ_DESIGN_SYSTEM must be DesignSystemSettings or None, got {type(raw).__name__}."
        )
    return issues


def inspect_active_settings_module() -> list[str]:
    """Locate the active ``DJANGO_SETTINGS_MODULE`` file and return AST ``# MANUAL:`` hints."""
    module_name = os.environ.get("DJANGO_SETTINGS_MODULE")
    if not module_name:
        return ["DJANGO_SETTINGS_MODULE is not set; AST inspection skipped."]
    spec = importlib.util.find_spec(module_name)
    if not spec or not spec.origin:
        return [
            f"AST could not locate source file for settings module '{module_name}'."
        ]
    try:
        source = Path(spec.origin).read_text(encoding="utf-8")
    except OSError:
        return [f"AST could not read settings file '{spec.origin}'."]
    return inspect_settings_source(source=source)


def format_python_code(*, code: str) -> str:
    """Format *code* with ``ruff format -`` when available, falling back cleanly."""
    ruff_bin = shutil.which("ruff")
    if not ruff_bin:
        return code
    try:
        completed = subprocess.run(
            [ruff_bin, "format", "-"],
            input=code,
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError:
        return code
    if completed.returncode == 0 and completed.stdout:
        return completed.stdout
    return code


class _SettingsCodeEmitter:
    """Serialises ``DesignSystemSettings`` and ``AppSettings`` into minimal executable Python."""

    def __init__(self, *, include_defaults: bool = False) -> None:
        self.include_defaults = include_defaults
        self.config_imports: set[str] = set()
        self.types_imports: set[str] = set()
        self.manual_notes: list[str] = []

    def _use_config(self, symbol: str) -> str:
        self.config_imports.add(symbol)
        return symbol

    def _use_types(self, symbol: str) -> str:
        self.types_imports.add(symbol)
        return symbol

    def _emit_nav_order(self, value: Any) -> str:
        if value == "alphabetical":
            return repr("alphabetical")
        if isinstance(value, (list, tuple)):
            parts: list[str] = []
            for item in value:
                if isinstance(item, NodeType):
                    parts.append(f"{self._use_config('NodeType')}.{item.name}")
                else:
                    parts.append(repr(str(item)))
            if len(parts) == 1:
                return f"({parts[0]},)"
            return f"({', '.join(parts)})"
        return repr(value)

    def _emit_html_attrs(self, value: Mapping[str, Any]) -> str:
        plain = {
            section: {k: v for k, v in attrs.items()}
            for section, attrs in value.items()
        }
        return repr(plain)

    def _emit_canvas_background(self, bg: CanvasBackground) -> str:
        cls = self._use_config("CanvasBackground")
        if bg.label:
            return f"{cls}(label={bg.label!r}, color={bg.color!r})"
        return f"{cls}(color={bg.color!r})"

    def _emit_theme_canvas_background(self, bg: Any) -> str:
        if isinstance(bg, CanvasBackground):
            return self._emit_canvas_background(bg)
        return repr(bg)

    def _emit_dark_mode(self, dm: DarkModeConfig) -> str:
        cls = self._use_config("DarkModeConfig")
        default_dm = DarkModeConfig()
        args: list[str] = []
        if self.include_defaults or dm.html_attrs != default_dm.html_attrs:
            args.append(f"html_attrs={self._emit_html_attrs(dm.html_attrs)}")
        if self.include_defaults or dm.css != default_dm.css:
            args.append(f"css={tuple(dm.css)!r}")
        if self.include_defaults or dm.js != default_dm.js:
            args.append(f"js={tuple(dm.js)!r}")
        if self.include_defaults or dm.css_bundles != default_dm.css_bundles:
            args.append(f"css_bundles={tuple(dm.css_bundles)!r}")
        if self.include_defaults or dm.js_bundles != default_dm.js_bundles:
            args.append(f"js_bundles={tuple(dm.js_bundles)!r}")
        if (
            self.include_defaults
            or dm.canvas_background != default_dm.canvas_background
        ):
            args.append(
                f"canvas_background={self._emit_theme_canvas_background(dm.canvas_background)}"
            )
        return f"{cls}({', '.join(args)})"

    def _emit_theme(self, slug: str, theme: Theme) -> str:
        cls = self._use_config("Theme")
        args: list[str] = []
        if self.include_defaults or (theme.value and theme.value != slug):
            args.append(f"value={theme.value!r}")
        if self.include_defaults or theme.label != slug.capitalize():
            args.append(f"label={theme.label!r}")
        if self.include_defaults or dict(theme.html_attrs):
            args.append(f"html_attrs={self._emit_html_attrs(theme.html_attrs)}")
        if self.include_defaults or theme.css:
            args.append(f"css={tuple(theme.css)!r}")
        if self.include_defaults or theme.js:
            args.append(f"js={tuple(theme.js)!r}")
        if self.include_defaults or theme.css_bundles:
            args.append(f"css_bundles={tuple(theme.css_bundles)!r}")
        if self.include_defaults or theme.js_bundles:
            args.append(f"js_bundles={tuple(theme.js_bundles)!r}")
        if self.include_defaults or theme.canvas_background is not None:
            args.append(
                f"canvas_background={self._emit_theme_canvas_background(theme.canvas_background)}"
            )
        if self.include_defaults or theme.dark_mode is not None:
            dm_expr = (
                "None"
                if theme.dark_mode is None
                else self._emit_dark_mode(theme.dark_mode)
            )
            args.append(f"dark_mode={dm_expr}")
        return f"{cls}({', '.join(args)})"

    def _emit_doc_variant(self, key: str, dv: DocVariantConfig) -> str:
        cls = self._use_config("DocVariantConfig")
        strat_cls = self._use_types("DocVariantStrategy")
        args = [
            f"key={dv.key!r}",
            f"name={dv.name!r}",
            f"label={dv.label!r}",
            f"strategy={strat_cls}.{dv.strategy.name}",
            f"show_in_docs={dv.show_in_docs!r}",
        ]
        if self.include_defaults or dict(dv.kwargs):
            args.append(f"kwargs={dict(dv.kwargs)!r}")
        if dv.param_factory is not None:
            self.manual_notes.append(
                f"DocVariantConfig '{key}' has non-literal param_factory; restore callable manually."
            )
            args.append("param_factory=None")
        if dv.slot_factory is not None:
            self.manual_notes.append(
                f"DocVariantConfig '{key}' has non-literal slot_factory; restore callable manually."
            )
            args.append("slot_factory=None")
        return f"{cls}({', '.join(args)})"

    def _emit_backgrounds_mapping(
        self, backgrounds: Mapping[str, CanvasBackground]
    ) -> str:
        if not self.include_defaults and all(
            slug in backgrounds and backgrounds[slug] == bg
            for slug, bg in DDS_DEFAULT_CANVAS_BACKGROUNDS.items()
        ):
            extras = {
                slug: bg
                for slug, bg in backgrounds.items()
                if slug not in DDS_DEFAULT_CANVAS_BACKGROUNDS
            }
            if not extras:
                return self._use_config("DDS_DEFAULT_CANVAS_BACKGROUNDS")
            base_sym = self._use_config("DDS_DEFAULT_CANVAS_BACKGROUNDS")
            extra_items = ", ".join(
                f"{slug!r}: {self._emit_canvas_background(bg)}"
                for slug, bg in extras.items()
            )
            return f"{{**{base_sym}, {extra_items}}}"

        items = ", ".join(
            f"{slug!r}: {self._emit_canvas_background(bg)}"
            for slug, bg in backgrounds.items()
        )
        return f"{{{items}}}"

    def _emit_doc_variants_mapping(
        self, variants: Mapping[str, DocVariantConfig]
    ) -> str:
        if not self.include_defaults and all(
            key in variants for key in DDS_DEFAULT_DOC_VARIANTS
        ):
            changed = {
                key: dv
                for key, dv in variants.items()
                if key not in DDS_DEFAULT_DOC_VARIANTS
                or DDS_DEFAULT_DOC_VARIANTS[key] != dv
            }
            if not changed:
                return self._use_config("DDS_DEFAULT_DOC_VARIANTS")
            base_sym = self._use_config("DDS_DEFAULT_DOC_VARIANTS")
            changed_items = ", ".join(
                f"{key!r}: {self._emit_doc_variant(key, dv)}"
                for key, dv in changed.items()
            )
            return f"{{**{base_sym}, {changed_items}}}"

        items = ", ".join(
            f"{key!r}: {self._emit_doc_variant(key, dv)}"
            for key, dv in variants.items()
        )
        return f"{{{items}}}"

    def _emit_directory(self, directory: DirectorySettings) -> str:
        cls = self._use_config("DirectorySettings")
        args: list[str] = []
        if self.include_defaults or directory.prefix is not None:
            args.append(f"prefix={directory.prefix!r}")
        if self.include_defaults or directory.flatten is not None:
            if directory.flatten is None:
                args.append("flatten=None")
            else:
                args.append(
                    f"flatten={self._use_config('FlattenStrategy')}.{directory.flatten.name}"
                )
        if self.include_defaults or directory.label is not None:
            args.append(f"label={directory.label!r}")
        if self.include_defaults or directory.promote_to_app:
            args.append(f"promote_to_app={directory.promote_to_app!r}")
        if self.include_defaults or directory.order is not None:
            args.append(f"order={directory.order!r}")
        if self.include_defaults or directory.nav_order is not None:
            nav_expr = (
                "None"
                if directory.nav_order is None
                else self._emit_nav_order(directory.nav_order)
            )
            args.append(f"nav_order={nav_expr}")
        return f"{cls}({', '.join(args)})"

    def emit_app_settings(self, app: AppSettings) -> str:
        cls = self._use_config("AppSettings")
        args: list[str] = []
        if app.label is not UNSET:
            args.append(f"label={app.label!r}")
        if app.order is not UNSET:
            args.append(f"order={app.order!r}")
        if app.nav_order is not UNSET:
            args.append(f"nav_order={self._emit_nav_order(app.nav_order)}")
        if app.prefix is not UNSET:
            args.append(f"prefix={app.prefix!r}")
        if app.flatten is not UNSET:
            args.append(
                f"flatten={self._use_config('FlattenStrategy')}.{app.flatten.name}"
            )
        if app.short_names is not UNSET:
            args.append(f"short_names={app.short_names!r}")
        if app.themes is not UNSET:
            themes_val = None if app.themes is None else tuple(app.themes)
            args.append(f"themes={themes_val!r}")
        if app.css is not UNSET:
            args.append(f"css={tuple(app.css)!r}")
        if app.extra_css is not UNSET:
            args.append(f"extra_css={tuple(app.extra_css)!r}")
        if app.js is not UNSET:
            args.append(f"js={tuple(app.js)!r}")
        if app.extra_js is not UNSET:
            args.append(f"extra_js={tuple(app.extra_js)!r}")
        if app.css_bundles is not UNSET:
            args.append(f"css_bundles={tuple(app.css_bundles)!r}")
        if app.js_bundles is not UNSET:
            args.append(f"js_bundles={tuple(app.js_bundles)!r}")
        if app.canvas_html_attrs is not UNSET:
            attrs_expr = (
                "None"
                if app.canvas_html_attrs is None
                else self._emit_html_attrs(app.canvas_html_attrs)
            )
            args.append(f"canvas_html_attrs={attrs_expr}")
        if app.directories is not UNSET:
            if app.directories is None:
                args.append("directories=None")
            else:
                dir_items = ", ".join(
                    f"{path!r}: {'None' if entry is None else self._emit_directory(entry)}"
                    for path, entry in app.directories.items()
                )
                args.append(f"directories={{{dir_items}}}")
        return f"{cls}({', '.join(args)})"

    def _emit_gallery_settings(self, gallery: GallerySettings) -> str | None:
        default_g = GallerySettings()
        args: list[str] = []
        if self.include_defaults or gallery.enabled != default_g.enabled:
            args.append(f"enabled={gallery.enabled!r}")
        if self.include_defaults or gallery.is_public != default_g.is_public:
            args.append(f"is_public={gallery.is_public!r}")
        if self.include_defaults or gallery.app_order != default_g.app_order:
            args.append(f"app_order={tuple(gallery.app_order)!r}")
        if self.include_defaults or gallery.nav_order != DDS_DEFAULT_NAV_ORDER:
            args.append(f"nav_order={self._emit_nav_order(gallery.nav_order)}")
        if (
            self.include_defaults
            or gallery.codehilite_style != default_g.codehilite_style
        ):
            args.append(f"codehilite_style={gallery.codehilite_style!r}")
        if self.include_defaults or gallery.ui_themes != DDS_DEFAULT_UI_THEMES:
            items = ", ".join(
                f"{slug!r}: {self._emit_theme(slug, theme)}"
                for slug, theme in gallery.ui_themes.items()
            )
            args.append(f"ui_themes={{{items}}}")
        if (
            self.include_defaults
            or gallery.default_ui_theme != default_g.default_ui_theme
        ):
            args.append(f"default_ui_theme={gallery.default_ui_theme!r}")
        if self.include_defaults or gallery.include_apps != default_g.include_apps:
            inc = None if gallery.include_apps is None else tuple(gallery.include_apps)
            args.append(f"include_apps={inc!r}")
        if self.include_defaults or gallery.exclude_apps != default_g.exclude_apps:
            args.append(f"exclude_apps={tuple(gallery.exclude_apps)!r}")
        if self.include_defaults or gallery.extra_css != default_g.extra_css:
            args.append(f"extra_css={tuple(gallery.extra_css)!r}")
        if self.include_defaults or gallery.doc_variants != DDS_DEFAULT_DOC_VARIANTS:
            args.append(
                f"doc_variants={self._emit_doc_variants_mapping(gallery.doc_variants)}"
            )
        if not args:
            return None
        cls = self._use_config("GallerySettings")
        return f"{cls}({', '.join(args)})"

    def _emit_canvas_settings(self, canvas: CanvasSettings) -> str | None:
        default_c = CanvasSettings()
        args: list[str] = []
        if (
            self.include_defaults
            or canvas.backgrounds != DDS_DEFAULT_CANVAS_BACKGROUNDS
        ):
            args.append(
                f"backgrounds={self._emit_backgrounds_mapping(canvas.backgrounds)}"
            )
        if (
            self.include_defaults
            or canvas.default_background != default_c.default_background
        ):
            args.append(f"default_background={canvas.default_background!r}")
        if self.include_defaults or dict(canvas.html_attrs):
            args.append(f"html_attrs={self._emit_html_attrs(canvas.html_attrs)}")
        if not args:
            return None
        cls = self._use_config("CanvasSettings")
        return f"{cls}({', '.join(args)})"

    def emit_design_system_settings(
        self,
        *,
        config: DesignSystemSettings,
        excluded_apps: set[str] | None = None,
    ) -> str:
        default_cfg = DesignSystemSettings()
        cls = self._use_config("DesignSystemSettings")
        args: list[str] = []

        if self.include_defaults or config.name != default_cfg.name:
            args.append(f"name={config.name!r}")
        if self.include_defaults or config.css != default_cfg.css:
            args.append(f"css={tuple(config.css)!r}")
        if self.include_defaults or config.js != default_cfg.js:
            args.append(f"js={tuple(config.js)!r}")
        if self.include_defaults or config.css_bundles != default_cfg.css_bundles:
            args.append(f"css_bundles={tuple(config.css_bundles)!r}")
        if self.include_defaults or config.js_bundles != default_cfg.js_bundles:
            args.append(f"js_bundles={tuple(config.js_bundles)!r}")
        if self.include_defaults or config.themes != DDS_DEFAULT_THEMES:
            items = ", ".join(
                f"{slug!r}: {self._emit_theme(slug, theme)}"
                for slug, theme in config.themes.items()
            )
            args.append(f"themes={{{items}}}")
        if self.include_defaults or config.default_theme != default_cfg.default_theme:
            args.append(f"default_theme={config.default_theme!r}")

        gallery_expr = self._emit_gallery_settings(config.gallery)
        if gallery_expr is not None:
            args.append(f"gallery={gallery_expr}")

        canvas_expr = self._emit_canvas_settings(config.canvas)
        if canvas_expr is not None:
            args.append(f"canvas={canvas_expr}")

        excluded = excluded_apps or set()
        remaining_apps = {
            label: app_cfg
            for label, app_cfg in config.apps.items()
            if label not in excluded
        }
        if self.include_defaults or remaining_apps:
            app_items = ", ".join(
                f"{label!r}: {self.emit_app_settings(app_cfg)}"
                for label, app_cfg in remaining_apps.items()
            )
            args.append(f"apps={{{app_items}}}")

        return f"DJ_DESIGN_SYSTEM = {cls}({', '.join(args)})\n"

    def render_imports(self) -> str:
        lines: list[str] = []
        if self.config_imports:
            syms = ", ".join(sorted(self.config_imports))
            lines.append(f"from dj_design_system.config import {syms}")
        if self.types_imports:
            syms = ", ".join(sorted(self.types_imports))
            lines.append(f"from dj_design_system.types import {syms}")
        return "\n".join(lines)


def render_project_settings(
    *,
    config: DesignSystemSettings,
    include_defaults: bool = False,
    format_with_ruff: bool = True,
    ast_hints: Sequence[str] = (),
    excluded_apps: set[str] | None = None,
) -> str:
    """Render a standalone Python snippet defining ``DJ_DESIGN_SYSTEM = DesignSystemSettings(...)``."""
    emitter = _SettingsCodeEmitter(include_defaults=include_defaults)
    body = emitter.emit_design_system_settings(
        config=config,
        excluded_apps=excluded_apps,
    )
    imports = emitter.render_imports()
    notes = [*ast_hints, *emitter.manual_notes]
    header = "".join(f"# MANUAL: {note}\n" for note in notes)
    code = f"{header}{imports}\n\n{body}" if imports else f"{header}{body}"
    return format_python_code(code=code) if format_with_ruff else code


def render_app_settings_snippet(
    *,
    app_label: str,
    app_settings: AppSettings,
    classification: AppClassification | None = None,
    include_defaults: bool = False,
    format_with_ruff: bool = True,
) -> str:
    """Render an ``AppConfig`` subclass snippet with ``design_system = AppSettings(...)``."""
    emitter = _SettingsCodeEmitter(include_defaults=include_defaults)
    expr = emitter.emit_app_settings(app_settings)
    imports = emitter.render_imports()

    class_name = (
        classification.config_class_name
        if classification is not None
        else f"{app_label.title().replace('_', '')}Config"
    )
    app_name = classification.app_name if classification is not None else app_label
    default_label = app_name.rsplit(".", 1)[-1]

    notes: list[str] = []
    if classification is not None:
        if classification.uses_default_app_config and classification.has_apps_py:
            notes.append(
                f"Existing apps.py found for '{app_label}' (possibly default = False); merge manually rather than overwriting."
            )
        if classification.already_has_design_system:
            notes.append(
                f"AppConfig for '{app_label}' already defines design_system; merge manually."
            )
    notes.extend(emitter.manual_notes)

    header = "".join(f"# MANUAL: {note}\n" for note in notes)
    label_line = f"    label = {app_label!r}\n" if app_label != default_label else ""
    code = (
        f"{header}"
        f"from django.apps import AppConfig\n"
        f"{imports}\n\n\n"
        f"class {class_name}(AppConfig):\n"
        f"    name = {app_name!r}\n"
        f"{label_line}"
        f"    design_system = {expr}\n"
    )
    return format_python_code(code=code) if format_with_ruff else code
