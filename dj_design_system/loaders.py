from django.apps import apps
from django.template import Origin, TemplateDoesNotExist
from django.template.loaders.base import Loader

from dj_design_system.services import component_dirs as component_dirs_service


class ComponentsTemplateLoader(Loader):
    """
    A template loader that serves ``.html`` files from each installed app's
    ``components/`` directory.

    Template names must follow the convention
    ``{app_label}/components/{sub_path}``, for example::

        demo_components/components/button/button.html
        demo_components/components/card.html

    Only ``.html`` files are served — Python, CSS, JS and other file types
    are never exposed through this loader.

    To enable, switch from ``APP_DIRS: True`` to an explicit ``loaders``
    list in your ``TEMPLATES`` setting and add this loader::

        TEMPLATES = [
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [],
                "APP_DIRS": False,
                "OPTIONS": {
                    "loaders": [
                        (
                            "django.template.loaders.cached.Loader",
                            [
                                "django.template.loaders.filesystem.Loader",
                                "django.template.loaders.app_directories.Loader",
                                "dj_design_system.loaders.ComponentsTemplateLoader",
                            ],
                        ),
                    ],
                    "context_processors": [...],
                },
            },
        ]
    """

    def get_dirs(self) -> list[str]:
        """Return installed apps' ``components/`` directories for template autoreload.

        Returns:
            A list of existing ``<app>/components`` directory paths so Django's
            development server watches component templates and resets
            ``cached.Loader`` when they change.
        """
        return [
            str(components_dir)
            for components_dir in component_dirs_service.get_components_dirs().values()
        ]

    def get_template_sources(self, template_name: str):
        """
        Yield ``Origin`` objects for *template_name* if it matches our
        ``{app_label}/components/{sub_path}`` convention and the file exists.
        """
        parts = template_name.split("/", 2)
        if len(parts) < 3 or parts[1] != "components":
            return

        app_label, _, sub_path = parts[0], parts[1], parts[2]

        if not sub_path.endswith(".html"):
            return

        try:
            app_config = apps.get_app_config(app_label)
        except LookupError:
            return

        components_dir = component_dirs_service.get_components_dir(
            app_config=app_config
        )
        if components_dir is None:
            return

        yield Origin(
            name=str(components_dir / sub_path),
            template_name=template_name,
            loader=self,
        )

    def get_contents(self, origin: Origin) -> str:
        """Return the source of the template at *origin*, or raise ``TemplateDoesNotExist``."""
        try:
            with open(origin.name, encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            raise TemplateDoesNotExist(origin)
