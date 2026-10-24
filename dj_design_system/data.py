from __future__ import annotations

import inspect
import warnings
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any, Type

from dj_design_system.exceptions import InvalidTagType
from dj_design_system.gallery import GalleryConfig, Variant, load_gallery_config
from dj_design_system.types import FlattenStrategy, NodeType, TagType


BLOCK_CONTENT_PLACEHOLDER = "Sample content"
"""Default content used for block component previews in the canvas and code examples."""


@dataclass(frozen=True)
class CanvasSpec:
    """Specification for rendering a single component inside a canvas.

    Holds the component name, keyword parameters, positional arguments,
    and optional variant name needed to instantiate and render the component.
    """

    component_name: str
    params: dict[str, Any] = field(default_factory=dict)
    positional_args: tuple[Any, ...] = field(default_factory=tuple)
    variant: str | None = None


@dataclass(frozen=True)
class GalleryParameter:
    """An optional wrapper for specifying component parameter values in gallery views.

    This wrapper is not required for basic Python types (strings, booleans, ints, etc.).
    It is specifically useful when providing complex Django types (like QuerySets)
    as examples, where you want to pass the actual object to the sandbox preview,
    but show a simpler string representation in the template tag documentation.

    Args:
        value: The actual Python object or value to be passed to the component.
        code: Optional literal string to display in the generated template tag
            signature block (e.g. ``user=request.user`` instead of the stringified value).
    """

    value: Any
    code: str | None = None


@dataclass
class ComponentMedia:
    """
    Holds the static URL paths for CSS and JS files required by a component.

    Paths are Django static URL strings (e.g.
    ``"myapp/components/icon/icon.css"``), with no leading slash.  They
    are served by ``ComponentsStaticFinder`` and can be passed directly to
    ``{% static %}`` or used in ``<link>`` / ``<script>`` tags.
    """

    css: list[str] = field(default_factory=list)
    js: list[str] = field(default_factory=list)

    def merge(self, other: "ComponentMedia") -> "ComponentMedia":
        """Return a new ``ComponentMedia`` combining *self* and *other*.

        ``self`` entries appear first; duplicates are removed while
        preserving the original order of first appearance.
        """
        combined_css = list(dict.fromkeys(self.css + other.css))
        combined_js = list(dict.fromkeys(self.js + other.js))
        return ComponentMedia(css=combined_css, js=combined_js)

    def __bool__(self) -> bool:
        return bool(self.css or self.js)


