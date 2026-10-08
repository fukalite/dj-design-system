"""Gallery configuration and variants for the built-in table component."""

from django.utils.safestring import mark_safe

from dj_design_system.gallery import GalleryConfig, Variant


DEFAULT_HEAD = mark_safe(
    s=(
        "<tr>"
        '<th scope="col">Parameter</th>'
        '<th scope="col">Type</th>'
        '<th scope="col">Description</th>'
        "</tr>"
    )
)

DEFAULT_BODY = mark_safe(
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

config = GalleryConfig(
    variants=[
        Variant(
            name="basic",
            label="Default Table",
            description="Standard table with header and body rows.",
            kwargs={
                "slot__head": DEFAULT_HEAD,
                "slot__body": DEFAULT_BODY,
            },
        ),
        Variant(
            name="compact",
            label="Compact Density with Caption",
            description="Dense row padding with an accessible table caption.",
            kwargs={
                "caption": "Table component parameters",
                "density": "compact",
                "slot__head": DEFAULT_HEAD,
                "slot__body": DEFAULT_BODY,
            },
        ),
        Variant(
            name="body_only",
            label="Body Only",
            description="Table rendered without the optional head slot.",
            kwargs={
                "slot__body": DEFAULT_BODY,
            },
        ),
    ],
)
