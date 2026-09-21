from django.urls import path

from dj_design_system.api import views


urlpatterns = [
    path("registry/", views.ComponentRegistryView.as_view(), name="api-registry"),
    path("render/", views.ComponentRenderView.as_view(), name="api-render"),
]
