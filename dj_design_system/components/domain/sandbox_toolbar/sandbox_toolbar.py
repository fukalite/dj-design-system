"""Built-in interactive sandbox toolbar domain component for the dds gallery."""

import typing

from dj_design_system import components, parameters


DEFAULT_ACTIVE_VARIANT = ""
DEFAULT_COMPONENT_URL = ""
DEFAULT_ACTIVE_BACKGROUND = "white"
DEFAULT_ACTIVE_VIEWPORT = "responsive"
DEFAULT_ACTIVE_ZOOM = "100"
DEFAULT_ARIA_LABEL = "Sandbox controls"
DEFAULT_VARIANT_LABEL = "Default"

DEFAULT_BACKGROUNDS: tuple[tuple[str, str], ...] = (
    ("white", "White"),
    ("light", "Light"),
    ("dark", "Dark"),
)

DEFAULT_VIEWPORTS: tuple[tuple[str, str], ...] = (
    ("responsive", "Responsive"),
    ("320", "Small mobile — 320px"),
    ("414", "Large mobile — 414px"),
    ("768", "Tablet — 768px"),
    ("1024", "Desktop — 1024px"),
    ("1920", "Full HD — 1920px"),
    ("2560", "Ultrawide — 2560px"),
)

DEFAULT_ZOOM_LEVELS: tuple[str, ...] = (
    "50",
    "75",
    "100",
    "125",
    "150",
    "200",
)


