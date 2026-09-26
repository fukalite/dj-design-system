"""Gallery configuration and variant definitions for components."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Sequence


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

        if isinstance(self.positional_args, (list, tuple)):
            self.positional_args = tuple(self.positional_args)

        if not isinstance(self.kwargs, dict):
            self.kwargs = dict(self.kwargs)

        if not isinstance(self.extra_context, dict):
            self.extra_context = dict(self.extra_context)


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
        if not isinstance(self.hidden, bool):
            raise TypeError(
                f"hidden must be a boolean, got {type(self.hidden).__name__}"
            )

        if not isinstance(self.order, int):
            raise TypeError(
                f"order must be an integer, got {type(self.order).__name__}"
            )

        if not isinstance(self.extra_context, dict):
            self.extra_context = dict(self.extra_context)

        if not isinstance(self.param_defaults, dict):
            self.param_defaults = dict(self.param_defaults)

        coerced_variants: list[Variant] = []
        if isinstance(self.variants, Mapping):
            for var_name, var_data in self.variants.items():
                if isinstance(var_data, Variant):
                    coerced_variants.append(var_data)
                elif isinstance(var_data, dict):
                    data = dict(var_data)
                    data.setdefault("name", var_name)
                    coerced_variants.append(Variant(**data))
                else:
                    raise TypeError(
                        f"Invalid variant definition for '{var_name}': {var_data!r}"
                    )
        elif isinstance(self.variants, (Sequence, Iterable)):
            for item in self.variants:
                if isinstance(item, Variant):
                    coerced_variants.append(item)
                elif isinstance(item, dict):
                    coerced_variants.append(Variant(**item))
                else:
                    raise TypeError(f"Invalid variant item: {item!r}")
        else:
            raise TypeError(
                f"variants must be a list or dict, got {type(self.variants).__name__}"
            )

        seen_names: set[str] = set()
        for v in coerced_variants:
            if v.name in seen_names:
                raise ValueError(
                    f"Duplicate variant name: '{v.name}' in GalleryConfig."
                )
            seen_names.add(v.name)

        self.variants = coerced_variants

    def get_variant(self, name: str) -> Variant | None:
        """Return the variant matching *name*, or None."""
        for v in self.variants:
            if v.name == name:
                return v
        return None
