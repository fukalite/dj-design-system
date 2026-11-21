"""Import-safety tests ensuring settings-time imports never touch Django settings."""

from __future__ import annotations

import os
import subprocess
import sys

from django.contrib.auth import get_user_model

from dj_design_system.parameters.user import UserParam


def test_importing_config_and_types_does_not_load_django() -> None:
    env = {k: v for k, v in os.environ.items() if k != "DJANGO_SETTINGS_MODULE"}
    code = (
        "import sys; "
        "import dj_design_system.constants; "
        "import dj_design_system.types; "
        "import dj_design_system.config; "
        "assert 'django' not in sys.modules, list(m for m in sys.modules if m.startswith('django'))"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"stdout={result.stdout}\nstderr={result.stderr}"


def test_importing_user_param_does_not_evaluate_django_settings() -> None:
    env = {k: v for k, v in os.environ.items() if k != "DJANGO_SETTINGS_MODULE"}
    code = "import dj_design_system.parameters.user"
    result = subprocess.run(
        [sys.executable, "-c", code],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, f"stdout={result.stdout}\nstderr={result.stderr}"


def test_user_param_resolves_auth_user_model_lazily() -> None:
    param = UserParam("The acting user.")
    assert param._resolve_model() is get_user_model()
    assert callable(UserParam.Meta.model)
