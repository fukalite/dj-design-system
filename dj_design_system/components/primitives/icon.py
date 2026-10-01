from django.utils.safestring import mark_safe

from dj_design_system.components import TagComponent
from dj_design_system.parameters import IntParam, StrParam
from dj_design_system.services.media import FOUNDATION_CSS


#: Inline SVG icons: name -> (inner markup, uses round line caps and joins).
SVG_ICONS: dict[str, tuple[str, bool]] = {
    "external-link": (
        '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />'
        '<polyline points="15 3 21 3 21 9" />'
        '<line x1="10" y1="14" x2="21" y2="3" />',
        True,
    ),
    "eye": (
        '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />'
        '<circle cx="12" cy="12" r="3" />',
        True,
    ),
    "code": (
        '<polyline points="16 18 22 12 16 6" /><polyline points="8 6 2 12 8 18" />',
        True,
    ),
    "file-code": (
        '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />'
        '<polyline points="14 2 14 8 20 8" />'
        '<polyline points="10 13 8 15 10 17" />'
        '<polyline points="14 13 16 15 14 17" />',
        True,
    ),
    "monitor": (
        '<rect x="2" y="3" width="20" height="14" rx="2" />'
        '<line x1="8" y1="21" x2="16" y2="21" />'
        '<line x1="12" y1="17" x2="12" y2="21" />',
        False,
    ),
    "box-model": (
        '<rect x="1" y="1" width="22" height="22" rx="2" stroke-dasharray="4 2" />'
        '<rect x="5" y="5" width="14" height="14" rx="1" />'
        '<rect x="9" y="9" width="6" height="6" rx="0.5" fill="currentColor"'
        ' opacity="0.3" />',
        False,
    ),
    "ruler": (
        '<path d="M2 2v20h20" /><path d="M6 18V8" /><path d="M4 8h4" />'
        '<path d="M4 18h4" /><path d="M10 18h8" /><path d="M10 16v4" />'
        '<path d="M18 16v4" />',
        False,
    ),
    "rtl": (
        '<path d="M10 5v14" /><path d="M14 5v14" />'
        '<path d="M14 5h2a4 4 0 0 1 0 8h-2" /><path d="M7 15l-3-3 3-3" />',
        False,
    ),
}

#: Icons drawn with a CSS mask from the ``--gallery-icon-*`` tokens.
MASK_ICONS = (
    "component",
    "component-variants",
    "doc",
    "folder",
    "folder-open",
    "variant",
)

ICON_NAMES = [*SVG_ICONS, *MASK_ICONS]


class Icon(TagComponent):
    """A decorative gallery icon.

    Line icons render as inline SVG sized in pixels. Node-type icons
    (``component``, ``component-variants``, ``doc``, ``folder``,
    ``folder-open``, ``variant``) render as a span
    masked with the ``--gallery-icon-*`` tokens, coloured by ``currentColor``.
    Icons are always hidden from assistive technology: give the surrounding
    control an accessible label instead.

    Use ``extra_classes`` to add a context's own classes, which that
    context's stylesheet can use to size or colour the icon.

    Example usage::

        {% dds__primitives__icon "external-link" %}
        {% dds__primitives__icon "folder" extra_classes="gallery-nav__icon" %}
    """

    template_name = "dj_design_system/ui/primitives/icon.html"

    name = StrParam("Which icon to draw.", choices=ICON_NAMES)
    size = IntParam(
        "Width and height in pixels. Defaults to 14 for line icons; mask icons"
        " take their size from CSS.",
        required=False,
    )
    extra_classes = StrParam("Extra CSS classes.", required=False)

    class Meta:
        positional_args = ["name"]

    class Media:
        css = [FOUNDATION_CSS, "dj_design_system/ui/primitives/icon.css"]

    def get_context(self):
        context = super().get_context()
        is_svg = self.name in SVG_ICONS
        classes = ["gallery-icon"]
        if not is_svg:
            classes.append("gallery-icon--mask")
        classes.append(f"gallery-icon--{self.name}")
        if self.extra_classes:
            classes.append(self.extra_classes)
        context["icon_classes"] = " ".join(classes)
        if is_svg:
            markup, rounded = SVG_ICONS[str(self.name)]
            context["svg"] = mark_safe(markup)  # noqa: S308 - constant markup
            context["rounded"] = rounded
            context["px"] = self.size or 14
        return context