class SandboxToolbar(components.TagComponent):
    """Sandbox preview toolbar composing popout selectors and inspection toggles.

    Renders a ``<div class="dds-sandbox-toolbar" data-surface="sandbox"
    role="toolbar">`` container using Every Layout ``<l-cluster>`` composition
    and delegating controls to ``{% dds__popout %}``, ``{% dds__popout_option %}``,
    and ``{% dds__button %}``:

    - Optional variant preset selector (``[data-sandbox-control="variant"]``)
      when ``variants`` is non-empty.
    - Canvas background selector (``[data-sandbox-control="background"]``).
    - Viewport width preset selector (``[data-sandbox-control="viewport"]``).
    - Zoom percentage selector (``[data-sandbox-control="zoom"]``).
    - Inspection toggle and action group (``[data-sandbox-toggles]``) with box
      model outline, measurement overlay, RTL direction, optional parameter
      reset, and optional standalone canvas link.

    Args:
        variants: Optional list of ``Variant`` instances or dicts with ``name``
            and ``label``.
        active_variant: Currently active variant name or ``Variant`` instance.
        component_url: Base component URL for variant switching.
        backgrounds: Available canvas background dicts with ``value``, ``label``,
            and optional ``color``.
        active_background: Currently active background identifier.
        viewports: Optional viewport preset dicts with ``value`` and ``label``.
        active_viewport: Currently active viewport preset value.
        zoom_levels: Optional zoom percentage presets.
        active_zoom: Currently active zoom level.
        outline_active: Whether box model outline is initially enabled.
        measure_active: Whether measurement overlay is initially enabled.
        rtl_active: Whether RTL direction is initially enabled.
        canvas_url: Optional standalone canvas URL for opening in a new tab.
        reset_url: Optional URL to reset sandbox parameters.
        aria_label: Accessible toolbar label.

    Example usage::

        {% dds__sandbox_toolbar variants=variants active_variant="primary" component_url="/gallery/button/" %}

        {% dds__sandbox_toolbar active_background="dark" active_viewport="768" outline_active=True canvas_url="/canvas/button/" %}
    """

    variants = parameters.ListParam(
        description="Optional list of Variant instances or dicts with 'name' and 'label'.",
        default=None,
        required=False,
    )
    active_variant = parameters.StrParam(
        description="Currently active variant name or Variant instance.",
        default=DEFAULT_ACTIVE_VARIANT,
        required=False,
    )
    component_url = parameters.StrParam(
        description="Base component URL for variant switching.",
        default=DEFAULT_COMPONENT_URL,
        required=False,
    )
    backgrounds = parameters.ListParam(
        description="Available canvas background dicts with 'value', 'label', and optional 'color'.",
        default=None,
        required=False,
    )
    active_background = parameters.StrParam(
        description="Currently active background identifier.",
        default=DEFAULT_ACTIVE_BACKGROUND,
        required=False,
    )
    viewports = parameters.ListParam(
        description="Optional viewport preset dicts with 'value' and 'label'.",
        default=None,
        required=False,
    )
    active_viewport = parameters.StrParam(
        description="Currently active viewport preset value.",
        default=DEFAULT_ACTIVE_VIEWPORT,
        required=False,
    )
    zoom_levels = parameters.ListParam(
        description="Optional zoom percentage presets.",
        default=None,
        required=False,
    )
    active_zoom = parameters.StrParam(
        description="Currently active zoom level.",
        default=DEFAULT_ACTIVE_ZOOM,
        required=False,
    )
    outline_active = parameters.BoolParam(
        description="Whether box model outline is initially enabled.",
        default=False,
        required=False,
    )
    measure_active = parameters.BoolParam(
        description="Whether measurement overlay is initially enabled.",
        default=False,
        required=False,
    )
    rtl_active = parameters.BoolParam(
        description="Whether RTL direction is initially enabled.",
        default=False,
        required=False,
    )
    canvas_url = parameters.StrParam(
        description="Optional standalone canvas URL for opening in a new tab.",
        default="",
        required=False,
    )
    reset_url = parameters.StrParam(
        description="Optional URL to reset sandbox parameters.",
        default="",
        required=False,
    )
    aria_label = parameters.StrParam(
        description="Accessible toolbar label.",
        default=DEFAULT_ARIA_LABEL,
        required=False,
    )

    def __init__(self, **kwargs: typing.Any) -> None:
        """Initialise the sandbox toolbar, normalising non-string active variant and zoom inputs.

        Args:
            **kwargs: Component parameter keyword arguments.
        """
        if (
            "active_variant" in kwargs
            and kwargs["active_variant"] is not None
            and not isinstance(kwargs["active_variant"], str)
        ):
            kwargs["active_variant"] = str(
                getattr(
                    kwargs["active_variant"],
                    "name",
                    kwargs["active_variant"],
                )
            )
        if (
            "active_zoom" in kwargs
            and kwargs["active_zoom"] is not None
            and not isinstance(kwargs["active_zoom"], str)
        ):
            kwargs["active_zoom"] = str(kwargs["active_zoom"])
        super().__init__(**kwargs)

    def get_context(self) -> dict[str, typing.Any]:
        """Compute normalized variants, backgrounds, viewports, zoom levels, and toggle flags.

        Returns:
            Dictionary containing normalized option lists, active labels, and
            boolean state flags for rendering ``sandbox_toolbar.html``.
        """
        context = super().get_context()
        raw_variants = list(self.variants) if self.variants is not None else []
        resolved_active_variant = (
            str(self.active_variant) if self.active_variant else ""
        )
        base_url = str(self.component_url) if self.component_url else ""

        normalized_variants: list[dict[str, typing.Any]] = []
        active_variant_label = DEFAULT_VARIANT_LABEL

        for raw_variant in raw_variants:
            if isinstance(raw_variant, str):
                raw_name: typing.Any = raw_variant
                raw_label: typing.Any = (
                    raw_variant.capitalize()
                    if raw_variant.islower()
                    else raw_variant
                )
                raw_href: typing.Any = None
            elif isinstance(raw_variant, dict):
                raw_name = raw_variant.get("name")
                raw_label = raw_variant.get("label")
                raw_href = raw_variant.get("href")
            else:
                raw_name = getattr(raw_variant, "name", None)
                raw_label = getattr(raw_variant, "label", None)
                raw_href = getattr(raw_variant, "href", None)

            name = str(raw_name) if raw_name is not None else ""
            if raw_label is not None:
                label = str(raw_label)
            elif name:
                label = name.capitalize() if name.islower() else name
            else:
                label = DEFAULT_VARIANT_LABEL

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

            is_selected = bool(resolved_active_variant) and (
                name == resolved_active_variant
            )
            if is_selected:
                active_variant_label = label

            normalized_variants.append(
                {
                    "name": name,
                    "label": label,
                    "href": href,
                    "is_selected": is_selected,
                }
            )

        raw_backgrounds: list[typing.Any] = (
            list(self.backgrounds)
            if self.backgrounds is not None
            else list(DEFAULT_BACKGROUNDS)
        )
        extracted_backgrounds: list[tuple[str, str]] = []
        for raw_bg in raw_backgrounds:
            if isinstance(raw_bg, tuple | list) and len(raw_bg) >= 2:
                bg_value = str(raw_bg[0])
                bg_label = str(raw_bg[1])
            elif isinstance(raw_bg, str):
                bg_value = raw_bg
                bg_label = raw_bg.capitalize() if raw_bg.islower() else raw_bg
            elif isinstance(raw_bg, dict):
                raw_bg_value = raw_bg.get("value")
                raw_bg_label = raw_bg.get("label")
                bg_value = str(raw_bg_value) if raw_bg_value is not None else ""
                bg_label = (
                    str(raw_bg_label)
                    if raw_bg_label is not None
                    else (
                        bg_value.capitalize()
                        if bg_value.islower()
                        else bg_value
                    )
                )
            else:
                raw_bg_value = getattr(raw_bg, "value", None)
                raw_bg_label = getattr(raw_bg, "label", None)
                bg_value = str(raw_bg_value) if raw_bg_value is not None else ""
                bg_label = (
                    str(raw_bg_label)
                    if raw_bg_label is not None
                    else (
                        bg_value.capitalize()
                        if bg_value.islower()
                        else bg_value
                    )
                )
            extracted_backgrounds.append((bg_value, bg_label))

        bg_values = [val for val, _ in extracted_backgrounds]
        if self.active_background and str(self.active_background) in bg_values:
            resolved_background = str(self.active_background)
        elif extracted_backgrounds:
            resolved_background = extracted_backgrounds[0][0]
        else:
            resolved_background = str(
                self.active_background or DEFAULT_ACTIVE_BACKGROUND
            )

        normalized_backgrounds: list[dict[str, typing.Any]] = []
        active_background_label = (
            resolved_background.capitalize()
            if resolved_background.islower()
            else resolved_background
        )
        for bg_value, bg_label in extracted_backgrounds:
            is_bg_selected = bg_value == resolved_background
            if is_bg_selected:
                active_background_label = bg_label
            normalized_backgrounds.append(
                {
                    "value": bg_value,
                    "label": bg_label,
                    "is_selected": is_bg_selected,
                }
            )

        raw_viewports: list[typing.Any] = (
            list(self.viewports)
            if self.viewports is not None
            else list(DEFAULT_VIEWPORTS)
        )
        extracted_viewports: list[tuple[str, str]] = []
        for raw_vp in raw_viewports:
            if isinstance(raw_vp, tuple | list) and len(raw_vp) >= 2:
                vp_value = str(raw_vp[0])
                vp_label = str(raw_vp[1])
            elif isinstance(raw_vp, str):
                vp_value = raw_vp
                vp_label = raw_vp.capitalize() if raw_vp.islower() else raw_vp
            elif isinstance(raw_vp, dict):
                raw_vp_value = raw_vp.get("value")
                raw_vp_label = raw_vp.get("label")
                vp_value = str(raw_vp_value) if raw_vp_value is not None else ""
                vp_label = (
                    str(raw_vp_label)
                    if raw_vp_label is not None
                    else (
                        vp_value.capitalize()
                        if vp_value.islower()
                        else vp_value
                    )
                )
            else:
                raw_vp_value = getattr(raw_vp, "value", None)
                raw_vp_label = getattr(raw_vp, "label", None)
                vp_value = str(raw_vp_value) if raw_vp_value is not None else ""
                vp_label = (
                    str(raw_vp_label)
                    if raw_vp_label is not None
                    else (
                        vp_value.capitalize()
                        if vp_value.islower()
                        else vp_value
                    )
                )
            extracted_viewports.append((vp_value, vp_label))

        vp_values = [val for val, _ in extracted_viewports]
        if self.active_viewport and str(self.active_viewport) in vp_values:
            resolved_viewport = str(self.active_viewport)
        elif extracted_viewports:
            resolved_viewport = extracted_viewports[0][0]
        else:
            resolved_viewport = str(
                self.active_viewport or DEFAULT_ACTIVE_VIEWPORT
            )

        normalized_viewports: list[dict[str, typing.Any]] = []
        active_viewport_label = (
            resolved_viewport.capitalize()
            if resolved_viewport.islower()
            else resolved_viewport
        )
        for vp_value, vp_label in extracted_viewports:
            is_vp_selected = vp_value == resolved_viewport
            if is_vp_selected:
                active_viewport_label = vp_label
            normalized_viewports.append(
                {
                    "value": vp_value,
                    "label": vp_label,
                    "is_selected": is_vp_selected,
                }
            )

        raw_zoom_levels: list[typing.Any] = (
            list(self.zoom_levels)
            if self.zoom_levels is not None
            else list(DEFAULT_ZOOM_LEVELS)
        )
        extracted_zooms: list[tuple[str, str]] = []
        for raw_zoom in raw_zoom_levels:
            if isinstance(raw_zoom, tuple | list) and len(raw_zoom) >= 2:
                zoom_value = str(raw_zoom[0]).rstrip("%")
                zoom_label = str(raw_zoom[1])
            elif isinstance(raw_zoom, dict):
                raw_zoom_val = raw_zoom.get("value")
                raw_zoom_lbl = raw_zoom.get("label")
                zoom_value = (
                    str(raw_zoom_val).rstrip("%")
                    if raw_zoom_val is not None
                    else ""
                )
                zoom_label = (
                    str(raw_zoom_lbl)
                    if raw_zoom_lbl is not None
                    else f"{zoom_value}%"
                )
            else:
                zoom_value = str(raw_zoom).rstrip("%")
                zoom_label = f"{zoom_value}%"
            extracted_zooms.append((zoom_value, zoom_label))

        raw_active_zoom = (
            str(self.active_zoom).rstrip("%")
            if self.active_zoom
            else DEFAULT_ACTIVE_ZOOM
        )
        zoom_values = [val for val, _ in extracted_zooms]
        if raw_active_zoom in zoom_values:
            resolved_zoom = raw_active_zoom
        elif extracted_zooms:
            resolved_zoom = extracted_zooms[0][0]
        else:
            resolved_zoom = raw_active_zoom

        normalized_zoom_levels: list[dict[str, typing.Any]] = []
        for zoom_value, zoom_label in extracted_zooms:
            is_zoom_selected = zoom_value == resolved_zoom
            normalized_zoom_levels.append(
                {
                    "value": zoom_value,
                    "label": zoom_label,
                    "is_selected": is_zoom_selected,
                }
            )

        active_zoom_label = f"{resolved_zoom}%"
        canvas_url = str(self.canvas_url) if self.canvas_url else ""
        reset_url = str(self.reset_url) if self.reset_url else ""
        resolved_aria_label = (
            str(self.aria_label) if self.aria_label else DEFAULT_ARIA_LABEL
        )

        context["active_variant"] = resolved_active_variant
        context["active_background"] = resolved_background
        context["active_viewport"] = resolved_viewport
        context["active_zoom"] = resolved_zoom
        context["normalized_variants"] = normalized_variants
        context["active_variant_label"] = active_variant_label
        context["normalized_backgrounds"] = normalized_backgrounds
        context["active_background_label"] = active_background_label
        context["normalized_viewports"] = normalized_viewports
        context["active_viewport_label"] = active_viewport_label
        context["normalized_zoom_levels"] = normalized_zoom_levels
        context["active_zoom_label"] = active_zoom_label
        context["has_variants"] = bool(normalized_variants)
        context["canvas_url"] = canvas_url
        context["reset_url"] = reset_url
        context["has_canvas_url"] = bool(canvas_url)
        context["has_reset_url"] = bool(reset_url)
        context["outline_active"] = bool(self.outline_active)
        context["measure_active"] = bool(self.measure_active)
        context["rtl_active"] = bool(self.rtl_active)
        context["resolved_aria_label"] = resolved_aria_label
        context["aria_label"] = resolved_aria_label
        return context
