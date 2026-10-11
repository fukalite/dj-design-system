"""Built-in resizable split pane domain component for the dds gallery."""

import typing

from dj_design_system import components, parameters, slots


ORIENTATION_CHOICES: tuple[str, ...] = ("horizontal", "vertical")
DEFAULT_ORIENTATION = "horizontal"
DEFAULT_INITIAL_RATIO = 50
DEFAULT_MIN_RATIO = 20
DEFAULT_MAX_RATIO = 80
DEFAULT_PRIMARY_SURFACE = "docs"
DEFAULT_SECONDARY_SURFACE = "sandbox"
DEFAULT_RESIZER_LABEL = "Resize panes"


class SplitPane(components.BlockComponent):
    """Resizable dual-pane layout container with an accessible separator handle.

    Renders a ``<dds-split-pane class="dds-split-pane">`` Light DOM custom
    element containing a primary pane (``[data-split-pane="primary"]``), an
    accessible separator handle (``[data-split-resizer]`` with
    ``role="separator"``), and a secondary pane
    (``[data-split-pane="secondary"]``).

    Supports both ``"horizontal"`` (side-by-side) and ``"vertical"`` (stacked)
    orientations, clamped ratio bounds (10% to 90%), optional pane header
    labels, and configurable ``data-surface`` tokens on each pane.

    Args:
        orientation: Split orientation (``'horizontal'`` for side-by-side or
            ``'vertical'`` for stacked).
        initial_ratio: Initial primary pane percentage (clamped within bounds).
        min_ratio: Minimum primary pane percentage (clamped to 10-90).
        max_ratio: Maximum primary pane percentage (clamped to min_ratio-90).
        primary_surface: Optional ``data-surface`` attribute for the primary pane.
        secondary_surface: Optional ``data-surface`` attribute for the secondary pane.
        primary_label: Optional header label for the primary pane.
        secondary_label: Optional header label for the secondary pane.
        resizer_label: Accessible label for the resize separator handle.

    Example usage::

        {% dds__split_pane orientation="horizontal" initial_ratio=60 primary_label="Preview" secondary_label="Controls" %}
            {% slot "primary" %}
                <div>Canvas preview</div>
            {% endslot %}
            {% slot "secondary" %}
                <div>Parameter controls</div>
            {% endslot %}
        {% enddds__split_pane %}
    """

    orientation = parameters.StrParam(
        description="Split orientation ('horizontal' for side-by-side or 'vertical' for stacked).",
        default=DEFAULT_ORIENTATION,
        required=False,
        choices=list(ORIENTATION_CHOICES),
    )
    initial_ratio = parameters.IntParam(
        description="Initial primary pane percentage (10-90).",
        default=DEFAULT_INITIAL_RATIO,
        required=False,
    )
    min_ratio = parameters.IntParam(
        description="Minimum primary pane percentage.",
        default=DEFAULT_MIN_RATIO,
        required=False,
    )
    max_ratio = parameters.IntParam(
        description="Maximum primary pane percentage.",
        default=DEFAULT_MAX_RATIO,
        required=False,
    )
    primary_surface = parameters.StrParam(
        description="Optional data-surface attribute for the primary pane.",
        default=DEFAULT_PRIMARY_SURFACE,
        required=False,
    )
    secondary_surface = parameters.StrParam(
        description="Optional data-surface attribute for the secondary pane.",
        default=DEFAULT_SECONDARY_SURFACE,
        required=False,
    )
    primary_label = parameters.StrParam(
        description="Optional header label for the primary pane.",
        default="",
        required=False,
    )
    secondary_label = parameters.StrParam(
        description="Optional header label for the secondary pane.",
        default="",
        required=False,
    )
    resizer_label = parameters.StrParam(
        description="Accessible label for the resize separator handle.",
        default=DEFAULT_RESIZER_LABEL,
        required=False,
    )

    class Meta:
        slots = {
            "primary": slots.Slot(
                required=False,
                description="Primary (leading/top) pane content.",
            ),
            "secondary": slots.Slot(
                required=False,
                description="Secondary (trailing/bottom) pane content.",
            ),
        }

    def get_context(self) -> dict[str, typing.Any]:
        """Compute normalized template context for the split pane and separator handle.

        Returns:
            Dictionary containing clamped ratio bounds, ARIA attributes, and pane content.
        """
        context = super().get_context()
        resolved_orientation = self.orientation or DEFAULT_ORIENTATION
        separator_aria_orientation = (
            "vertical" if resolved_orientation == "horizontal" else "horizontal"
        )
        raw_min = (
            self.min_ratio if self.min_ratio is not None else DEFAULT_MIN_RATIO
        )
        raw_max = (
            self.max_ratio if self.max_ratio is not None else DEFAULT_MAX_RATIO
        )
        raw_initial = (
            self.initial_ratio
            if self.initial_ratio is not None
            else DEFAULT_INITIAL_RATIO
        )
        resolved_min_ratio = max(10, min(90, int(raw_min)))
        resolved_max_ratio = max(resolved_min_ratio, min(90, int(raw_max)))
        resolved_ratio = max(
            resolved_min_ratio, min(resolved_max_ratio, int(raw_initial))
        )
        primary_slot_val = self.slots.get("primary") if self.slots else None
        primary_content = (
            primary_slot_val if primary_slot_val else (self.content or "")
        )
        secondary_content = (
            self.slots.get("secondary") if self.slots else None
        ) or ""
        primary_label = self.primary_label or ""
        secondary_label = self.secondary_label or ""
        primary_surface = (
            self.primary_surface
            if self.primary_surface is not None
            else DEFAULT_PRIMARY_SURFACE
        )
        secondary_surface = (
            self.secondary_surface
            if self.secondary_surface is not None
            else DEFAULT_SECONDARY_SURFACE
        )
        resolved_resizer_label = self.resizer_label or DEFAULT_RESIZER_LABEL
        has_primary_label = bool(primary_label)
        has_secondary_label = bool(secondary_label)
        has_primary_surface = bool(primary_surface)
        has_secondary_surface = bool(secondary_surface)

        context["resolved_orientation"] = resolved_orientation
        context["separator_aria_orientation"] = separator_aria_orientation
        context["resolved_min_ratio"] = resolved_min_ratio
        context["resolved_max_ratio"] = resolved_max_ratio
        context["resolved_ratio"] = resolved_ratio
        context["primary_content"] = primary_content
        context["secondary_content"] = secondary_content
        context["primary_label"] = primary_label
        context["secondary_label"] = secondary_label
        context["primary_surface"] = primary_surface
        context["secondary_surface"] = secondary_surface
        context["resolved_resizer_label"] = resolved_resizer_label
        context["has_primary_label"] = has_primary_label
        context["has_secondary_label"] = has_secondary_label
        context["has_primary_surface"] = has_primary_surface
        context["has_secondary_surface"] = has_secondary_surface
        context["slots"] = self.slots
        context["content"] = self.content or ""
        return context
