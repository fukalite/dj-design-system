import json
import logging

logger = logging.getLogger(__name__)

from django.http import JsonResponse
from django.views import View

from dj_design_system.api.serializers import (
    ComponentListSerializer, 
    ComponentNotFoundError,
    ComponentRenderRequestSerializer,
    ComponentValidationError,
)
from dj_design_system.data import CanvasSpec
from dj_design_system.services.canvas import _resolve_component, render_component
from dj_design_system.services.registry import component_registry


class ComponentRegistryView(View):
    """View to list all registered components."""

    serializer_class = ComponentListSerializer

    def get(self, request, *args, **kwargs):
        components = component_registry.list_all()
        serializer = self.serializer_class(components)
        return JsonResponse(serializer.data(), safe=False)


class ComponentRenderView(View):
    """View to render a specific component to HTML."""

    def _get_payload(self, request) -> dict | None:
        if not request.body:
            return None
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError as exc:
            logger.error(f"Invalid JSON payload received in ComponentRenderView: {exc}")
            return None
        if not isinstance(payload, dict):
            return None
        return payload

    def post(self, request, *args, **kwargs):
        payload = self._get_payload(request=request)
        if not payload:
            return JsonResponse({"error": "Invalid JSON payload."}, status=400)

        serializer = ComponentRenderRequestSerializer(data=payload, registry=component_registry)
        
        try:
            serializer.validate()
        except ComponentValidationError as exc:
            return JsonResponse({"error": str(exc)}, status=400)
        except ComponentNotFoundError as exc:
            return JsonResponse({"error": str(exc)}, status=404)

        spec = serializer.to_spec()

        try:
            rendered_html = render_component(
                spec=spec, registry=component_registry, raise_errors=True
            )
        except (ValueError, TypeError, KeyError) as exc:
            return JsonResponse(
                {"error": f"Failed to render component: {exc}"}, status=400
            )

        return JsonResponse({"html": rendered_html})
