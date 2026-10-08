"""Shared fixtures for dj_design_system tests."""

import pkgutil
import sys
import textwrap
from importlib import import_module
from pathlib import Path

import pytest
from django.contrib.auth import get_user_model

from dj_design_system.data import ComponentInfo
from dj_design_system.services.component import derive_relative_path
from dj_design_system.services.navigation import _build_navigation
from dj_design_system.services.registry import ComponentRegistry


User = get_user_model()

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

DEMO_NAV = "example_project.demo_nav"
DEMO_NAV_COMPONENTS = (
    Path(__file__).parent.parent / "example_project" / "demo_nav" / "components"
)


def discover_app_into_registry(
    reg: ComponentRegistry, app_name: str, app_label: str
) -> None:
    """Simulate autodiscovery for a single app into an existing registry."""
    module_path = f"{app_name}.components"
    module = import_module(module_path)
    reg._discover_module(module, app_label, relative_path="")

    if hasattr(module, "__path__"):
        for _importer, modname, _ispkg in pkgutil.walk_packages(
            module.__path__, prefix=module.__name__ + "."
        ):
            submodule = import_module(modname)
            relative_path = derive_relative_path(modname, module_path)
            reg._discover_module(submodule, app_label, relative_path)


def make_info(
    name: str,
    app_label: str = "test_app",
    relative_path: str = "",
) -> ComponentInfo:
    """Create a minimal ComponentInfo for testing (no real class needed)."""
    return ComponentInfo(
        component_class=type(f"{name}_cls", (), {}),
        name=name,
        app_label=app_label,
        relative_path=relative_path,
    )


@pytest.fixture()
def builtin_modules(tmp_path):
    """Factory adding temporary modules under ``dj_design_system.components``.

    Call it with ``{"<subpackage>/<module>.py": source}``. The files are
    written to a temporary directory appended to the package's ``__path__``,
    so autodiscovery treats them exactly like real built-in components.
    Returns the registry-ready ``tmp_path`` root; everything is removed from
    ``__path__`` and ``sys.modules`` afterwards.
    """
    import dj_design_system.components as components_package

    root = tmp_path / "builtins"
    root.mkdir()
    components_package.__path__.append(str(root))
    before = set(sys.modules)

    def add(files: dict[str, str]) -> Path:
        for relative, source in files.items():
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            for parent in path.relative_to(root).parents:
                init = root / parent / "__init__.py"
                if parent != Path(".") and not init.exists():
                    init.write_text("")
            path.write_text(textwrap.dedent(source))
        return root

    yield add

    components_package.__path__.remove(str(root))
    for name in set(sys.modules) - before:
        if name.startswith("dj_design_system.components."):
            del sys.modules[name]


# ---------------------------------------------------------------------------
# Registry fixtures
#
# Fixtures return only the registry — component classes are imported at the
# top of each test file, avoiding brittle positional tuple unpacking.
# ---------------------------------------------------------------------------


@pytest.fixture()
def registry_with_demo_components():
    """Create a fresh ComponentRegistry with demo_components only."""
    reg = ComponentRegistry()
    discover_app_into_registry(
        reg, "example_project.demo_components", "demo_components"
    )
    return reg


@pytest.fixture()
def registry_with_two_apps(registry_with_demo_components):
    """Extend the demo_components registry with demo_extra to test duplicate names."""
    reg = registry_with_demo_components
    discover_app_into_registry(reg, "example_project.demo_extra", "demo_extra")
    return reg


@pytest.fixture()
def registry_with_demo_single():
    """Create a registry with the single-file components.py app."""
    reg = ComponentRegistry()
    discover_app_into_registry(reg, "example_project.demo_single", "demo_single")
    return reg


# ---------------------------------------------------------------------------
# Navigation fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def nav_registry():
    """Registry loaded with demo_nav components."""
    reg = ComponentRegistry()
    discover_app_into_registry(reg, DEMO_NAV, "demo_nav")
    return reg


@pytest.fixture()
def nav_tree(nav_registry):
    """Full navigation tree for demo_nav including markdown discovery."""
    return _build_navigation(
        nav_registry.list_all(),
        app_component_paths={"demo_nav": DEMO_NAV_COMPONENTS},
    )


@pytest.fixture()
def nav_tree_no_docs(nav_registry):
    """Navigation tree for demo_nav without markdown discovery."""
    return _build_navigation(nav_registry.list_all())


# ---------------------------------------------------------------------------
# View fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def user_client(client):
    """A test client logged in as a user with a profile (needed for 404 pages)."""
    user = User.objects.create_user(username="testgallery")
    client.force_login(user)
    return client


# ---------------------------------------------------------------------------
# Canvas fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def internal_registry(builtin_modules):
    """Built-ins discovered first, then a consumer app (INSTALLED_APPS order)."""
    from tests.test_internal_components import BUILTINS, _add_builtins, _add_consumer

    builtin_modules(BUILTINS)
    reg = ComponentRegistry()
    _add_builtins(reg)
    _add_consumer(reg)
    return reg


@pytest.fixture()
def visibility_registry(builtin_modules):
    """Built-ins plus two consumer apps for gallery visibility tests."""
    from tests.test_gallery_visibility import BUILTINS

    builtin_modules(BUILTINS)
    reg = ComponentRegistry()
    discover_app_into_registry(reg, "dj_design_system", "dj_design_system")
    discover_app_into_registry(
        reg, "example_project.demo_components", "demo_components"
    )
    discover_app_into_registry(reg, "example_project.demo_single", "demo_single")
    return reg


@pytest.fixture()
def global_builtins(builtin_modules):
    """Temporarily add the fixture built-ins to the global registry."""
    from dj_design_system.services.registry import component_registry
    from tests.test_gallery_visibility import BUILTINS

    builtin_modules(BUILTINS)
    before = list(component_registry._components)
    discover_app_into_registry(
        component_registry, "dj_design_system", "dj_design_system"
    )
    yield
    component_registry._components[:] = before


@pytest.fixture(autouse=True)
def _clear_nav_cache():
    """Clear navigation and search index cache before and after every test."""
    from dj_design_system.services.navigation import clear_navigation_cache

    clear_navigation_cache()
    yield
    clear_navigation_cache()
