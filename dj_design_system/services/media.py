import html
from typing import Type

from django.templatetags.static import static
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe

from dj_design_system.data import ComponentMedia

try:
    from webpack_loader.utils import get_files as _webpack_get_files

    _WEBPACK_AVAILABLE = True
except ImportError:
    _webpack_get_files = None
    _WEBPACK_AVAILABLE = False


def coerce_path_list(value: str | list[str]) -> list[str]:
    """Normalise a CSS/JS path value to a list of strings.

    Accepts either a single string or a list of strings, returning a list
    in both cases.  This mirrors the convention used by Django's form widget
    ``Media`` inner class, where single strings are also accepted.
    """
    if isinstance(value, str):
        return [value]
    return list(value)


def get_own_media(cls: Type) -> ComponentMedia | None:
    """Return a ``ComponentMedia`` built from *cls*'s own ``Media`` inner class.

    Returns ``None`` if *cls* has no ``Media`` defined directly on it (i.e.
    not inherited).  Accepts a single string or a list for each of ``css``
    and ``js``.
    """
    media_cls = cls.__dict__.get("Media")
    if media_cls is None:
        return None

    css_raw = coerce_path_list(getattr(media_cls, "css", []))
    js_raw = coerce_path_list(getattr(media_cls, "js", []))

    return ComponentMedia(css=css_raw, js=js_raw)


def get_bundle_urls(bundles: list[tuple], extension: str) -> list[str]:
    """Return chunk URLs from webpack bundles, or an empty list.

    Each entry in *bundles* is a tuple whose first element is the bundle name
    and whose optional second element is the webpack_loader config name
    (defaults to ``"DEFAULT"``).  Returns an empty list when
    ``webpack_loader`` is not installed or *bundles* is empty.
    """
    if not _WEBPACK_AVAILABLE or not bundles:
        return []
    urls: list[str] = []
    for bundle_args in bundles:
        bundle_name = bundle_args[0]
        config = bundle_args[1] if len(bundle_args) > 1 else "DEFAULT"
        for chunk in _webpack_get_files(
            bundle_name, extension=extension, config=config
        ):
            urls.append(chunk["url"])
    return urls


def build_static_url(app_label: str, relative_path: str, name: str, ext: str) -> str:
    """Build the Django static URL for a co-located component asset.

    Given a component with ``app_label="myapp"``, ``relative_path="cards"``,
    ``name="hero"`` and ``ext=".css"``, returns
    ``"myapp/components/cards/hero.css"``.
    """
    parts = [app_label, "components"]
    if relative_path:
        parts.extend(relative_path.split("."))
    parts.append(f"{name}{ext}")
    return "/".join(parts)


def resolve_asset_url(*, path: str) -> str:
    """Return external URLs unchanged; resolve local paths via ``static()``.

    Args:
        path: A static file path or external URL (``http://``, ``https://``, ``//``).
            The scheme is matched case-insensitively.

    Returns:
        The resolved asset URL string.
    """
    if path.lower().startswith(("http://", "https://", "//")):
        return path
    return static(path)


def build_link_tags(css_paths: list[str]) -> str:
    """Build ``<link>`` tags for a list of static or external CSS paths."""
    if not css_paths:
        return ""
    return format_html_join(
        "\n",
        '<link rel="stylesheet" href="{}">',
        ((resolve_asset_url(path=path),) for path in css_paths),
    )


def build_script_tags(js_paths: list[str], nonce: str | None = None) -> str:
    """Build ``<script>`` tags for a list of static or external JS paths."""
    if not js_paths:
        return ""
    if nonce:
        nonce_attr = mark_safe(f' nonce="{html.escape(str(nonce))}"')
        return format_html_join(
            "\n",
            f'<script src="{{}}" {nonce_attr}></script>',
            ((resolve_asset_url(path=path),) for path in js_paths),
        )
    return format_html_join(
        "\n",
        '<script src="{}"></script>',
        ((resolve_asset_url(path=path),) for path in js_paths),
    )


COMPONENTS_TEMPLATE_LOADER = "dj_design_system.loaders.ComponentsTemplateLoader"
COMPONENTS_STATIC_FINDER = "dj_design_system.finders.ComponentsStaticFinder"


def _contains_loader(loaders: list | tuple, target: str) -> bool:
    for entry in loaders:
        if entry == target:
            return True
        if (
            isinstance(entry, (list, tuple))
            and len(entry) >= 2
            and isinstance(entry[1], (list, tuple))
            and _contains_loader(entry[1], target)
        ):
            return True
    return False


def ensure_component_loaders_and_finders() -> None:
    """Ensure ``ComponentsTemplateLoader`` and ``ComponentsStaticFinder`` are active.

    Registers the static finder in ``settings.STATICFILES_FINDERS`` and the
    template loader on active ``DjangoTemplates`` engines if the consumer project
    did not explicitly configure them in ``settings.py``.
    """
    from django.conf import settings
    from django.contrib.staticfiles import finders as static_finders
    from django.template import engines
    from django.template.backends.django import DjangoTemplates

    finders_list = list(getattr(settings, "STATICFILES_FINDERS", ()))
    if COMPONENTS_STATIC_FINDER not in finders_list:
        settings.STATICFILES_FINDERS = [*finders_list, COMPONENTS_STATIC_FINDER]
        static_finders.get_finder.cache_clear()

    for backend in engines.all():
        if not isinstance(backend, DjangoTemplates):
            continue
        engine = backend.engine
        if _contains_loader(engine.loaders, COMPONENTS_TEMPLATE_LOADER):
            continue
        engine.loaders = [*engine.loaders, COMPONENTS_TEMPLATE_LOADER]
        engine.__dict__.pop("template_loaders", None)
        if hasattr(engine.get_template, "cache_clear"):
            engine.get_template.cache_clear()

