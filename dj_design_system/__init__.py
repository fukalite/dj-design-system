"""Public package exports for dj-design-system (loaded lazily via PEP 562)."""

from __future__ import annotations

from importlib import import_module
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from dj_design_system.components import (
        BaseComponent,
        BlockComponent,
        TagComponent,
    )
    from dj_design_system.data import GalleryParameter
    from dj_design_system.exceptions import DJDesignSystemError
    from dj_design_system.gallery import GalleryConfig, Variant
    from dj_design_system.services.registry import (
        ComponentRegistry,
        component_registry,
    )
    from dj_design_system.slots import Slot


_LAZY_EXPORTS: dict[str, tuple[str, str]] = {
    "BaseComponent": ("dj_design_system.components", "BaseComponent"),
    "BlockComponent": ("dj_design_system.components", "BlockComponent"),
    "ComponentRegistry": ("dj_design_system.services.registry", "ComponentRegistry"),
    "DJDesignSystemError": ("dj_design_system.exceptions", "DJDesignSystemError"),
    "GalleryConfig": ("dj_design_system.gallery", "GalleryConfig"),
    "GalleryParameter": ("dj_design_system.data", "GalleryParameter"),
    "Slot": ("dj_design_system.slots", "Slot"),
    "TagComponent": ("dj_design_system.components", "TagComponent"),
    "Variant": ("dj_design_system.gallery", "Variant"),
    "component_registry": ("dj_design_system.services.registry", "component_registry"),
}

__all__ = [
    "BaseComponent",
    "BlockComponent",
    "ComponentRegistry",
    "DJDesignSystemError",
    "GalleryConfig",
    "GalleryParameter",
    "Slot",
    "TagComponent",
    "Variant",
    "component_registry",
]


def __getattr__(name: str) -> Any:
    target = _LAZY_EXPORTS.get(name)
    if target is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_path, attr_name = target
    value = getattr(import_module(module_path), attr_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted({*globals(), *__all__})
