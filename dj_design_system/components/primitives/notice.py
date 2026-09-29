from dj_design_system.components import BlockComponent
from dj_design_system.parameters import BoolParam, StrParam
from dj_design_system.services.media import FOUNDATION_CSS


#: Variant -> BEM class.
VARIANT_CLASSES = {
    "warning": "gallery-static-snapshot-notice",
    "hint": "gallery-debug-hint",
}


class Notice(BlockComponent):
    """A boxed message: a yellow ``warning`` or a quiet, dashed ``hint``.

    ``snapshot=True`` makes a warning the static snapshot notice: it stays
    hidden until its script finds the gallery is being viewed away from
    ``localhost``, i.e. as a published static snapshot.

    Example usage::

        {% dds__primitives__notice variant="hint" %}
            <p>Add an <code>index.md</code> file to this folder.</p>
        {% enddds__primitives__notice %}
    """

    template_name = "dj_design_system/ui/primitives/notice.html"

    variant = StrParam(
        "Visual style.",
        required=False,
        default="warning",
        choices=list(VARIANT_CLASSES),
    )
    snapshot = BoolParam(
        "Show only on a published static snapshot. Warning variant only.",
        required=False,
        default=False,
    )

    class Media:
        css = [FOUNDATION_CSS, "dj_design_system/ui/primitives/notice.css"]
        js = "dj_design_system/ui/primitives/notice.js"

    def validate_params(self) -> None:
        if self.snapshot and self.variant != "warning":
            raise ValueError("Notice 'snapshot' only applies to the warning variant.")

    def get_context(self):
        context = super().get_context()
        context["notice_class"] = VARIANT_CLASSES[str(self.variant)]
        return context
