import inspect
import re
import typing
from pathlib import Path

from dj_design_system.data import BUILTIN_APP_LABEL, BUILTIN_PREFIX


__all__ = [
    "BUILTIN_APP_LABEL",
    "BUILTIN_PREFIX",
    "EmptyMeta",
    "derive_name",
    "derive_relative_path",
    "get_meta_name",
    "get_own_meta",
    "is_abstract",
    "is_internal",
    "resolve_colocated_template",
]


class EmptyMeta:
    """Sentinel returned by ``get_own_meta`` when a class has no own Meta.

    Allows callers to use ``getattr`` unconditionally, without a None check.
    """


def get_own_meta(cls: type[typing.Any]) -> type[typing.Any]:
    """Return the Meta inner class defined directly on ``cls``.

    Only looks at the class's own ``__dict__``, not inherited Meta from
    parent classes - matching Django's convention where Meta is not
    inherited. Returns ``EmptyMeta`` if the class has no own Meta.
    """
    return cls.__dict__.get("Meta", EmptyMeta)


def is_abstract(cls: type[typing.Any]) -> bool:
    """Return True if the class's own Meta marks it as abstract."""
    return getattr(get_own_meta(cls), "abstract", False)


def is_internal(cls: type[typing.Any], app_label: str) -> bool:
    """Return True if the component is internal.

    Built-in components (from the ``dj_design_system`` app) are always
    internal. Any other component is internal when its own ``Meta`` sets
    ``internal = True``; like other ``Meta`` options, it is not inherited.
    """
    return app_label == BUILTIN_APP_LABEL or bool(
        getattr(get_own_meta(cls), "internal", False)
    )


def get_meta_name(cls: type[typing.Any]) -> str | None:
    """Return the explicit name from the class's own Meta, if provided."""
    name = getattr(get_own_meta(cls), "name", None)
    return name if isinstance(name, str) else None


def derive_name(cls: type[typing.Any]) -> str:
    """
    Derive a component name from a class name by stripping a trailing
    'Component' suffix and converting to snake_case.

    Examples:
        IconComponent -> "icon"
        MyFancyButton -> "my_fancy_button"
        HeroCardComponent -> "hero_card"
        Component -> "component"  (no stripping when it's the entire name)
    """
    COMPONENT_SUFFIX = "Component"
    class_name = cls.__name__

    # Strip trailing "Component" if it's not the entire name
    if class_name.endswith(COMPONENT_SUFFIX) and class_name != COMPONENT_SUFFIX:
        class_name = class_name[: -len(COMPONENT_SUFFIX)]

    # CamelCase to snake_case
    name = re.sub(r"(?<=[a-z0-9])([A-Z])", r"_\1", class_name)
    name = re.sub(r"(?<=[A-Z])([A-Z][a-z])", r"_\1", name)
    return name.lower()


def derive_relative_path(modname: str, components_module_path: str) -> str:
    """
    Derive the dotted directory path relative to the ``components`` package.

    For example, given:
        modname = "myapp.components.buttons.primary"
        components_module_path = "myapp.components"
    Returns ``"buttons"`` (the directory containing ``primary.py``,
    excluding the module file name itself).
    """
    suffix = modname[len(components_module_path) + 1 :]
    parts = suffix.split(".")
    return ".".join(parts[:-1])  # drop the module filename, keep directories


def resolve_colocated_template(
    cls: type[typing.Any],
    *,
    app_label: str | None = None,
    relative_path: str | None = None,
    name: str | None = None,
) -> str | None:
    """Resolve the template loader path for a component's co-located ``.html`` file.

    Args:
        cls: The component class to inspect.
        app_label: Optional explicit Django app label; derived from ``cls.__module__``
            when omitted.
        relative_path: Optional dotted path relative to ``components/``; derived
            from ``cls.__module__`` when omitted.
        name: Optional component name; derived from ``cls`` when omitted.

    Returns:
        The ``{app_label}/components/{sub_path}/{name}.html`` template path if a
        co-located ``.html`` file exists on disk, or ``None``.
    """
    from dj_design_system.services.media import build_static_url

    try:
        source_file = inspect.getfile(cls)
    except (TypeError, OSError):
        return None

    source_path = Path(source_file)
    source_dir = source_path.parent
    comp_name = name or get_meta_name(cls) or derive_name(cls)

    candidates = list(dict.fromkeys([f"{comp_name}.html", f"{source_path.stem}.html"]))
    matched_stem: str | None = None
    for candidate in candidates:
        if (source_dir / candidate).is_file():
            matched_stem = candidate[:-5]
            break

    if matched_stem is None:
        return None

    if app_label is None or relative_path is None:
        mod_name = getattr(cls, "__module__", "")
        if ".components" in mod_name:
            app_prefix, _, after = mod_name.partition(".components")
            if app_label is None:
                app_label = app_prefix.rsplit(".", 1)[-1]
            if relative_path is None:
                if after.startswith("."):
                    sub_parts = after[1:].split(".")
                    relative_path = ".".join(sub_parts[:-1])
                else:
                    relative_path = ""
        elif "components" in source_path.parts:
            idx = (
                len(source_path.parts) - 1 - source_path.parts[::-1].index("components")
            )
            if app_label is None and idx > 0:
                app_label = source_path.parts[idx - 1]
            if relative_path is None:
                rel_parts = source_path.parts[idx + 1 : -1]
                relative_path = ".".join(rel_parts)

    if not app_label:
        return None

    return build_static_url(app_label, relative_path or "", matched_stem, ".html")
