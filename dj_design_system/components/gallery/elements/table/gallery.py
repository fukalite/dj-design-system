"""Gallery configuration and variants for the built-in table component."""

from django.utils import safestring

from dj_design_system import gallery


DEFAULT_HEAD = safestring.mark_safe(
    s=(
        "<tr>"
        '<th scope="col">Parameter</th>'
        '<th scope="col">Type</th>'
        '<th scope="col">Description</th>'
        "</tr>"
    )
)

DEFAULT_BODY = safestring.mark_safe(
    s=(
        "<tr>"
        "<td>caption</td>"
        "<td>str</td>"
        "<td>Optional accessible table caption.</td>"
        "</tr>"
        "<tr>"
        "<td>density</td>"
        "<td>str</td>"
        "<td>Row padding density (compact or default).</td>"
        "</tr>"
    )
)

DEFAULT_FOOT = safestring.mark_safe(
    s=('<tr><th scope="row">Total</th><td>2 parameters</td><td></td></tr>')
)

config = gallery.GalleryConfig(
    param_defaults={
        "caption": "Component Parameters",
        "slot__head": DEFAULT_HEAD,
        "slot__body": DEFAULT_BODY,
        "slot__foot": "",
    },
)
