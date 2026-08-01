class AssessmentPlugin:
    """Base interface for assessment plugins."""
    
    def run_assessment(self, component, variant, theme):
        """Run an assessment for a given component, variant, and theme."""
        raise NotImplementedError


class IterationEngine:
    """Core generator that maps components, variants, and themes."""
    
    def __init__(self, components=None, themes=None, variants=None):
        self.components = components or []
        self.themes = themes or ["light", "dark"]
        self.variants = variants or ["basic", "maximal"]
        self._filters = []
        
    def add_filter(self, filter_func):
        """Add a filter hook to customize the loop."""
        self._filters.append(filter_func)
        
    def get_combinations(self):
        """Yield (component, variant, theme) combinations that pass filters."""
        for comp in self.components:
            for variant in self.variants:
                for theme in self.themes:
                    if self._passes_filters(comp, variant, theme):
                        yield (comp, variant, theme)
                        
    def _passes_filters(self, comp, variant, theme):
        for f in self._filters:
            if not f(comp, variant, theme):
                return False
        return True
        
    def run_plugins(self, plugins):
        """Run all plugins on all valid combinations."""
        for comp, variant, theme in self.get_combinations():
            for plugin in plugins:
                plugin.run_assessment(comp, variant, theme)
