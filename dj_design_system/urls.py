from django.urls import path

from dj_design_system import views
from dj_design_system.api import views as api_views


urlpatterns = [
    path(
        "",
        views.gallery_index,
        name="gallery",
    ),
    path(
        "_canvas/",
        views.canvas_iframe_view,
        name="gallery-canvas-iframe",
    ),
    path(
        "api/registry/",
        api_views.ComponentRegistryView.as_view(),
        name="api-registry",
    ),
    path(
        "api/render/",
        api_views.ComponentRenderView.as_view(),
        name="api-render",
    ),
    # Catch-all: resolves to folder, component, or document
    # based on the node type found in the navigation tree.
    path(
        "<str:app_label>/<path:path>/",
        views.gallery_node,
        name="gallery-node",
    ),
    # App root (no path segments after the app label)
    path(
        "<str:app_label>/",
        views.gallery_node,
        name="gallery-node-root",
    ),
]
