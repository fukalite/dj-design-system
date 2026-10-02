"""Error and warning messages shown in a component's canvas.

They render inside component canvases, which load the project's own assets
and never the built-in components', so they are shared templates rather than
built-in components.
"""

from django.template.loader import render_to_string
from django.utils.safestring import SafeString, mark_safe


def canvas_error(
    message: str, *, label: str = "Canvas error", source: str = ""
) -> SafeString:
    """Return the error shown when a canvas can't render, with its ``source`` if given."""
    markup = render_to_string(
        "dj_design_system/canvas/error.html",
        {"label": label, "message": message, "source": source},
    )
    return mark_safe(markup.strip())  # noqa: S308 - the template escapes the values


def plain_str_warning(component_name: str, output: str) -> SafeString:
    """Return the warning shown, with the escaped ``output``, when a component's
    ``render()`` returns a plain ``str``."""
    markup = render_to_string(
        "dj_design_system/canvas/warning.html",
        {"component_name": component_name, "output": output},
    )
    return mark_safe(markup.strip())  # noqa: S308 - the template escapes the values
