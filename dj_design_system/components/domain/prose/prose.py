"""Built-in prose document domain component for the dds gallery."""

import typing

from django.utils import safestring

from dj_design_system import components, parameters


class Prose(components.BlockComponent):
    """A typographic container for rendered Markdown documentation and long-form prose.

    Use ``Prose`` (``{% dds__prose %}``) to present trusted HTML generated from
    Markdown documentation (such as component ``index.md`` files or standalone
    documentation pages) on the ``docs`` surface with rhythmic vertical flow,
    typographic hierarchy, and optional reading-measure constraint.

    Accepts pre-rendered HTML either via the ``html`` parameter (positional or
    keyword) or via block body content between ``{% dds__prose %}`` and
    ``{% enddds__prose %}``.

    Parameters:
        - ``html``: Optional pre-rendered HTML prose string (trusted markdown output).
        - ``title``: Optional document or section heading title.
        - ``measure``: Whether to constrain reading width to ``--dds-layout-prose-measure`` (default ``True``).

    Example usage::

        {% dds__prose html=doc_html title="Getting Started" %}
        {% enddds__prose %}

        {% dds__prose title="Overview" measure=False %}
            <p>Inline prose content rendered on the docs surface.</p>
        {% enddds__prose %}
    """

    html = parameters.StrParam(
        description="Optional pre-rendered HTML prose string (trusted markdown output).",
        default="",
        required=False,
    )
    title = parameters.StrParam(
        description="Optional document or section heading title.",
        default="",
        required=False,
    )
    measure = parameters.BoolParam(
        description="Whether to constrain reading width to --dds-layout-prose-measure.",
        default=True,
        required=False,
    )

    class Meta:
        positional_args = ["html"]

    def get_context(self) -> dict[str, typing.Any]:
        """Compute template context with resolved prose HTML, title, and measure state.

        Returns:
            Dictionary containing component parameters, ``prose_html``,
            ``has_title``, ``has_body``, and ``constrain_measure``.
        """
        context = super().get_context()
        raw_body = self.html if self.html else (self.content or "")
        prose_html = safestring.SafeString(str(raw_body)) if raw_body else ""
        has_title = bool(self.title)
        has_body = bool(prose_html and str(prose_html).strip())
        constrain_measure = bool(self.measure)

        context["title"] = self.title if self.title is not None else ""
        context["prose_html"] = prose_html
        context["has_title"] = has_title
        context["has_body"] = has_body
        context["constrain_measure"] = constrain_measure
        return context
