from __future__ import annotations

import inspect
import warnings
from dataclasses import dataclass, field
from functools import cached_property
from pathlib import Path
from typing import Any, Type

from django.utils import safestring

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


BUILTIN_APP_LABEL = "dj_design_system"
"""App label of the package itself; its components are built-ins."""

BUILTIN_PREFIX = "dds"
"""Qualified-name prefix for built-in components, e.g. ``dds__button``."""


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
    def is_internal(self) -> bool:
        """Return True for built-in components and those with ``Meta.internal = True``.

        Internal components are registered only under their qualified name,
        ignored by short-name lookups, and excluded from ``get_merged_media()``.
        """
        meta = self.component_class.__dict__.get("Meta")
        return self.app_label == BUILTIN_APP_LABEL or bool(
            getattr(meta, "internal", False)
        )

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
    def has_index_doc(self) -> bool:
        return self.index_doc_path is not None


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


def _get_field(raw: Any, key: str, default: Any = None) -> Any:
    """Read *key* from a mapping or attribute from an object."""
    if isinstance(raw, dict):
        return raw.get(key, default)
    return getattr(raw, key, default)


@dataclass(frozen=True)
class SandboxControlOptionData:
    """Normalized option item for ThemeSelect and SandboxToolbar controls."""

    value: str
    label: str
    name: str = ""
    href: str = ""
    is_selected: bool = False

    @classmethod
    def from_raw(
        cls,
        raw_item: Any,
        *,
        base_url: str = "",
        is_variant: bool = False,
        is_zoom: bool = False,
        default_label: str = "Default",
    ) -> SandboxControlOptionData:
        """Normalise a string, 2-tuple, dict, ``Theme``, or ``Variant`` into an option."""
        if is_variant:
            if isinstance(raw_item, str):
                raw_name: Any = raw_item
                raw_label: Any = (
                    raw_item.capitalize() if raw_item.islower() else raw_item
                )
                raw_href: Any = None
            else:
                raw_name = _get_field(raw_item, "name")
                raw_label = _get_field(raw_item, "label")
                raw_href = _get_field(raw_item, "href")

            name = str(raw_name) if raw_name is not None else ""
            if raw_label is not None:
                label = str(raw_label)
            elif name:
                label = name.capitalize() if name.islower() else name
            else:
                label = default_label

            if raw_href is not None and str(raw_href):
                href = str(raw_href)
            elif base_url:
                if name:
                    separator = "&" if "?" in base_url else "?"
                    href = f"{base_url}{separator}variant={name}"
                else:
                    href = base_url
            else:
                href = ""
            return cls(value=name, label=label, name=name, href=href)

        if is_zoom:
            if isinstance(raw_item, (tuple, list)) and len(raw_item) >= 2:
                zoom_val = str(raw_item[0]).rstrip("%")
                zoom_lbl = str(raw_item[1])
            elif isinstance(raw_item, dict) or hasattr(raw_item, "value"):
                raw_val = _get_field(raw_item, "value")
                raw_lbl = _get_field(raw_item, "label")
                zoom_val = str(raw_val).rstrip("%") if raw_val is not None else ""
                zoom_lbl = str(raw_lbl) if raw_lbl is not None else f"{zoom_val}%"
            else:
                zoom_val = str(raw_item).rstrip("%")
                zoom_lbl = f"{zoom_val}%"
            return cls(value=zoom_val, label=zoom_lbl)

        if isinstance(raw_item, (tuple, list)) and len(raw_item) >= 2:
            value = str(raw_item[0])
            label = str(raw_item[1])
        elif isinstance(raw_item, str):
            value = raw_item
            label = raw_item.capitalize() if raw_item.islower() else raw_item
        else:
            raw_val = _get_field(raw_item, "value")
            raw_lbl = _get_field(raw_item, "label")
            value = str(raw_val) if raw_val is not None else ""
            label = (
                str(raw_lbl)
                if raw_lbl is not None
                else (value.capitalize() if value.islower() else value)
            )
        return cls(value=value, label=label)

    def to_dict(self, *, is_selected: bool | None = None) -> dict[str, Any]:
        """Return a template-ready dictionary representation."""
        selected = self.is_selected if is_selected is None else is_selected
        if self.name or self.href:
            return {
                "name": self.name,
                "label": self.label,
                "href": self.href,
                "is_selected": selected,
            }
        return {
            "value": self.value,
            "label": self.label,
            "is_selected": selected,
        }


