import abc
from typing import Callable, Iterable, Optional

from dj_design_system.data import ComponentInfo


class AssessmentPlugin(abc.ABC):
    """Base interface for assessment plugins."""

    @abc.abstractmethod
    def run_assessment(self, component: ComponentInfo, variant: str, theme: str) -> None:
        """Run an assessment for a given component, variant, and theme."""
        pass


class IterationEngine:
    """Core generator that maps components, variants, and themes."""

    def __init__(
        self,
        components: Optional[list[ComponentInfo]] = None,
        themes: Optional[list[str]] = None,
        variants: Optional[list[str]] = None,
    ):
        self.components = components or []
        self.themes = themes or ["light", "dark"]
        self.variants = variants or ["basic", "maximal"]
        self._filters: list[Callable[[ComponentInfo, str, str], bool]] = []

    def add_filter(self, filter_func: Callable[[ComponentInfo, str, str], bool]) -> None:
        """Add a filter hook to customize the loop."""
        self._filters.append(filter_func)

    def get_combinations(self) -> Iterable[tuple[ComponentInfo, str, str]]:
        """Yield (component, variant, theme) combinations that pass filters."""
        for comp in self.components:
            for variant in self.variants:
                for theme in self.themes:
                    if self._passes_filters(comp, variant, theme):
                        yield (comp, variant, theme)

    def _passes_filters(self, comp: ComponentInfo, variant: str, theme: str) -> bool:
        for f in self._filters:
            if not f(comp, variant, theme):
                return False
        return True

    def run_plugins(self, plugins: list[AssessmentPlugin], fail_fast: bool = False) -> None:
        """Run all plugins on all valid combinations."""
        errors: list[str] = []
        for comp, variant, theme in self.get_combinations():
            for plugin in plugins:
                try:
                    plugin.run_assessment(comp, variant, theme)
                except Exception as e:
                    error_msg = f"[{comp.qualified_name} | {variant} | {theme} | {plugin.__class__.__name__}]: {e}"
                    if fail_fast:
                        raise AssertionError(f"Component assessment failed (fail_fast=True):\n\n{error_msg}") from e
                    errors.append(error_msg)

        if errors:
            raise AssertionError(
                "Component assessments failed:\n\n" + "\n\n".join(errors)
            )
