# REST API

Django Design System provides a headless REST API that exposes the component registry and renders components to HTML. This is particularly useful for building integrations with external tools, such as the [Figma plugin](https://github.com/fukalite/figma-dj-design-system).

## Installation

To enable the REST API, you need to include its URL configuration in your project's `urls.py`:

```python
from django.urls import include, path

urlpatterns = [
    # Optional: Include the REST API endpoints
    path("api/", include("dj_design_system.api.urls")),
    
    # ... your other routes
]
```

This will mount the following endpoints:

- `GET /api/registry/`: Lists all registered components and their schemas.
- `POST /api/render/`: Renders a specific component and returns its HTML, CSS, JS, and canvas URL.

## Authentication and Security

By default, the `api/render/` endpoint is decorated with `csrf_exempt` to allow cross-origin POST requests from tools like Figma.

However, neither endpoint enforces authentication out of the box. If you want to secure these endpoints (e.g., behind a token authentication scheme), you should subclass the views and add your own decorators or permission classes.

### Securing the Endpoints

To add authentication, create your own URL routing that points to customized subclasses of the API views:

```python
# my_project/api/views.py
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from dj_design_system.api.views import ComponentRegistryView, ComponentRenderView

@method_decorator(login_required, name="dispatch")
class SecureComponentRegistryView(ComponentRegistryView):
    pass

@method_decorator(login_required, name="dispatch")
class SecureComponentRenderView(ComponentRenderView):
    pass
```

Then, map these custom views in your `urls.py` instead of including `dj_design_system.api.urls`:

```python
# my_project/urls.py
from django.urls import path
from my_project.api.views import SecureComponentRegistryView, SecureComponentRenderView

urlpatterns = [
    path("api/registry/", SecureComponentRegistryView.as_view(), name="api-registry"),
    path("api/render/", SecureComponentRenderView.as_view(), name="api-render"),
]
```

## Overriding Serializers

The API views are built using standard Django `View` classes. If you need to change the shape of the JSON payload (for example, to include additional project-specific metadata), you can override the `serializer_class` attribute.

```python
from dj_design_system.api.views import ComponentRegistryView
from my_project.serializers import CustomRegistrySerializer

class CustomComponentRegistryView(ComponentRegistryView):
    serializer_class = CustomRegistrySerializer
```
