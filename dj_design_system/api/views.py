import json
import logging

from django.http import JsonResponse
from django.templatetags.static import static
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from dj_design_system.api.serializers import (
    ComponentListSerializer,
    ComponentRenderRequestSerializer,
)
from dj_design_system.exceptions import ComponentNotFoundError, ComponentValidationError
from dj_design_system.services.canvas import (
    build_canvas_url,
    get_component_media,
    render_component,
)
from dj_design_system.services.media import get_bundle_urls
from dj_design_system.services.registry import component_registry
from dj_design_system.settings import dds_settings


logger = logging.getLogger(__name__)


class ComponentRegistryView(View):
    """View to list all registered components."""

    serializer_class = ComponentListSerializer
    registry = component_registry

    def get(self, request, *args, **kwargs):
        components = self.registry.list_all()
        serializer = self.serializer_class(components)
        return JsonResponse(serializer.data(), safe=False)


@method_decorator(csrf_exempt, name="dispatch")
class ComponentRenderView(View):
    """View to render a specific component to HTML."""

    def _get_payload(self, request) -> tuple[dict | None, str | None]:
        if not request.body:
            return None, "Request body is empty."
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            return None, "Request body is not valid JSON."
        if not isinstance(payload, dict):
            return None, "JSON payload must be an object, not an array."
        return payload, None

    def post(self, request, *args, **kwargs):
        payload, error_msg = self._get_payload(request=request)
        if not payload:
            return JsonResponse({"error": error_msg}, status=400)

        serializer = ComponentRenderRequestSerializer(
            data=payload, registry=component_registry
        )

        try:
            serializer.validate()
        except ComponentValidationError as exc:
            return JsonResponse({"error": exc.message}, status=400)
        except ComponentNotFoundError as exc:
            return JsonResponse({"error": exc.message}, status=404)

        spec = serializer.to_spec()

        try:
            rendered_html = render_component(
                spec=spec, registry=component_registry, raise_errors=True
            )
        except (ValueError, TypeError, KeyError):
            logger.exception("Failed to render component")
            return JsonResponse(
                {"error": "Failed to render component. Please check your parameters."},
                status=400,
            )

        media = get_component_media(spec=spec, registry=component_registry)

        try:
            canvas_path = reverse("gallery-canvas-iframe")
        except NoReverseMatch:
            canvas_path = "/_canvas/"

        canvas_url = build_canvas_url(
            spec, request.build_absolute_uri(canvas_path), registry=component_registry
        )

        global_css = get_bundle_urls(dds_settings.GLOBAL_CSS_BUNDLES, "css") + [
            static(path) for path in dds_settings.GLOBAL_CSS
        ]
        global_js = get_bundle_urls(dds_settings.GLOBAL_JS_BUNDLES, "js") + [
            static(path) for path in dds_settings.GLOBAL_JS
        ]

        return JsonResponse(
            {
                "html": rendered_html,
                "css": media.css,
                "js": media.js,
                "global_css": global_css,
                "global_js": global_js,
                "canvas_url": canvas_url,
            }
        )