@dataclass(frozen=True)
class ComponentInfo:
    """Metadata about a discovered component."""

    component_class: Type
    name: str
    app_label: str
    relative_path: str
    namespace_prefix: str | None = None
    namespace_remaining_parts: tuple[str, ...] | None = None
    flatten_strategy: FlattenStrategy = FlattenStrategy.NONE

    @cached_property
    def is_builtin(self) -> bool:
        """Return True for built-in framework components.

        Built-in components are registered only under their qualified name,
        ignored by short-name lookups, and excluded from ``get_media()``.
        """
        from dj_design_system.services.component import is_builtin

        return is_builtin(self.component_class, app_label=self.app_label)

    @property
    def class_name(self) -> str:
        """Return the Python component class name."""
        return self.component_class.__name__

    @property
    def gallery_basic_kwargs(self) -> dict[str, Any]:
        warnings.warn(
            f"ComponentInfo.gallery_basic_kwargs for '{self.name}' is deprecated and will be removed "
            "in a future release. Use ComponentInfo.gallery_config.get_variant('basic').kwargs instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._gallery_kwargs[0]

    @property
    def gallery_maximal_kwargs(self) -> dict[str, Any]:
        warnings.warn(
            f"ComponentInfo.gallery_maximal_kwargs for '{self.name}' is deprecated and will be removed "
            "in a future release. Use ComponentInfo.gallery_config.get_variant('maximal').kwargs instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._gallery_kwargs[1]

    @cached_property
    def _gallery_kwargs(self) -> tuple[dict, dict]:
        cfg = self.gallery_config
        basic_v = cfg.get_variant("basic")
        maximal_v = cfg.get_variant("maximal")
        return (
            dict(basic_v.kwargs) if basic_v else {},
            dict(maximal_v.kwargs) if maximal_v else {},
        )

    @cached_property
    def gallery_config(self) -> GalleryConfig:
        source_file = None
        try:
            if hasattr(self.component_class, "__file__"):
                source_file = Path(self.component_class.__file__)
            else:
                source_file = Path(inspect.getfile(self.component_class))
        except (TypeError, OSError):
            source_file = None

        if not source_file:
            return GalleryConfig()

        return load_gallery_config(source_file.parent, self.name)

    @property
    def qualified_name(self) -> str:
        """Return a fully qualified tag name: ``app_label__path__name``.

        Parts are joined with ``__``. If ``relative_path`` is empty,
        the result is ``{app_label}__{name}``.

        Examples::

            "fake_app__button"
            "fake_app__cards__info_card"
            "fake_app__cards__layouts__hero"
        """
        parts: list[str] = []
        if self.namespace_prefix is not None:
            if self.namespace_prefix:
                parts.append(self.namespace_prefix)

            rem = (
                list(self.namespace_remaining_parts)
                if self.namespace_remaining_parts
                else []
            )
            if self.flatten_strategy == FlattenStrategy.NONE:
                parts.extend(rem)
            elif self.flatten_strategy == FlattenStrategy.LEAF:
                if rem and rem[-1] == self.name:
                    rem = rem[:-1]
                parts.extend(rem)
            elif self.flatten_strategy == FlattenStrategy.ALL:
                pass
        else:
            parts.append(self.app_label)
            if self.relative_path:
                parts.extend(self.relative_path.split("."))

        parts.append(self.name)
        return "__".join(parts)

    @property
    def media(self) -> ComponentMedia:
        """Return the CSS and JS static URL paths required by this component.

        Both sources below are always consulted and merged together.  Explicit
        entries appear first; auto-discovered files are appended (duplicates
        removed):

        1. **Explicit ``Media`` class**: If any class in the component's MRO
           defines an inner ``Media`` class (like Django form widgets), those
           entries are collected.  Media from parent classes is merged before
           child additions, with duplicates removed.

        2. **Auto-discovery**: The registry looks for ``{name}.css`` and
           ``{name}.js`` files in the same directory as the component's Python
           source file.  Files that do not exist on disk are silently omitted.
        """
        from dj_design_system.services.media import build_static_url, get_own_media

        # Collect any explicit Media classes from the MRO.
        mro_media = [
            m
            for cls in self.component_class.__mro__
            if (m := get_own_media(cls)) is not None
        ]

        if mro_media:
            # MRO is child-first; reverse so parent media is merged first.
            mro_media.reverse()
            result = ComponentMedia()
            for m in mro_media:
                result = result.merge(m)
        else:
            result = ComponentMedia()

        # Always auto-discover co-located CSS/JS files.
        try:
            source_file = inspect.getfile(self.component_class)
        except (TypeError, OSError):
            return result

        source_path = Path(source_file)
        source_dir = source_path.parent
        auto_css: list[str] = []
        auto_js: list[str] = []

        for ext, target in ((".css", auto_css), (".js", auto_js)):
            candidates = list(
                dict.fromkeys([f"{self.name}{ext}", f"{source_path.stem}{ext}"])
            )
            for candidate in candidates:
                template_base_name = candidate[: -len(ext)]
                has_file = (source_dir / candidate).is_file() or (
                    ext == ".js" and (source_dir / f"{template_base_name}.ts").is_file()
                )
                if has_file:
                    target.append(
                        build_static_url(
                            self.app_label, self.relative_path, template_base_name, ext
                        )
                    )
                    break

        return result.merge(ComponentMedia(css=auto_css, js=auto_js))

    @property
    def template_name(self) -> str | None:
        """Return the resolved template name for this component, or ``None``.

        Set during registration by the registry's ``_bind_template()`` method.
        Returns the value of ``_template_name`` if it was placed on the class
        (either from an explicit ``template_name`` class attribute or from
        auto-discovering a co-located ``.html`` file), otherwise ``None``.

        When ``None``, the component renders via ``template_format_str``.
        """
        return getattr(self.component_class, "_template_name", None)

    @property
    def tag_type(self) -> TagType:
        """Return the tag registration type for this component.

        Returns ``TagType.TAG`` for ``TagComponent`` subclasses or
        ``TagType.BLOCK`` for ``BlockComponent`` subclasses.

        Raises ``InvalidTagType`` if the component class is a direct
        ``BaseComponent`` subclass that cannot be registered as a
        template tag.
        """
        from dj_design_system.components import BlockComponent, TagComponent

        if issubclass(self.component_class, BlockComponent):
            return TagType.BLOCK
        if issubclass(self.component_class, TagComponent):
            return TagType.TAG
        raise InvalidTagType(
            f"Component '{self.name}' ({self.component_class.__name__}) is a "
            f"direct BaseComponent subclass. Use TagComponent or BlockComponent."
        )


@dataclass
class NavNode:
    """A single node in the gallery navigation tree.

    A node can represent an app root, a folder, a component, a markdown
    document, or a component variant — or a combination (e.g. a folder that
    also carries a component when the leaf-folder collapsing rule is applied).
    """

    label: str
    slug: str
    node_type: NodeType
    children: list[NavNode] = field(default_factory=list)
    component: ComponentInfo | None = None
    variant: Variant | None = None
    doc_path: Path | None = None
    index_doc_path: Path | None = None
    icon: str | None = None
    order: int = 0
    url: str = ""
    active_path: str = ""
    base_active_path: str = ""
    app_label: str = ""
    _app_label: str = ""
    _path_parts: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate that data fields are consistent with ``node_type``."""
        if self.node_type == NodeType.COMPONENT and self.component is None:
            raise ValueError("COMPONENT nodes must have a ComponentInfo")
        if self.node_type != NodeType.COMPONENT and self.component is not None:
            raise ValueError(
                f"{self.node_type.value.upper()} nodes must not carry a ComponentInfo"
            )
        if self.node_type == NodeType.DOCUMENT and self.doc_path is None:
            raise ValueError("DOCUMENT nodes must have a doc_path")
        if self.node_type != NodeType.DOCUMENT and self.doc_path is not None:
            raise ValueError(
                f"{self.node_type.value.upper()} nodes must not carry a doc_path"
            )
        if self.node_type == NodeType.VARIANT and self.variant is None:
            raise ValueError("VARIANT nodes must have a Variant")
        if self.node_type != NodeType.VARIANT and self.variant is not None:
            raise ValueError(
                f"{self.node_type.value.upper()} nodes must not carry a Variant"
            )

    # ------------------------------------------------------------------
    # Mutation helpers — keep *node_type* and data fields in sync
    # ------------------------------------------------------------------

    def upgrade_to_component(self, info: ComponentInfo, label: str) -> None:
        """Atomically convert a folder node into a component node."""
        self.component = info
        self.node_type = NodeType.COMPONENT
        self.label = label
        self.icon = info.gallery_config.icon
        self.order = info.gallery_config.order

    # ------------------------------------------------------------------
    # Convenience predicates
    # ------------------------------------------------------------------

    @property
    def has_children(self) -> bool:
        return bool(self.children)

    @property
    def is_component(self) -> bool:
        return self.node_type == NodeType.COMPONENT

    @property
    def is_document(self) -> bool:
        return self.node_type == NodeType.DOCUMENT

    @property
    def is_variant(self) -> bool:
        return self.node_type == NodeType.VARIANT

    @property
    def has_variants(self) -> bool:
        """Return True if any immediate child node represents a variant."""
        return any(c.is_variant for c in self.children)

    @property
    def has_index_doc(self) -> bool:
        return self.index_doc_path is not None and self.index_doc_path.is_file()


def format_param_type_name(param_type: Any, fallback: str = "any") -> str:
    """Format a Python type, tuple of types, or string into a human-readable type label."""
    if isinstance(param_type, str) and param_type:
        return param_type
    if isinstance(param_type, tuple) and param_type:
        return " | ".join(getattr(t, "__name__", str(t)) for t in param_type)
    if getattr(param_type, "__name__", None):
        return str(getattr(param_type, "__name__"))
    if param_type is not None:
        return str(param_type)
    return fallback


@dataclass(frozen=True)
class ParamSpecData:
    """Immutable view of a component parameter specification."""

    description: str
    required: bool
    type_name: str
    default: Any = None
    choices: list[Any] | tuple[Any, ...] | None = None

    @classmethod
    def from_param(cls, spec_param: Any) -> ParamSpecData:
        """Create a ``ParamSpecData`` from a ``BaseParam``, dict, or existing instance."""
        if isinstance(spec_param, cls):
            return spec_param
        if isinstance(spec_param, dict):
            param_type = spec_param.get("type")
            raw_type_name = spec_param.get("type_name")
            return cls(
                description=str(spec_param.get("description") or ""),
                required=bool(spec_param.get("required", False)),
                type_name=(
                    str(raw_type_name)
                    if raw_type_name
                    else format_param_type_name(param_type)
                ),
                default=spec_param.get("default"),
                choices=spec_param.get("choices"),
            )
        param_type = getattr(spec_param, "type", type(spec_param))
        raw_type_name = getattr(spec_param, "type_name", None)
        return cls(
            description=str(getattr(spec_param, "description", "") or ""),
            required=bool(getattr(spec_param, "required", False)),
            type_name=(
                str(raw_type_name)
                if raw_type_name
                else format_param_type_name(param_type)
            ),
            default=getattr(spec_param, "default", None),
            choices=getattr(spec_param, "choices", None),
        )


@dataclass(frozen=True)
class ParamRowData:
    """Immutable parameter row combining a parameter name, spec, and bound form field."""

    name: str
    spec: ParamSpecData
    field: Any = None

    def __getitem__(self, key: str) -> Any:
        if key in ("name", "spec", "field"):
            return getattr(self, key)
        raise KeyError(key)

    def __contains__(self, key: object) -> bool:
        return key in ("name", "spec", "field")

    def get(self, key: str, default: Any = None) -> Any:
        if key in ("name", "spec", "field"):
            return getattr(self, key)
        return default
