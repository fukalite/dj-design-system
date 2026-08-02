import pytest


pytest_plugins = ["pytester"]


def test_testing_module_importable():
    """Verify that the testing module can be imported when extras are installed."""
    try:
        import dj_design_system.testing  # noqa: F401
    except ImportError:
        pytest.fail("dj_design_system.testing should be importable.")


def test_base_pytest_fixtures_available(pytester):
    """Verify that the basic pytest fixtures are exposed by the testing module."""
    # We can use pytester to verify our fixture gets registered, but for now we
    # just check if the module exposes the expected fixtures list or function.
    import dj_design_system.testing

    assert hasattr(dj_design_system.testing, "design_system_iteration_engine")
