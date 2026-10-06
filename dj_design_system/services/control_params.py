"""Gallery and canvas control query parameters.

Control parameters (``variant``, ``mode``, ``theme``, ``bg``) are sent with a
``_dds_`` prefix so they cannot collide with component parameters of the same
name. The bare names are still accepted as a legacy fallback, but only where
the bare name cannot belong to the component.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


CONTROL_PARAM_PREFIX = "_dds_"
CONTROL_PARAM_NAMES = ("variant", "mode", "theme", "bg")

# Sent by the sandbox form so the server knows bare names belong to the component.
SANDBOX_SUBMISSION_PARAM = "_iss"


def control_param_key(name: str) -> str:
    """Return the namespaced query key for control parameter ``name``."""
    return f"{CONTROL_PARAM_PREFIX}{name}"


def declares_param(component_class: Any, name: str) -> bool:
    """Return True if ``component_class`` declares a parameter called ``name``."""
    if component_class is None:
        return False
    params = getattr(component_class, "get_params", lambda: {})()
    positional = getattr(component_class, "get_positional_args", lambda: [])()
    return name in params or name in positional


def get_control_param(
    query: Mapping[str, str], name: str, *, bare_fallback: bool = True
) -> str | None:
    """Return the value of control parameter ``name`` from ``query``.

    The namespaced key always wins, including when empty (an explicit
    "default"). The bare key is only consulted when ``bare_fallback`` is true.
    Returns ``None`` when neither source supplies the parameter.
    """
    key = control_param_key(name)
    if key in query:
        return query[key]
    if bare_fallback and name in query:
        return query[name]
    return None
