"""Gallery configuration and variant definitions for components."""

from __future__ import annotations

import hashlib
import importlib.util
import sys
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping


@dataclass
class Variant:
    """A named component variation with preset arguments and preview configurations.

    Attributes:
        name: Unique identifier slug for this variant (e.g. ``"primary"``, ``"danger"``).
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
            When left as None, the owning ``GalleryConfig`` resolves it: False for the variants
            chosen as ``smaller_variant`` or ``bigger_variant`` so they do not clutter the sidebar
            tree, and True for every other variant. Explicitly set to True or False to override.
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

        self.positional_args = tuple(self.positional_args or ())
        self.kwargs = dict(self.kwargs or {})
        self.extra_context = dict(self.extra_context or {})

    @classmethod
    def from_dict(cls, data: Mapping[str, Any], name: str | None = None) -> Variant:
        """Create a Variant from a dictionary or mapping."""
        payload = dict(data)
        if name is not None and "name" not in payload:
            payload["name"] = name
        return cls(**payload)

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Variant):
            return NotImplemented
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
        variants: List of named Variant instances. To construct from dictionary mappings,
            use ``GalleryConfig.from_dict(...)``.
        smaller_variant: Name of the variant shown as the smaller (minimal) usage example.
            When None, the smaller example is generated from parameter defaults.
        bigger_variant: Name of the variant shown as the bigger (maximal) usage example.
            When None, the bigger example is generated from parameter defaults.
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
    smaller_variant: str | None = None
    bigger_variant: str | None = None

    @classmethod
    def _normalize_variants(
        cls, variants: list[Variant] | Mapping[str, Any] | list[dict[str, Any]]
    ) -> list[Variant]:
        """Normalize variant instances, dict mappings, or dict lists into a list of Variants."""
        if isinstance(variants, Mapping):
            return [
                v if isinstance(v, Variant) else Variant.from_dict(v, name=k)
                for k, v in variants.items()
            ]
        elif isinstance(variants, (list, tuple)):
            return [
                v if isinstance(v, Variant) else Variant.from_dict(v) for v in variants
            ]
        raise TypeError(
            f"variants must be a list, tuple, or mapping, got {type(variants).__name__}"
        )

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> GalleryConfig:
        """Create a GalleryConfig from a dictionary or mapping.

        Converts nested variant dictionaries or mappings into Variant instances.
        """
        payload = dict(data)
        if "variants" in payload:
            payload["variants"] = cls._normalize_variants(payload["variants"])
        return cls(**payload)

    def __post_init__(self) -> None:
        self.extra_context = dict(self.extra_context or {})
        self.param_defaults = dict(self.param_defaults or {})
        if not isinstance(self.variants, list):
            if isinstance(self.variants, (tuple, set)):
                self.variants = list(self.variants)
            else:
                raise TypeError(
                    f"GalleryConfig.variants must be a list of Variant instances, got {type(self.variants).__name__}. "
                    "Use GalleryConfig.from_dict(...) if initializing from a mapping or dictionary."
                )

        seen_names: set[str] = set()
        for v in self.variants:
            if not isinstance(v, Variant):
                raise TypeError(
                    f"GalleryConfig.variants must contain only Variant instances, got {type(v).__name__}. "
                    "Use GalleryConfig.from_dict(...) to parse dictionary configurations."
                )
            if v.name in seen_names:
                raise ValueError(
                    f"Duplicate variant name: '{v.name}' in GalleryConfig."
                )
            seen_names.add(v.name)

        for kwarg in ("smaller_variant", "bigger_variant"):
            name = getattr(self, kwarg)
            if name is not None and name not in seen_names:
                raise ValueError(
                    f"GalleryConfig.{kwarg} is '{name}', but no variant has that name."
                )

        example_names = {self.smaller_variant, self.bigger_variant}
        for v in self.variants:
            if v.show_in_nav is None:
                v.show_in_nav = v.name not in example_names

    def get_variant(self, name: str) -> Variant | None:
        """Return the variant matching *name*, or None."""
        for v in self.variants:
            if v.name == name:
                return v
        return None

    def get_smaller_variant(self) -> Variant | None:
        """Return the variant shown as the smaller usage example, or None."""
        return self.get_variant(self.smaller_variant) if self.smaller_variant else None

    def get_bigger_variant(self) -> Variant | None:
        """Return the variant shown as the bigger usage example, or None."""
        return self.get_variant(self.bigger_variant) if self.bigger_variant else None


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

    resolved_path = gallery_path.resolve()
    path_hash = hashlib.sha256(str(resolved_path).encode("utf-8")).hexdigest()[:16]
    mod_name = f"dj_design_system_gallery_{component_name}_{path_hash}"
    spec = importlib.util.spec_from_file_location(mod_name, resolved_path)
    if not (spec and spec.loader):
        return GalleryConfig()

    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    source = resolved_path.read_text(encoding="utf-8")
    exec(compile(source, str(resolved_path), "exec"), mod.__dict__)

    cfg = getattr(mod, "config", None)
    if isinstance(cfg, GalleryConfig):
        return cfg
    if isinstance(cfg, Mapping):
        return GalleryConfig.from_dict(cfg)

    named_cfg = getattr(mod, f"{component_name}_config", None)
    if isinstance(named_cfg, GalleryConfig):
        return named_cfg
    if isinstance(named_cfg, Mapping):
        return GalleryConfig.from_dict(named_cfg)

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
        return GalleryConfig(
            variants=variants,
            smaller_variant="basic" if basic_kwargs is not None else None,
            bigger_variant="maximal" if maximal_kwargs is not None else None,
        )

    return GalleryConfig()
