"""Core enums and immutable value types for dj-design-system."""

from __future__ import annotations

import copy
import enum
from collections.abc import Callable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any, Generic, Literal, TypeAlias, TypedDict, TypeVar


K = TypeVar("K")
V = TypeVar("V")


class FrozenMapping(Mapping[K, V], Generic[K, V]):
    """Immutable mapping wrapper safe under ``copy.deepcopy``, ``pickle``, and ``asdict``."""

    __slots__ = ("_data",)

    def __init__(self, data: Mapping[K, V] | None = None) -> None:
        self._data: dict[K, V] = dict(data) if data is not None else {}

    def __getitem__(self, key: K) -> V:
        return self._data[key]

    def __iter__(self) -> Iterator[K]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"FrozenMapping({self._data!r})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, FrozenMapping):
            return self._data == other._data
        if isinstance(other, Mapping):
            return self._data == dict(other)
        return NotImplemented

    def __deepcopy__(self, memo: dict[int, Any]) -> FrozenMapping[K, V]:
        return FrozenMapping(copy.deepcopy(self._data, memo))

    def __reduce__(self) -> tuple[type[FrozenMapping[K, V]], tuple[dict[K, V]]]:
        return (FrozenMapping, (dict(self._data),))


class HtmlAttrsDict(TypedDict, total=False):
    """Canvas document attribute overrides for ``<html>`` and ``<body>`` tags."""

    html: Mapping[str, str | None]
    body: Mapping[str, str | None]


HtmlAttrsInput: TypeAlias = HtmlAttrsDict | Mapping[str, Mapping[str, str | None]]
WebpackBundleSpec: TypeAlias = str | tuple[str] | tuple[str, str]


def freeze_html_attrs(
    raw: HtmlAttrsInput | None,
) -> FrozenMapping[str, FrozenMapping[str, str | None]]:
    """Convert a nested ``html_attrs`` mapping into deeply frozen mappings."""
    if raw is None:
        return FrozenMapping()
    if not isinstance(raw, Mapping):
        raise TypeError(
            f"html_attrs must be a mapping or None, got {type(raw).__name__}."
        )
    frozen: dict[str, FrozenMapping[str, str | None]] = {}
    for target, attrs in raw.items():
        if not isinstance(target, str):
            raise TypeError(f"html_attrs target key must be a str, got {target!r}.")
        if not isinstance(attrs, Mapping):
            raise TypeError(
                f"html_attrs[{target!r}] must be a mapping, got {type(attrs).__name__}."
            )
        normalised: dict[str, str | None] = {}
        for attr_name, attr_val in attrs.items():
            if not isinstance(attr_name, str):
                raise TypeError(
                    f"html_attrs[{target!r}] attribute name must be a str, got {attr_name!r}."
                )
            if attr_val is not None and not isinstance(attr_val, str):
                normalised[attr_name] = str(attr_val)
            else:
                normalised[attr_name] = attr_val
        frozen[target] = FrozenMapping(normalised)
    return FrozenMapping(frozen)


def coerce_str_tuple(
    value: str | Sequence[str] | None, *, field_name: str
) -> tuple[str, ...]:
    """Normalise a string or sequence of strings into an immutable tuple."""
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return tuple(str(item) for item in value)
    raise TypeError(f"{field_name} must be a string or sequence of strings.")


def coerce_bundle_tuple(
    value: Sequence[WebpackBundleSpec] | None, *, field_name: str
) -> tuple[WebpackBundleSpec, ...]:
    """Normalise webpack bundle specs into an immutable tuple, rejecting bare strings."""
    if value is None:
        return ()
    if isinstance(value, (str, bytes, bytearray)):
        raise TypeError(
            f"{field_name} must be a sequence of bundle specs, not a bare string."
        )
    if not isinstance(value, Sequence):
        raise TypeError(f"{field_name} must be a sequence of bundle specs.")
    normalised: list[WebpackBundleSpec] = []
    for item in value:
        if isinstance(item, str):
            normalised.append(item)
        elif isinstance(item, Sequence) and not isinstance(item, (bytes, bytearray)):
            items = tuple(str(part) for part in item)
            if len(items) == 1:
                normalised.append((items[0],))
            elif len(items) == 2:
                normalised.append((items[0], items[1]))
            else:
                raise ValueError(
                    f"Invalid bundle spec in {field_name}: expected 1 or 2 items, got {len(items)}."
                )
        else:
            raise TypeError(f"Invalid bundle spec in {field_name}: {item!r}.")
    return tuple(normalised)


class DocVariantStrategy(str, enum.Enum):
    """Built-in parameter and slot generation strategies for standard documentation variants."""

    MINIMAL = "minimal"
    MAXIMAL = "maximal"
    DEFAULTS = "defaults"
    ALL_SLOTS = "all_slots"
    CUSTOM = "custom"


@dataclass(frozen=True)
class DocVariantConfig:
    """Normalized configuration for a standard documentation variant.

    Attributes:
        key: Identifier key in ``doc_variants`` (e.g. ``"minimal"``, ``"maximal"``).
        name: Variant slug matched against ``GalleryConfig.variants`` (e.g. ``"basic"``, ``"maximal"``).
        label: Heading label displayed in the Usage documentation section.
        strategy: Built-in generation strategy used when the variant is not overridden in ``gallery.py``.
        show_in_docs: Whether this variant is included in component documentation by default.
        kwargs: Optional static parameter overrides for custom global variants.
        param_factory: Reserved hook for custom parameter value factory callables.
        slot_factory: Reserved hook for custom slot content factory callables.
    """

    key: str = ""
    name: str = ""
    label: str = ""
    strategy: DocVariantStrategy = DocVariantStrategy.MINIMAL
    show_in_docs: bool = True
    kwargs: Mapping[str, Any] = field(default_factory=FrozenMapping)
    param_factory: Callable[..., Any] | None = None
    slot_factory: Callable[..., Any] | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.kwargs, FrozenMapping):
            object.__setattr__(self, "kwargs", FrozenMapping(self.kwargs))


