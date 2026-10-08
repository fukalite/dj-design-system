"""Tests for example_project showcase breadth, DDS gallery settings, and shadowing."""

import pathlib
import types

from django import template, test, urls

from dj_design_system import components, parameters
from dj_design_system import settings as dds_settings_mod
from dj_design_system import types as dds_types
from dj_design_system.services import canvas as canvas_service
from dj_design_system.services import navigation as navigation_service
from dj_design_system.services import registry as registry_service
from dj_design_system.services import visibility as visibility_service
from example_project import settings as base_settings
from example_project import settings_dds_gallery
from tests import conftest


EXAMPLE_PROJECT_DIR = pathlib.Path(base_settings.BASE_DIR) / "example_project"
CONSUMER_THEME_CSS = (
    EXAMPLE_PROJECT_DIR / "static" / "example_project" / "theme-dds-consumer.css"
)


def _render_template(*, library: template.Library, source: str) -> str:
    """Render a Django template string using the given template library."""
    engine = template.Engine()
    engine.template_builtins.append(library)
    compiled = engine.from_string(template_code=source)
    return compiled.render(context=template.Context())


class TestExampleProjectPedagogicalBreadth:
    """Verify example_project compliance with example-project.md."""

    def test_zero_private_tier1_token_leaks_in_example_project(self) -> None:
        """Ensure no file in example_project references private --_dds-* tokens."""
        text_suffixes = {".py", ".html", ".css", ".js", ".md"}
        leaking_files: list[str] = []
        for path in EXAMPLE_PROJECT_DIR.rglob(pattern="*"):
            if path.is_file() and path.suffix in text_suffixes:
                content = path.read_text(encoding="utf-8")
                if "--_dds-" in content:
                    leaking_files.append(str(path.relative_to(EXAMPLE_PROJECT_DIR)))
        assert not leaking_files

    def test_exercises_component_types_slots_and_parameters(self) -> None:
        """Verify TagComponent, BlockComponent, slots, and parameter types exist."""
        all_infos = registry_service.component_registry.list_all()
        consumer_infos = [
            info for info in all_infos if info.app_label != "dj_design_system"
        ]
        assert any(
            issubclass(info.component_class, components.TagComponent)
            for info in consumer_infos
        )
        assert any(
            issubclass(info.component_class, components.BlockComponent)
            for info in consumer_infos
        )
        assert any(
            issubclass(info.component_class, components.BlockComponent)
            and info.component_class.has_slots()
            for info in consumer_infos
        )

        param_types_used = {
            type(param)
            for info in consumer_infos
            for param in info.component_class.get_params().values()
        }
        expected_param_types = {
            parameters.StrParam,
            parameters.BoolParam,
            parameters.UserParam,
        }
        assert expected_param_types.issubset(param_types_used)

    def test_exercises_directory_strategies_media_variants_and_docs(self) -> None:
        """Verify FlattenStrategy, promote_to_app, broken_components, and docs."""
        dirs_config = base_settings.DJ_DESIGN_SYSTEM["COMPONENT_DIRECTORIES"]
        demo_dirs = dirs_config["demo_components"]
        assert demo_dirs["card"]["flatten"] == dds_types.FlattenStrategy.NONE
        assert demo_dirs["icon"]["flatten"] == dds_types.FlattenStrategy.ALL
        assert demo_dirs["promoted"]["promote_to_app"] is True
        assert "broken_components" in dirs_config

        demo_infos = registry_service.component_registry.list_by_app(
            app_label="demo_components"
        )
        assert any(info.media.css for info in demo_infos)
        assert any(info.gallery_config.variants for info in demo_infos)

        md_files = list(EXAMPLE_PROJECT_DIR.rglob(pattern="index.md"))
        assert md_files
        assert any(
            "```canvas" in md.read_text(encoding="utf-8") for md in md_files
        )


