"""Built-in accessible tooltip element component."""

import typing

from dj_design_system import components, parameters


PLACEMENT_TOP = "top"
PLACEMENT_BOTTOM = "bottom"
PLACEMENT_LEFT = "left"
PLACEMENT_RIGHT = "right"
PLACEMENT_CHOICES: tuple[str, ...] = (
    PLACEMENT_TOP,
    PLACEMENT_BOTTOM,
    PLACEMENT_LEFT,
    PLACEMENT_RIGHT,
)
DEFAULT_PLACEMENT = PLACEMENT_TOP

ALIGN_CENTER = "center"
ALIGN_START = "start"
ALIGN_END = "end"
ALIGN_CHOICES: tuple[str, ...] = (
    ALIGN_CENTER,
    ALIGN_START,
    ALIGN_END,
)
DEFAULT_ALIGN = ALIGN_CENTER


class Tooltip(components.BlockComponent):
    """Accessible rollover and focus tooltip primitive backed by ``<dds-tooltip>``.

    Renders a ``<dds-tooltip class="dds-tooltip">`` Light DOM custom element
    wrapping a trigger element (passed via the block body) and an accessible
    floating tooltip bubble (``<div data-tooltip-bubble role="tooltip">``).

    The client-side web component automatically manages ``aria-describedby``
    linkage between the trigger and the bubble, handles Escape key dismissal,
    supports pointer hover over both trigger and bubble without closing
    (WCAG 2.1 SC 1.4.13), and synchronises with trigger focus/blur and open
    menu states.

    When to Use:
        - Clarifying icon-only buttons, toggles, or compact controls with brief text labels.
        - Providing supplementary hints or keyboard shortcuts on rollover and focus.
        - Offering lightweight contextual information without interrupting user flow.

    Variants & Placements:
        - ``placement`` controls vertical/horizontal orientation relative to the trigger
          (``top``, ``bottom``, ``left``, or ``right``).
        - ``align`` controls alignment along the trigger edge (``center``, ``start``,
          or ``end``).
    """

    text = parameters.StrParam(
        description="Plain text content for the tooltip bubble.",
        default="",
        required=False,
    )
    placement = parameters.StrParam(
        description="Tooltip placement relative to trigger ('top', 'bottom', 'left', 'right').",
        default=DEFAULT_PLACEMENT,
        required=False,
        data_attr=True,
        choices=list(PLACEMENT_CHOICES),
    )
    align = parameters.StrParam(
        description="Tooltip alignment relative to trigger ('center', 'start', 'end').",
        default=DEFAULT_ALIGN,
        required=False,
        data_attr=True,
        choices=list(ALIGN_CHOICES),
    )
    id = parameters.StrParam(
        description="Optional explicit HTML id for the tooltip bubble element.",
        default="",
        required=False,
    )

    class Meta:
        positional_args = ["text"]

    def get_context(self) -> dict[str, typing.Any]:
        """Compute normalized template context for trigger and tooltip bubble.

        Returns:
            Dictionary containing component parameters, resolved placement/alignment,
            and visibility flags.
        """
        context = super().get_context()
        resolved_placement = (
            self.placement if self.placement in PLACEMENT_CHOICES else DEFAULT_PLACEMENT
        )
        resolved_align = self.align if self.align in ALIGN_CHOICES else DEFAULT_ALIGN
        tip_content = self.text or ""

        context["placement"] = resolved_placement
        context["align"] = resolved_align
        context["tip_content"] = tip_content
        context["has_tip"] = bool(tip_content)
        context["bubble_id"] = str(self.id) if self.id else ""
        context["trigger_content"] = self.content or ""
        return context