@dataclass(frozen=True)
class FormFieldRowData:
    """Normalized parameter form row for ``ParamsForm``."""

    name: str
    label: str
    field_id: str
    description: str
    required: bool
    errors: list[str]
    error: str
    has_field_html: bool
    field_html: Any

    @classmethod
    def from_raw(cls, raw_item: Any) -> FormFieldRowData:
        """Normalise a ``ParamRowData``, dict, or duck-typed row object."""
        raw_name = _get_field(raw_item, "name", "")

        raw_label = _get_field(raw_item, "label")
        raw_spec = _get_field(raw_item, "spec")
        raw_field = _get_field(raw_item, "field")
        raw_field_id = _get_field(raw_item, "field_id", "")
        raw_description = _get_field(raw_item, "description")
        raw_required = _get_field(raw_item, "required", False)
        raw_item_errors = _get_field(raw_item, "errors")

        name = str(raw_name) if raw_name is not None else ""
        label = str(raw_label) if raw_label else name
        field_id = str(
            getattr(raw_field, "id_for_label", None) or raw_field_id or f"id_{name}"
        )
        spec_desc = (
            _get_field(raw_spec, "description") if raw_spec is not None else None
        )
        description = str(spec_desc or raw_description or "")
        if raw_spec is not None:
            required = bool(_get_field(raw_spec, "required", False))
        else:
            required = bool(raw_required)

        field_errors = getattr(raw_field, "errors", None)
        raw_errors = field_errors if field_errors is not None else raw_item_errors
        if isinstance(raw_errors, str):
            errors = [raw_errors] if raw_errors else []
        elif raw_errors is not None:
            errors = [str(err) for err in raw_errors]
        else:
            errors = []
        error = " ".join(errors)

        has_field_html = raw_field is not None
        field_html: Any = (
            safestring.SafeString(str(raw_field)) if has_field_html else ""
        )
        return cls(
            name=name,
            label=label,
            field_id=field_id,
            description=description,
            required=required,
            errors=errors,
            error=error,
            has_field_html=has_field_html,
            field_html=field_html,
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation for template contexts."""
        return {
            "name": self.name,
            "label": self.label,
            "field_id": self.field_id,
            "description": self.description,
            "required": self.required,
            "errors": self.errors,
            "error": self.error,
            "has_field_html": self.has_field_html,
            "field_html": self.field_html,
        }

    def __getitem__(self, key: str) -> Any:
        return self.to_dict()[key]


@dataclass(frozen=True)
class ParamTableRowData:
    """Normalized parameter metadata row for ``ParamsTable``."""

    name: str
    type_name: str
    required: bool
    required_label: str
    required_variant: str
    has_default: bool
    default_display: str
    choices: list[str]
    has_choices: bool
    description: str

    @classmethod
    def from_raw(
        cls,
        raw_item: Any,
        *,
        empty_placeholder: str = "—",
        fallback_type_name: str = "any",
    ) -> ParamTableRowData:
        """Normalise a ``(name, spec)`` tuple, ``ParamRowData``, dict, or object."""
        if isinstance(raw_item, (tuple, list)) and len(raw_item) == 2:
            raw_name: Any = raw_item[0]
            spec: Any = raw_item[1]
        else:
            raw_name = _get_field(raw_item, "name", "")
            nested_spec = _get_field(raw_item, "spec")
            spec = nested_spec if nested_spec is not None else raw_item

        raw_type_name = _get_field(spec, "type_name")
        raw_type = _get_field(spec, "type")
        raw_required = _get_field(spec, "required", False)
        raw_default = _get_field(spec, "default")
        raw_choices = _get_field(spec, "choices")
        raw_description = _get_field(spec, "description")

        type_name = (
            str(raw_type_name)
            if raw_type_name
            else format_param_type_name(raw_type, fallback=fallback_type_name)
        )
        required = bool(raw_required)
        has_default = raw_default is not None
        choices = (
            [str(choice) for choice in raw_choices] if raw_choices is not None else []
        )
        return cls(
            name=str(raw_name) if raw_name is not None else "",
            type_name=type_name,
            required=required,
            required_label="Required" if required else "Optional",
            required_variant="error" if required else "neutral",
            has_default=has_default,
            default_display=str(raw_default) if has_default else empty_placeholder,
            choices=choices,
            has_choices=bool(choices),
            description=str(raw_description) if raw_description else empty_placeholder,
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation for template contexts."""
        return {
            "name": self.name,
            "type_name": self.type_name,
            "required": self.required,
            "required_label": self.required_label,
            "required_variant": self.required_variant,
            "has_default": self.has_default,
            "default_display": self.default_display,
            "choices": self.choices,
            "has_choices": self.has_choices,
            "description": self.description,
        }

    def __getitem__(self, key: str) -> Any:
        return self.to_dict()[key]


@dataclass(frozen=True)
class SlotTableRowData:
    """Normalized slot metadata row for ``ParamsTable``."""

    name: str
    required: bool
    required_label: str
    required_variant: str
    has_default: bool
    default_display: str
    description: str

    @classmethod
    def from_raw(
        cls,
        raw_slot: Any,
        *,
        empty_placeholder: str = "—",
    ) -> SlotTableRowData:
        """Normalise a ``(name, slot)`` tuple, dict, or slot object."""
        if isinstance(raw_slot, (tuple, list)) and len(raw_slot) == 2:
            raw_slot_name: Any = raw_slot[0]
            slot_spec: Any = raw_slot[1]
        else:
            raw_slot_name = _get_field(raw_slot, "name", "")
            nested_slot = _get_field(raw_slot, "slot")
            if nested_slot is None:
                nested_slot = _get_field(raw_slot, "spec")
            slot_spec = nested_slot if nested_slot is not None else raw_slot

        slot_required = bool(_get_field(slot_spec, "required", False))
        slot_default_raw = _get_field(slot_spec, "default")
        slot_description_raw = _get_field(slot_spec, "description")
        has_default = slot_default_raw is not None and slot_default_raw != ""
        return cls(
            name=str(raw_slot_name) if raw_slot_name is not None else "",
            required=slot_required,
            required_label="Required" if slot_required else "Optional",
            required_variant="error" if slot_required else "neutral",
            has_default=has_default,
            default_display=str(slot_default_raw) if has_default else empty_placeholder,
            description=(
                str(slot_description_raw) if slot_description_raw else empty_placeholder
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a dictionary representation for template contexts."""
        return {
            "name": self.name,
            "required": self.required,
            "required_label": self.required_label,
            "required_variant": self.required_variant,
            "has_default": self.has_default,
            "default_display": self.default_display,
            "description": self.description,
        }

    def __getitem__(self, key: str) -> Any:
        return self.to_dict()[key]


@dataclass(frozen=True)
class NavItemInputData:
    """Normalized navigation node input fields shared by ``NavTree`` and ``FolderListing``."""

    label: str
    slug: str
    node_type: str
    url: str
    active_path: str
    base_active_path: str
    children: list[Any]
    icon: str
    is_component: bool | None
    is_document: bool | None
    is_variant: bool | None
    has_children: bool | None
    has_index_doc: bool
    child_count: int | None

    @classmethod
    def from_raw(
        cls,
        raw_node: Any,
        *,
        default_label_from_name: bool = False,
        default_url: str = "#",
    ) -> NavItemInputData:
        """Extract normalized attributes from a ``NavNode``, dict, or duck-typed object."""
        raw_label = _get_field(raw_node, "label")
        if raw_label is None:
            if default_label_from_name:
                raw_label = _get_field(
                    raw_node,
                    "name",
                    "" if isinstance(raw_node, dict) else str(raw_node),
                )
            else:
                raw_label = ""
        raw_slug = _get_field(raw_node, "slug", "")
        raw_type = (
            _get_field(raw_node, "node_type")
            or _get_field(raw_node, "type")
            or _get_field(raw_node, "node_kind")
            or ""
        )
        raw_url = _get_field(raw_node, "url") or _get_field(raw_node, "href")
        raw_active = _get_field(raw_node, "active_path", "")
        raw_base_active = _get_field(raw_node, "base_active_path", "")
        raw_children_val = _get_field(raw_node, "children")
        raw_icon = _get_field(raw_node, "icon")
        raw_is_component = _get_field(raw_node, "is_component")
        raw_is_document = _get_field(raw_node, "is_document")
        raw_is_variant = _get_field(raw_node, "is_variant")
        raw_has_children = _get_field(raw_node, "has_children")
        raw_has_index_doc = _get_field(raw_node, "has_index_doc")
        if raw_has_index_doc is None:
            raw_has_index_doc = _get_field(raw_node, "index_doc_path") is not None
        raw_child_count = _get_field(raw_node, "child_count")

        node_type_val = getattr(raw_type, "value", raw_type)
        node_type = str(node_type_val).lower() if node_type_val else ""

        children = (
            list(raw_children_val)
            if isinstance(raw_children_val, (list, tuple, set))
            else (list(raw_children_val) if raw_children_val is not None else [])
        )
        child_count = (
            max(0, raw_child_count)
            if isinstance(raw_child_count, int)
            and not isinstance(raw_child_count, bool)
            else None
        )
        return cls(
            label=str(raw_label) if raw_label is not None else "",
            slug=str(raw_slug) if raw_slug is not None else "",
            node_type=node_type,
            url=str(raw_url) if raw_url else default_url,
            active_path=str(raw_active) if raw_active else "",
            base_active_path=str(raw_base_active) if raw_base_active else "",
            children=children,
            icon=str(raw_icon) if raw_icon else "",
            is_component=bool(raw_is_component)
            if raw_is_component is not None
            else None,
            is_document=bool(raw_is_document) if raw_is_document is not None else None,
            is_variant=bool(raw_is_variant) if raw_is_variant is not None else None,
            has_children=bool(raw_has_children)
            if raw_has_children is not None
            else None,
            has_index_doc=bool(raw_has_index_doc),
            child_count=child_count,
        )