class TestSettingsDdsGallery:
    """Verify example_project.settings_dds_gallery configuration and visibility."""

    def test_settings_dds_gallery_configuration(self) -> None:
        """Verify DJ_DESIGN_SYSTEM overrides in settings_dds_gallery."""
        dds_cfg = settings_dds_gallery.DJ_DESIGN_SYSTEM
        assert (
            dds_cfg["DESIGN_SYSTEM_NAME"]
            == "dj-design-system Internal Component Library"
        )
        assert dds_cfg["GALLERY_SHOW_DDS_COMPONENTS"] is True
        assert set(dds_cfg["GALLERY_EXCLUDE_APPS"]) == {
            "demo_components",
            "demo_extra",
            "demo_nav",
            "demo_single",
            "broken_components",
        }
        assert dds_cfg["GLOBAL_CSS"] == ["example_project/theme-dds-consumer.css"]

    def test_navigation_and_views_expose_only_builtin_dds_components(
        self, client: test.Client
    ) -> None:
        """Verify navigation and gallery views show all built-in DDS components."""
        navigation_service.clear_navigation_cache()
        try:
            with test.override_settings(
                DJ_DESIGN_SYSTEM=settings_dds_gallery.DJ_DESIGN_SYSTEM
            ):
                assert (
                    dds_settings_mod.dds_settings.GALLERY_SHOW_DDS_COMPONENTS is True
                )
                visible = visibility_service.get_gallery_components()
                visible_apps = {info.app_label for info in visible}
                assert visible_apps == {"dj_design_system"}
                assert len(visible) >= 22

                collections = {
                    info.relative_path.split(".")[0] for info in visible
                }
                assert collections == {"domain", "elements"}

                nav_tree = navigation_service.build_navigation()
                assert [node.slug for node in nav_tree] == ["dj_design_system"]

                response = client.get(path=urls.reverse(viewname="gallery"))
                assert response.status_code == 200
                assert response.context["total_components"] == len(visible)
        finally:
            navigation_service.clear_navigation_cache()


class TestConsumerTier2TokenTheming:
    """Verify theme-dds-consumer.css overrides Tier 2 --dds-* tokens cleanly."""

    def test_consumer_theme_stylesheet_uses_only_tier2_dds_tokens(self) -> None:
        """Verify :root and .gallery-theme-dark overrides with zero --_dds-* tokens."""
        assert CONSUMER_THEME_CSS.is_file()
        css_text = CONSUMER_THEME_CSS.read_text(encoding="utf-8")
        assert ":root" in css_text
        assert ".gallery-theme-dark" in css_text
        assert "--dds-color-accent:" in css_text
        assert "--dds-color-accent-hover:" in css_text
        assert "--dds-radius-md:" in css_text
        assert "--dds-font-sans:" in css_text
        assert "--dds-control-accent-color:" in css_text
        assert "--_dds-" not in css_text


class TestConsumerDdsComponentShadowing:
    """Verify a consumer component with prefix 'dds' shadows a built-in component."""

    def test_consumer_dds_prefix_shadows_builtin_badge_component(self) -> None:
        """Registering a consumer badge under 'dds' shadows built-in dds__badge."""
        override_module = types.ModuleType("demo_single.components.dds_overrides")

        class BadgeComponent(components.TagComponent):
            """Consumer override for dds__badge."""

            template_format_str = (
                "<span class='consumer-dds-badge'>{label}</span>"
            )
            label = parameters.StrParam(
                default="Custom",
                description="Badge label.",
            )

        BadgeComponent.__module__ = override_module.__name__
        override_module.BadgeComponent = BadgeComponent  # type: ignore[attr-defined]

        with test.override_settings(
            DJ_DESIGN_SYSTEM={
                "COMPONENT_DIRECTORIES": {
                    "demo_single": {
                        "dds_overrides": {
                            "prefix": "dds",
                            "flatten": dds_types.FlattenStrategy.ALL,
                        }
                    }
                }
            }
        ):
            reg = registry_service.ComponentRegistry()
            conftest.discover_app_into_registry(
                reg=reg,
                app_name="dj_design_system",
                app_label="dj_design_system",
            )
            reg._discover_module(
                module=override_module,
                app_label="demo_single",
                relative_path="dds_overrides",
            )

            library = template.Library()
            reg.register_templatetags(library=library)

            rendered = _render_template(
                library=library,
                source='{% dds__badge label="Shadowed" %}',
            )
            assert "<span class='consumer-dds-badge'>Shadowed</span>" in rendered
            resolved = canvas_service.resolve_component(
                name="dds__badge",
                registry=reg,
            )
            assert resolved.app_label == "demo_single"