class NodeType(str, enum.Enum):
    """Discriminates the kind of navigation node."""

    APP = "app"
    FOLDER = "folder"
    COMPONENT = "component"
    DOCUMENT = "document"
    VARIANT = "variant"


NavOrderSpec: TypeAlias = tuple[NodeType | str, ...] | Literal["alphabetical"]


class TagType(str, enum.Enum):
    """The type of template tag a component should be registered as."""

    TAG = "tag"
    BLOCK = "block"


class CanvasMode(str, enum.Enum):
    """Rendering mode for a canvas instance."""

    BASIC = "basic"
    EXTENDED = "extended"


class FlattenStrategy(str, enum.Enum):
    """Strategy for flattening nested folder structures in component resolution."""

    NONE = "none"
    ALL = "all"
    LEAF = "leaf"


class ColorScheme(str, enum.Enum):
    """W3C color scheme values."""

    LIGHT = "light"
    DARK = "dark"


@dataclass(frozen=True)
class CanvasBackground:
    """Preview canvas background colour and display label."""

    color: str
    label: str = ""


def coerce_canvas_background(
    value: str | CanvasBackground | Mapping[str, Any] | None,
) -> str | CanvasBackground | None:
    """Coerce a raw background mapping into a ``CanvasBackground``."""
    if value is None or isinstance(value, (str, CanvasBackground)):
        return value
    if isinstance(value, Mapping):
        return CanvasBackground(
            color=str(value.get("color", "")),
            label=str(value.get("label", "")),
        )
    raise TypeError(
        f"canvas_background must be a slug string, CanvasBackground, mapping, or None; got {type(value).__name__}."
    )


@dataclass(frozen=True)
class DarkModeConfig:
    """Explicit configuration for how a theme activates dark mode."""

    html_attrs: HtmlAttrsInput = field(default_factory=FrozenMapping)
    css: Sequence[str] = ()
    js: Sequence[str] = ()
    css_bundles: Sequence[WebpackBundleSpec] = ()
    js_bundles: Sequence[WebpackBundleSpec] = ()
    canvas_background: str | CanvasBackground | Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "html_attrs", freeze_html_attrs(self.html_attrs))
        object.__setattr__(self, "css", coerce_str_tuple(self.css, field_name="css"))
        object.__setattr__(self, "js", coerce_str_tuple(self.js, field_name="js"))
        object.__setattr__(
            self,
            "css_bundles",
            coerce_bundle_tuple(self.css_bundles, field_name="css_bundles"),
        )
        object.__setattr__(
            self,
            "js_bundles",
            coerce_bundle_tuple(self.js_bundles, field_name="js_bundles"),
        )
        object.__setattr__(
            self,
            "canvas_background",
            coerce_canvas_background(self.canvas_background),
        )


@dataclass(frozen=True)
class Theme:
    """Immutable configuration for a consumer or gallery UI theme."""

    value: str = ""
    label: str = ""
    html_attrs: HtmlAttrsInput = field(default_factory=FrozenMapping)
    css: Sequence[str] = ()
    js: Sequence[str] = ()
    css_bundles: Sequence[WebpackBundleSpec] = ()
    js_bundles: Sequence[WebpackBundleSpec] = ()
    canvas_background: str | CanvasBackground | Mapping[str, Any] | None = None
    dark_mode: DarkModeConfig | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "html_attrs", freeze_html_attrs(self.html_attrs))
        object.__setattr__(self, "css", coerce_str_tuple(self.css, field_name="css"))
        object.__setattr__(self, "js", coerce_str_tuple(self.js, field_name="js"))
        object.__setattr__(
            self,
            "css_bundles",
            coerce_bundle_tuple(self.css_bundles, field_name="css_bundles"),
        )
        object.__setattr__(
            self,
            "js_bundles",
            coerce_bundle_tuple(self.js_bundles, field_name="js_bundles"),
        )
        object.__setattr__(
            self,
            "canvas_background",
            coerce_canvas_background(self.canvas_background),
        )
        if isinstance(self.dark_mode, Mapping):
            object.__setattr__(
                self,
                "dark_mode",
                DarkModeConfig(
                    html_attrs=self.dark_mode.get("html_attrs", {}),
                    css=self.dark_mode.get("css", ()),
                    js=self.dark_mode.get("js", ()),
                    css_bundles=self.dark_mode.get("css_bundles", ()),
                    js_bundles=self.dark_mode.get("js_bundles", ()),
                    canvas_background=self.dark_mode.get("canvas_background"),
                ),
            )
        elif self.dark_mode is not None and not isinstance(
            self.dark_mode, DarkModeConfig
        ):
            raise TypeError(
                f"dark_mode must be a DarkModeConfig, mapping, or None; got {type(self.dark_mode).__name__}."
            )

    @property
    def supports_dark_mode(self) -> bool:
        """Return True if this theme explicitly configures dark mode support."""
        return self.dark_mode is not None

    @property
    def has_dark_mode_assets(self) -> bool:
        """Return True if this theme's dark mode loads external CSS or JS assets."""
        return bool(
            self.dark_mode
            and (
                self.dark_mode.css
                or self.dark_mode.js
                or self.dark_mode.css_bundles
                or self.dark_mode.js_bundles
            )
        )

    @property
    def has_external_assets(self) -> bool:
        """Return True if this theme loads external CSS or JS assets."""
        return bool(
            self.css
            or self.js
            or self.css_bundles
            or self.js_bundles
            or self.has_dark_mode_assets
        )
