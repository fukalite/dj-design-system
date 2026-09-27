"""Gallery configuration and variant definitions for components."""

from __future__ import annotations

import importlib.util
import uuid
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping


@dataclass
class Variant:
    """A named component variation with preset arguments and preview configurations.

    Attributes:
        name: Unique identifier slug for this variant (e.g. ``"basic"``, ``"danger"``).
        label: Human-readable display label in documentation and sidebar navigation.
            Defaults to title-cased name.
        description: Optional markdown text describing when/how to use this variant.
        kwargs: Component keyword parameters passed to instantiation. Supports raw values,
            ``GalleryParameter`` instances, or dynamic callables.
        positional_args: Positional argument values passed to the component tag.
        canvas_template: Optional variant-level HTML layout override for previewing this variant.
        extra_context: Additional template context variables available during preview rendering.
        icon: Optional icon name or SVG path for sidebar navigation.
        theme: Optional theme override when previewing this variant.
        show_in_nav: Whether to display this variant as a child node in the gallery sidebar navigation.
            Defaults to False for default variants ("basic", "maximal") and True for custom variants.
    """

    name: str
    label: str | None = None
    description: str | None = None
    kwargs: dict[str, Any] = field(default_factory=dict)
    positional_args: tuple[Any, ...] = field(default_factory=tuple)
    canvas_template: str | None = None
    extra_context: dict[str, Any] = field(default_factory=dict)
    icon: str | None = None
    theme: str | None = None
    show_in_nav: bool | None = None

    def __post_init__(self) -> None:
        if self.label is None:
            self.label = self.name.replace("_", " ").replace("-", " ").title()

        if self.show_in_nav is None:
            self.show_in_nav = False if self.name in ("basic", "maximal") else True

        self.positional_args = tuple(self.positional_args or ())
        self.kwargs = dict(self.kwargs or {})
        self.extra_context = dict(self.extra_context or {})

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return self.name == other
        if isinstance(other, Variant):
            return (
                self.name == other.name
                and self.label == other.label
                and self.description == other.description
                and self.kwargs == other.kwargs
                and self.positional_args == other.positional_args
                and self.canvas_template == other.canvas_template
                and self.extra_context == other.extra_context
                and self.icon == other.icon
                and self.theme == other.theme
                and self.show_in_nav == other.show_in_nav
            )
        return False


@dataclass
class GalleryConfig:
    """Explicit configuration for a component within the design system gallery.

    Attributes:
        hidden: If True, hides the component and its variants from gallery navigation and search.
        icon: Custom icon name (e.g. ``"mdi:button"``) for the component in sidebar navigation.
        theme: Theme override for the component preview.
        group: Grouping category for sidebar navigation.
        order: Ordering priority integer for sidebar navigation. Lower numbers appear first.
        canvas_template: HTML template string for wrapping previews. Operates in Smart Hybrid mode:
            if ``{{ component }}`` is present, wraps the rendered component; otherwise renders as
            raw template syntax.
        extra_context: Context variables passed to preview templates.
        param_defaults: Mapping of param names to default values or callables.
        variants: List of named variants. Supports initialization from ``Variant`` instances,
            lists of dicts, or dictionary mappings.
    """

    hidden: bool = False
    icon: str | None = None
    theme: str | None = None
    group: str | None = None
    order: int = 0
    canvas_template: str | None = None
    extra_context: dict[str, Any] = field(default_factory=dict)
    param_defaults: dict[str, Any] = field(default_factory=dict)
    variants: list[Variant] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.extra_context = dict(self.extra_context or {})
        self.param_defaults = dict(self.param_defaults or {})

        if isinstance(self.variants, Mapping):
            raw = [
                v if isinstance(v, Variant) else Variant(name=k, **v)
                for k, v in self.variants.items()
            ]
        else:
            raw = [
                v if isinstance(v, Variant) else Variant(**v)
                for v in (self.variants or [])
            ]

        seen_names: set[str] = set()
        for v in raw:
            if v.name in seen_names:
                raise ValueError(
                    f"Duplicate variant name: '{v.name}' in GalleryConfig."
                )
            seen_names.add(v.name)

        self.variants = raw

    def get_variant(self, name: str) -> Variant | None:
        """Return the variant matching *name*, or None."""
        for v in self.variants:
            if v.name == name:
                return v
        return None


def load_gallery_config(source_dir: Path, component_name: str) -> GalleryConfig:
    """Discover, import, and return the GalleryConfig for a component.

    Checks for ``{name}_gallery.py``, ``{name}.gallery.py``, or ``gallery.py``
    within *source_dir*. If found, imports the module safely and extracts
    the ``config`` (or ``{name}_config``) object. If legacy ``basic_kwargs``
    or ``maximal_kwargs`` are present without a config, emits a
    ``DeprecationWarning`` and synthesizes a fallback config.
    """
    candidates = [
        source_dir / f"{component_name}_gallery.py",
        source_dir / f"{component_name}.gallery.py",
        source_dir / "gallery.py",
    ]

    gallery_path = None
    for p in candidates:
        if p.is_file():
            gallery_path = p
            break

    if not gallery_path:
        return GalleryConfig()

    mod_name = f"dj_design_system_gallery_{uuid.uuid4().hex}"
    spec = importlib.util.spec_from_file_location(mod_name, gallery_path)
    if not (spec and spec.loader):
        return GalleryConfig()

    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    cfg = getattr(mod, "config", None)
    if isinstance(cfg, GalleryConfig):
        return cfg

    named_cfg = getattr(mod, f"{component_name}_config", None)
    if isinstance(named_cfg, GalleryConfig):
        return named_cfg

    # Legacy fallback for basic_kwargs / maximal_kwargs
    basic_kwargs = getattr(mod, "basic_kwargs", None)
    maximal_kwargs = getattr(mod, "maximal_kwargs", None)
    if basic_kwargs is not None or maximal_kwargs is not None:
        warnings.warn(
            f"Component '{component_name}' defines legacy 'basic_kwargs' or 'maximal_kwargs' "
            f"in '{gallery_path.name}'. Defining kwargs directly in gallery files is deprecated "
            "and will be removed in a future release. Export 'config = GalleryConfig(...)' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        variants: list[Variant] = []
        if basic_kwargs is not None:
            variants.append(Variant(name="basic", kwargs=basic_kwargs))
        if maximal_kwargs is not None:
            variants.append(Variant(name="maximal", kwargs=maximal_kwargs))
        return GalleryConfig(variants=variants)

    return GalleryConfig()
