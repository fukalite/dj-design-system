"""Built-in variant view domain component."""

import typing

from django.utils import safestring

from dj_design_system import components, parameters


DEFAULT_VARIANT_LABEL = "Variant"
DEFAULT_SANDBOX_HREF = "#pane-sandbox"


class VariantView(components.TagComponent):
    """Domain gallery component for displaying an individual component variant.

    Renders a ``<section class="dds-variant-view" data-surface="docs">``
    landmark containing a header cluster with a categorical ``dds__badge`` and
    variant heading, an optional pre-rendered HTML description, an optional
    live preview stage iframe with a quick-jump sandbox button, and an optional
    ``dds__code_block`` template usage snippet.

    Args:
        variant_label: Display label of the active variant (or ``Variant`` instance).
        description_html: Optional pre-rendered HTML description of the variant.
        preview_url: Optional preview iframe URL for the variant.
        code: Template tag usage snippet for the variant (or ``TagSignature`` instance).
        badge_label: Badge label displayed next to the variant heading.
        sandbox_href: Anchor or URL to open the variant in the sandbox.

    Example usage::

        {% dds__variant_view "Primary Button" preview_url="/canvas/button/?variant=primary" code="{% dds__button 'Save' variant='primary' %}" %}
        {% dds__variant_view variant_label=variant description_html=desc_html preview_url=url code=signature %}
    """

    template_name = (
        "dj_design_system/components/domain/variant_view/variant_view.html"
    )
    _template_name = template_name

    variant_label = parameters.StrParam(
        description="Display label of the active variant (or Variant instance).",
        default="",
        required=False,
    )
    description_html = parameters.StrParam(
        description="Optional pre-rendered HTML description of the variant.",
        default="",
        required=False,
    )
    preview_url = parameters.StrParam(
        description="Optional preview iframe URL for the variant.",
        default="",
        required=False,
    )
    code = parameters.StrParam(
        description="Template tag usage snippet for the variant (or TagSignature instance).",
        default="",
        required=False,
    )
    badge_label = parameters.StrParam(
        description="Badge label displayed next to the variant heading.",
        default=DEFAULT_VARIANT_LABEL,
        required=False,
    )
    sandbox_href = parameters.StrParam(
        description="Anchor or URL to open the variant in the sandbox.",
        default=DEFAULT_SANDBOX_HREF,
        required=False,
    )

    class Meta:
        positional_args = ["variant_label"]

    class Media:
        css = "dj_design_system/components/domain/variant_view/variant_view.css"

    def __init__(self, **kwargs: typing.Any) -> None:
        """Initialise VariantView and normalise object arguments for variant_label and code.

        Args:
            **kwargs: Component parameter keyword arguments.
        """
        if (
            "variant_label" in kwargs
            and kwargs["variant_label"] is not None
            and not isinstance(kwargs["variant_label"], str)
        ):
            kwargs["variant_label"] = str(
                getattr(kwargs["variant_label"], "label", None)
                or getattr(
                    kwargs["variant_label"], "name", kwargs["variant_label"]
                )
            )
        if (
            "code" in kwargs
            and kwargs["code"] is not None
            and not isinstance(kwargs["code"], str)
        ):
            kwargs["code"] = str(
                getattr(kwargs["code"], "minimal", kwargs["code"])
            )
        super().__init__(**kwargs)

    def get_context(self) -> dict[str, typing.Any]:
        """Build the normalized template context for the variant view.

        Returns:
            Dictionary containing normalized ``variant_label``, ``badge_label``,
            ``description_html``, ``description_safe``, ``has_description``,
            ``preview_url``, ``has_preview``, ``sandbox_href``,
            ``has_sandbox_link``, ``code``, ``has_code``, and ``iframe_title``.
        """
        context = super().get_context()
        variant_label = self.variant_label or DEFAULT_VARIANT_LABEL
        badge_label = self.badge_label or DEFAULT_VARIANT_LABEL
        raw_desc = self.description_html or ""
        description_safe = (
            safestring.SafeString(str(raw_desc)) if raw_desc else ""
        )
        has_description = bool(raw_desc.strip())
        preview_url = self.preview_url or ""
        has_preview = bool(preview_url)
        sandbox_href = (
            self.sandbox_href
            if self.sandbox_href is not None
            else DEFAULT_SANDBOX_HREF
        )
        has_sandbox_link = bool(preview_url and sandbox_href)
        code = self.code or ""
        has_code = bool(code.strip())
        iframe_title = f"{variant_label} preview"

        context["variant_label"] = variant_label
        context["badge_label"] = badge_label
        context["description_html"] = raw_desc
        context["description_safe"] = description_safe
        context["has_description"] = has_description
        context["preview_url"] = preview_url
        context["has_preview"] = has_preview
        context["sandbox_href"] = sandbox_href
        context["has_sandbox_link"] = has_sandbox_link
        context["code"] = code
        context["has_code"] = has_code
        context["iframe_title"] = iframe_title
        return context
