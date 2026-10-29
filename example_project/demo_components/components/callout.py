from dj_design_system import components, parameters, slots


class CalloutComponent(components.BlockComponent):
    """A highlighted callout with a message and an optional actions area.

    The ``message`` slot is required; the ``actions`` slot is optional and
    its wrapper is omitted entirely when nothing is supplied.

    Example usage::

        {% callout title="Heads up" %}
            {% slot "message" %}Your trial ends in 3 days.{% endslot %}
            {% slot "actions" %}<a href="/billing/">Upgrade</a>{% endslot %}
        {% endcallout %}
    """

    title = parameters.StrParam(
        "Optional heading shown above the message.", required=False
    )
    tone = parameters.StrParam(
        "Colour treatment of the callout.",
        default="neutral",
        choices=["neutral", "success", "warning"],
        css_class=True,
    )

    class Meta:
        slots = {
            "message": slots.Slot(required=True, description="Main callout text."),
            "actions": slots.Slot(
                required=False, description="Optional links or buttons below the text."
            ),
        }
