"""Built-in usage example domain component for the dds gallery."""

import typing

from dj_design_system import components, parameters


DEFAULT_CANVAS_ID = "preview"
DEFAULT_SANDBOX_HREF = "#pane-sandbox"
DEFAULT_LANGUAGE = "django"
DEFAULT_IFRAME_TITLE = "Component example preview"


class UsageExample(components.TagComponent):
    """Domain gallery component for displaying a component usage example with preview and code.

    Renders a ``<section class="dds-usage-example">`` container wrapping an
    Every Layout ``<l-stack>`` that composes:
    - An optional ``<h4 data-usage-title>`` heading when ``title`` is non-empty.
    - An optional ``<div data-usage-preview data-surface="stage">`` preview
      stage containing an isolated ``<iframe>`` and an optional
      ``{% dds__button %}`` sandbox shortcut when ``preview_url`` is provided.
    - An optional ``{% dds__code_block %}`` snippet when ``code`` contains
      non-whitespace characters.

    Args:
        title: Heading for the usage example block (e.g. ``"Minimal example"``).
        code: Raw template tag usage snippet string or ``TagSignature`` object.
        preview_url: Optional iframe preview URL.
        canvas_id: Identifier for the preview iframe (defaults to ``"preview"``).
        sandbox_href: Optional link anchor to open in sandbox (defaults to
            ``"#pane-sandbox"``; pass ``""`` to omit the sandbox button).
        language: Code block language identifier (defaults to ``"django"``).

    Example usage::

        {% dds__usage_example "Minimal example" "{% dds__button 'Save' %}" preview_url="/gallery/canvas/?component=dds__button" canvas_id="minimal" %}
        {% dds__usage_example title="Maximal example" code=signature.maximal preview_url=maximal_url canvas_id="maximal" %}
    """

    template_name = (
        "dj_design_system/components/domain/usage_example/usage_example.html"
    )
    _template_name = template_name

    title = parameters.StrParam(
        description="Heading for the usage example block (e.g. 'Minimal example').",
        default="",
        required=False,
    )
    code = parameters.StrParam(
        description="Raw template tag usage snippet string.",
        default="",
        required=False,
    )
    preview_url = parameters.StrParam(
        description="Optional iframe preview URL.",
        default="",
        required=False,
    )
    canvas_id = parameters.StrParam(
        description="Identifier for the preview iframe (e.g. 'minimal', 'maximal', 'variant').",
        default=DEFAULT_CANVAS_ID,
        required=False,
    )
    sandbox_href = parameters.StrParam(
        description="Optional link anchor to open in sandbox (e.g. '#pane-sandbox').",
        default=DEFAULT_SANDBOX_HREF,
        required=False,
    )
    language = parameters.StrParam(
        description="Code block language.",
        default=DEFAULT_LANGUAGE,
        required=False,
    )

    class Meta:
        positional_args = ["title", "code"]

    class Media:
        css = "dj_design_system/components/domain/usage_example/usage_example.css"

    def __init__(self, **kwargs: typing.Any) -> None:
        """Initialise the usage example component and normalise TagSignature code inputs.

        Args:
            **kwargs: Component parameter keyword arguments.
        """
        if (
            "code" in kwargs
            and kwargs["code"] is not None
            and not isinstance(kwargs["code"], str)
        ):
            kwargs["code"] = str(getattr(kwargs["code"], "minimal", kwargs["code"]))
        super().__init__(**kwargs)

    def get_context(self) -> dict[str, typing.Any]:
        """Build the normalised template context for the usage example block.

        Returns:
            Dictionary containing resolved ``title``, ``code``, ``preview_url``,
            ``canvas_id``, ``sandbox_href``, ``language``, ``iframe_title``,
            and boolean visibility flags (``has_title``, ``has_preview``,
            ``has_sandbox_link``, ``has_code``).
        """
        context = super().get_context()
        title = self.title or ""
        code = self.code or ""
        preview_url = self.preview_url or ""
        canvas_id = self.canvas_id or DEFAULT_CANVAS_ID
        sandbox_href = (
            self.sandbox_href
            if self.sandbox_href is not None
            else DEFAULT_SANDBOX_HREF
        )
        language = self.language or DEFAULT_LANGUAGE
        has_title = bool(title)
        has_preview = bool(preview_url)
        has_sandbox_link = bool(preview_url and sandbox_href)
        has_code = bool(code.strip())
        iframe_title = f"{title} preview" if title else DEFAULT_IFRAME_TITLE

        context["title"] = title
        context["code"] = code
        context["preview_url"] = preview_url
        context["canvas_id"] = canvas_id
        context["sandbox_href"] = sandbox_href
        context["language"] = language
        context["has_title"] = has_title
        context["has_preview"] = has_preview
        context["has_sandbox_link"] = has_sandbox_link
        context["has_code"] = has_code
        context["iframe_title"] = iframe_title
        return context
