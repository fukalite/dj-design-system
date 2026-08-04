import pytest


pytest_plugins = ["pytester"]


def test_testing_module_importable():
    """Verify that the testing module can be imported when extras are installed."""
    try:
        import dj_design_system.testing  # noqa: F401
    except ImportError:
        pytest.fail("dj_design_system.testing should be importable.")


