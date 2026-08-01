import json
import logging

logger = logging.getLogger(__name__)

from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from dj_design_system.api.serializers import (
    ComponentListSerializer, 
    ComponentNotFoundError,
    ComponentRenderRequestSerializer,
    ComponentValidationError,
)
from dj_design_system.data import CanvasSpec
from dj_design_system.services.canvas import _resolve_component, render_component, get_component_media, build_canvas_url
from dj_design_system.services.registry import component_registry
from dj_design_system.services.media import get_bundle_urls
from dj_design_system.settings import dds_settings
from django.templatetags.static import static
from django.urls import reverse


class ComponentRegistryView(View):
    """View to list all registered components."""

    serializer_class = ComponentListSerializer

    def get(self, request, *args, **kwargs):
        components = component_registry.list_all()
        serializer = self.serializer_class(components)
        return JsonResponse(serializer.data(), safe=False)


@method_decorator(csrf_exempt, name="dispatch")
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

        media = get_component_media(spec=spec, registry=component_registry)
        
        try:
            canvas_path = reverse("gallery-canvas-iframe")
        except Exception:
            canvas_path = "/_canvas/"
            
        canvas_url = build_canvas_url(
            spec, 
            request.build_absolute_uri(canvas_path), 
            registry=component_registry
        )
        
        global_css = get_bundle_urls(dds_settings.GLOBAL_CSS_BUNDLES, "css") + [
            static(path) for path in dds_settings.GLOBAL_CSS
        ]
        global_js = get_bundle_urls(dds_settings.GLOBAL_JS_BUNDLES, "js") + [
            static(path) for path in dds_settings.GLOBAL_JS
        ]

        return JsonResponse({
            "html": rendered_html,
            "css": media.css,
            "js": media.js,
            "global_css": global_css,
            "global_js": global_js,
            "canvas_url": canvas_url,
        })
