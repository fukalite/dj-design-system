"""Gallery configuration and variant definitions for components."""

from __future__ import annotations

import hashlib
import importlib.util
import sys
import warnings
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from dj_design_system.types import DocVariantConfig


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
            When left as None, defaults to False for standard global documentation variants
            (e.g. ``"basic"``, ``"maximal"``, ``"defaults"``, ``"all_slots"``) so they do not
            clutter the sidebar tree, and True for custom named variants.
            Explicitly set to True or False to override this default.
        show_in_docs: Whether to render this variant as an example in the component documentation pane.
            When left as None, defaults to True for enabled documentation variants
            (e.g. ``"basic"``, ``"maximal"``) and False for other variants.
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
    show_in_docs: bool | None = None
    _explicit_label: str | None = field(
        default=None, init=False, repr=False, compare=False
    )
    _explicit_show_in_docs: bool | None = field(
        default=None, init=False, repr=False, compare=False
    )
    _explicit_show_in_nav: bool | None = field(
        default=None, init=False, repr=False, compare=False
    )

    def __post_init__(self) -> None:
        from dj_design_system.settings import get_doc_variants

        self._explicit_label = self.label
        if self.label is None:
            self.label = self.name.replace("_", " ").replace("-", " ").title()

        self._explicit_show_in_docs = self.show_in_docs
        self._explicit_show_in_nav = self.show_in_nav

        doc_variants = get_doc_variants()
        self.show_in_docs = self.is_shown_in_docs(doc_variants=doc_variants)
        self.show_in_nav = self.is_shown_in_nav(doc_variants=doc_variants)

        self.positional_args = tuple(self.positional_args or ())
        self.kwargs = dict(self.kwargs or {})
        self.extra_context = dict(self.extra_context or {})

    def is_shown_in_docs(
        self,
        *,
        doc_variants: Sequence[DocVariantConfig] | None = None,
    ) -> bool:
        """Return whether this variant should be rendered in component documentation."""
        if self._explicit_show_in_docs is not None:
            return self._explicit_show_in_docs
        from dj_design_system.settings import get_doc_variants

        resolved_doc_variants = (
            doc_variants if doc_variants is not None else get_doc_variants()
        )
        enabled_doc_names = {dv.name for dv in resolved_doc_variants if dv.show_in_docs}
        return self.name in enabled_doc_names

    def is_shown_in_nav(
        self,
        *,
        doc_variants: Sequence[DocVariantConfig] | None = None,
    ) -> bool:
        """Return whether this variant should be rendered in sidebar navigation."""
        if self._explicit_show_in_nav is not None:
            return self._explicit_show_in_nav
        from dj_design_system.settings import get_doc_variants
        from dj_design_system.types import DocVariantStrategy

        resolved_doc_variants = (
            doc_variants if doc_variants is not None else get_doc_variants()
        )
        standard_doc_names = {
            dv.name
            for dv in resolved_doc_variants
            if dv.strategy != DocVariantStrategy.CUSTOM
        } | {dv.name for dv in get_doc_variants()}
        return self.name not in standard_doc_names

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
            and self.show_in_docs == other.show_in_docs
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
        doc_variants: Optional component-level documentation variant overrides (mapping or sequence)
            layered on top of the global ``GALLERY_DOC_VARIANTS`` setting.
        variants: List of named Variant instances. To construct from dictionary mappings,
            use ``GalleryConfig.from_dict(...)``.
    """

    hidden: bool = False
    icon: str | None = None
    theme: str | None = None
    group: str | None = None
    order: int = 0
    canvas_template: str | None = None
    extra_context: dict[str, Any] = field(default_factory=dict)
    param_defaults: dict[str, Any] = field(default_factory=dict)
    doc_variants: Mapping[str, Any] | Sequence[Any] | None = None
    variants: list[Variant] = field(default_factory=list)

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

        if self.doc_variants is not None:
            comp_doc_variants = self.get_doc_variants()
            for v in self.variants:
                v.show_in_docs = v.is_shown_in_docs(doc_variants=comp_doc_variants)
                v.show_in_nav = v.is_shown_in_nav(doc_variants=comp_doc_variants)

    def get_doc_variants(self) -> list[DocVariantConfig]:
        """Return resolved documentation variant configurations for this component."""
        from dj_design_system.settings import get_doc_variants, resolve_doc_variants

        global_variants = get_doc_variants()
        if self.doc_variants is None:
            return global_variants
        return resolve_doc_variants(
            raw_setting=self.doc_variants,
            base_variants=global_variants,
        )

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
        return GalleryConfig(variants=variants)

    return GalleryConfig()
