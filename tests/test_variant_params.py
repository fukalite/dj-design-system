"""Tests for merge_variant_params helper."""

from dj_design_system.components import BaseComponent
from dj_design_system.gallery import GalleryConfig, Variant
from dj_design_system.services.canvas import merge_variant_params


class DummyComponent(BaseComponent):
    class Meta:
        positional_args = ["title", "count"]


def test_merge_variant_params_defaults_only():
    """Returns param_defaults when no variant or overrides are provided."""
    config = GalleryConfig(param_defaults={"title": "Default Title", "size": "md"})
    merged = merge_variant_params(DummyComponent, config=config)
    assert merged == {"title": "Default Title", "size": "md"}


def test_merge_variant_params_with_variant_kwargs():
    """Variant kwargs override param_defaults."""
    config = GalleryConfig(param_defaults={"title": "Default", "size": "md"})
    variant = Variant(name="custom", kwargs={"size": "lg", "theme": "dark"})
    merged = merge_variant_params(DummyComponent, config=config, variant=variant)
    assert merged == {"title": "Default", "size": "lg", "theme": "dark"}


def test_merge_variant_params_with_variant_positional_args():
    """Variant positional args are mapped to positional_args parameter names."""
    config = GalleryConfig(param_defaults={"title": "Default", "count": 1})
    variant = Variant(name="pos", positional_args=("New Title", 42))
    merged = merge_variant_params(DummyComponent, config=config, variant=variant)
    assert merged == {"title": "New Title", "count": 42}


def test_merge_variant_params_with_overrides():
    """Explicit overrides take highest precedence over variant and defaults."""
    config = GalleryConfig(param_defaults={"title": "Default", "count": 1})
    variant = Variant(name="custom", kwargs={"title": "Variant Title", "count": 5})
    merged = merge_variant_params(
        DummyComponent,
        config=config,
        variant=variant,
        overrides={"count": 10, "extra": "yes"},
    )
    assert merged == {"title": "Variant Title", "count": 10, "extra": "yes"}


def test_merge_variant_params_positional_args_override():
    """Explicit positional_args override variant positional args."""
    config = GalleryConfig()
    variant = Variant(name="pos", positional_args=("Variant Title", 5))
    merged = merge_variant_params(
        DummyComponent,
        config=config,
        variant=variant,
        positional_args=("Override Title",),
    )
    assert merged == {"title": "Override Title", "count": 5}


def test_merge_variant_params_resolve_callables():
    """When resolve_values=True, callable parameter defaults and values are evaluated."""
    config = GalleryConfig(param_defaults={"title": lambda: "Computed Title"})
    variant = Variant(name="dyn", kwargs={"count": lambda: 99})
    merged = merge_variant_params(
        DummyComponent,
        config=config,
        variant=variant,
        resolve_values=True,
    )
    assert merged == {"title": "Computed Title", "count": 99}
