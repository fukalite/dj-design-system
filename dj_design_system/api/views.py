from django.http import JsonResponse
from django.views import View

from dj_design_system.api.serializers import ComponentSerializer
from dj_design_system.services.registry import component_registry


class ComponentRegistryView(View):
    """View to list all registered components."""
    
    serializer_class = ComponentSerializer

    def get(self, request, *args, **kwargs):
        components = component_registry.list_all()
        serializer = self.serializer_class(components)
        return JsonResponse(serializer.data(), safe=False)
