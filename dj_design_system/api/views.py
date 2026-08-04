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
from dj_design_system.exceptions import ComponentValidationError
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

    def get_serializer(self, *args, **kwargs):
        """Return the serializer instance."""
        return self.serializer_class(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        components = self.registry.list_all()
        serializer = self.get_serializer(components)
        return JsonResponse(serializer.data, safe=False)


@method_decorator(csrf_exempt, name="dispatch")
class ComponentRenderView(View):
    """View to render a specific component to HTML."""

    serializer_class = ComponentRenderRequestSerializer
    registry = component_registry

    def _get_payload(self, request) -> dict:
        if request.content_type != "application/json":
            raise ComponentValidationError("Content-Type must be 'application/json'.")

        if not request.body:
            raise ComponentValidationError("Request body is empty.")
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            raise ComponentValidationError("Request body is not valid JSON.")
        if not isinstance(payload, dict):
            raise ComponentValidationError(
                "JSON payload must be an object, not an array."
            )
        return payload

    def get_serializer(self, **kwargs) -> ComponentRenderRequestSerializer:
        """Return the serializer instance with the configured registry."""
        kwargs.setdefault("registry", self.registry)
        return self.serializer_class(**kwargs)

    def post(self, request, *args, **kwargs):
        try:
            payload = self._get_payload(request=request)
        except ComponentValidationError as exc:
            return JsonResponse({"error": exc.message}, status=400)

        serializer = self.get_serializer(data=payload)

        if not serializer.is_valid():
            error_message = serializer.errors.get("name", ["Unknown error"])[0]
            status_code = 404 if "not found" in error_message.lower() else 400
            return JsonResponse({"error": error_message}, status=status_code)

        spec = serializer.to_spec()

        try:
            rendered_html = render_component(
                spec=spec, registry=self.registry, raise_errors=True
            )
        except Exception as exc:  # Catch all rendering/template exceptions
            logger.exception("Failed to render component")
            return JsonResponse(
                {
                    "error": f"Failed to render component: {str(exc)}. Please check your parameters."
                },
                status=400,
            )

        media = get_component_media(spec=spec, registry=self.registry)

        try:
            canvas_path = reverse("gallery-canvas-iframe")
        except NoReverseMatch:
            canvas_path = "/_canvas/"

        canvas_url = build_canvas_url(
            spec, request.build_absolute_uri(canvas_path), registry=self.registry
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
