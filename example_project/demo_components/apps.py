from django.apps import AppConfig

from dj_design_system.config import AppSettings


class DemoComponentsConfig(AppConfig):
    name = "example_project.demo_components"
    verbose_name = "Demo Components"
    design_system = AppSettings(
        css=("example_project/app-demo.css",),
        canvas_html_attrs={"body": {"class": "demo-components-body"}},
    )
