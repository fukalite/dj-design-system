import abc
from typing import Callable, Iterable, Optional

from dj_design_system.data import ComponentInfo
from dj_design_system.gallery import GalleryConfig
from dj_design_system.settings import get_doc_variants


class AssessmentPlugin(abc.ABC):
    """Base interface for assessment plugins."""

    @abc.abstractmethod
    def run_assessment(
        self, component: ComponentInfo, variant: str, theme: str
    ) -> None:
        """Run an assessment for a given component, variant, and theme."""
        pass


class IterationEngine:
    """Core generator that maps components, variants, and themes."""

    def __init__(
        self,
        components: Optional[list[ComponentInfo]] = None,
        themes: Optional[list[str]] = None,
        variants: Optional[list[str]] = None,
    ) -> None:
        self.components = components or []
        self.themes = themes or ["light", "dark"]
        self._explicit_variants = variants is not None
        self.variants = (
            variants
            if variants is not None
            else [dv.name for dv in get_doc_variants() if dv.show_in_docs]
        )
        self._filters: list[Callable[[ComponentInfo, str, str], bool]] = []

    def add_filter(
        self, filter_func: Callable[[ComponentInfo, str, str], bool]
    ) -> None:
        """Add a filter hook to customize the loop."""
        self._filters.append(filter_func)

    def _get_component_variants(self, comp: ComponentInfo) -> list[str]:
        """Return the ordered, deduplicated variant names to assess for *comp*."""
        if self._explicit_variants:
            return list(self.variants)

        cfg = getattr(comp, "gallery_config", None)
        if isinstance(cfg, GalleryConfig):
            comp_doc_variants = cfg.get_doc_variants()
            comp_variants = [dv.name for dv in comp_doc_variants if dv.show_in_docs]
        else:
            comp_doc_variants = get_doc_variants()
            comp_variants = list(self.variants)

        cfg_variants = getattr(cfg, "variants", None) if cfg is not None else None
        if isinstance(cfg_variants, (list, tuple)):
            for variant_obj in cfg_variants:
                variant_name = getattr(variant_obj, "name", None)
                if not isinstance(variant_name, str) or not variant_name:
                    continue
                if hasattr(variant_obj, "is_shown_in_docs") and hasattr(
                    variant_obj, "is_shown_in_nav"
                ):
                    is_suppressed = not variant_obj.is_shown_in_docs(
                        doc_variants=comp_doc_variants
                    ) and not variant_obj.is_shown_in_nav(
                        doc_variants=comp_doc_variants
                    )
                else:
                    is_suppressed = (
                        getattr(variant_obj, "show_in_docs", True) is False
                        and getattr(variant_obj, "show_in_nav", True) is False
                    )
                if is_suppressed:
                    if variant_name in comp_variants:
                        comp_variants.remove(variant_name)
                    continue
                if variant_name not in comp_variants:
                    comp_variants.append(variant_name)
        return comp_variants

    def get_combinations(self) -> Iterable[tuple[ComponentInfo, str, str]]:
        """Yield (component, variant, theme) combinations that pass filters."""
        for comp in self.components:
            for variant in self._get_component_variants(comp):
                for theme in self.themes:
                    if self._passes_filters(comp, variant, theme):
                        yield (comp, variant, theme)

    def _passes_filters(self, comp: ComponentInfo, variant: str, theme: str) -> bool:
        for f in self._filters:
            if not f(comp, variant, theme):
                return False
        return True

    def run_plugins(
        self, plugins: list[AssessmentPlugin], fail_fast: bool = False
    ) -> None:
        """Run all plugins on all valid combinations."""
        errors: list[str] = []
        for comp, variant, theme in self.get_combinations():
            for plugin in plugins:
                try:
                    plugin.run_assessment(comp, variant, theme)
                except Exception as e:
                    error_msg = f"[{comp.qualified_name} | {variant} | {theme} | {plugin.__class__.__name__}]: {e}"
                    if fail_fast:
                        raise AssertionError(
                            f"Component assessment failed (fail_fast=True):\n\n{error_msg}"
                        ) from e
                    errors.append(error_msg)

        if errors:
            raise AssertionError(
                "Component assessments failed:\n\n" + "\n\n".join(errors)
            )
