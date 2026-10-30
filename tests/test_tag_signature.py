"""Tests for tag_signature module that generates template tag usage examples."""

import pytest

from dj_design_system.components import BlockComponent, TagComponent
from dj_design_system.data import BLOCK_CONTENT_PLACEHOLDER
from dj_design_system.gallery import GalleryConfig, Variant
from dj_design_system.parameters import (
    BoolCSSClassParam,
    BoolParam,
    DictParam,
    StrCSSClassParam,
    StrParam,
)
from dj_design_system.parameters.base import BaseParam
from dj_design_system.services.tag_signature import (
    generate_current_tag_signature,
    generate_tag_signature,
    generate_usage_examples,
)
from dj_design_system.slots import Slot


class SimpleTagComponent(TagComponent):
    """A simple tag component with one required string parameter."""

    name = StrParam("The name parameter")

    class Meta:
        positional_args = ["name"]

    template_format_str = "<div>{name}</div>"


class TagComponentWithOptional(TagComponent):
    """A tag component with required and optional parameters."""

    label = StrParam("The label")
    size = StrCSSClassParam("Size option", required=False, choices=["small", "large"])
    dark = BoolCSSClassParam(required=False, default=False)

    class Meta:
        positional_args = ["label"]

    template_format_str = "<button class='{classes}'>{label}</button>"


class TagComponentMultiplePositional(TagComponent):
    """A tag component with multiple positional arguments."""

    url = StrParam("The URL")
    label = StrParam("The link label")

    class Meta:
        positional_args = ["url", "label"]

    template_format_str = "<a href='{url}'>{label}</a>"


# ---------------------------------------------------------------------------
# Additional component helpers for gap coverage
# ---------------------------------------------------------------------------


class IntParam(BaseParam):
    """Custom integer parameter for testing non-standard type fallback."""

    type = int


class BoolPositionalComponent(TagComponent):
    """Component with a boolean default positional arg."""

    enabled = BoolParam(required=False, default=True)

    class Meta:
        positional_args = ["enabled"]

    template_format_str = "<div>{enabled}</div>"


class IntKwargComponent(TagComponent):
    """Component with a custom int keyword arg (non-str, non-bool)."""

    count = IntParam("A count", required=False, default=42)

    template_format_str = "<div>{count}</div>"


class IntPositionalComponent(TagComponent):
    """Component with a custom int positional arg."""

    count = IntParam("A count", default=42)

    class Meta:
        positional_args = ["count"]

    template_format_str = "<div>{count}</div>"


class BlockNoParamsComponent(BlockComponent):
    """Block component with no parameters at all."""

    template_format_str = "<div>{content}</div>"


class BlockMultiKwargComponent(BlockComponent):
    """Block component with multiple optional keyword parameters."""

    heading = StrParam("The heading", required=False)
    level = StrCSSClassParam("Level", required=False, choices=["info", "warning"])

    template_format_str = "<div class='{level}'><h3>{heading}</h3>{content}</div>"


class RequiredKwargComponent(TagComponent):
    """Component with a required non-positional keyword param."""

    label = StrParam("The label")

    template_format_str = "<button>{label}</button>"


class BoolCSSNoDefaultComponent(TagComponent):
    """Component with BoolCSSClassParam that has no default."""

    text = StrParam("Text")
    active = BoolCSSClassParam(required=False)  # no default

    class Meta:
        positional_args = ["text"]

    template_format_str = "<span class='{classes}'>{text}</span>"


class CustomNullValueComponent(TagComponent):
    """Component with a custom param type that generates None as example value."""

    count = IntParam("A count", required=False)  # no default, no choices

    template_format_str = "<div>{count}</div>"


class GhostPositionalComponent(TagComponent):
    """Component with positional_args listing a name not in params."""

    template_format_str = "<div></div>"

    class Meta:
        positional_args = ["nonexistent"]


class SimpleBlockComponent(BlockComponent):
    """A simple block component with no positional args."""

    heading = StrParam("Heading", required=False)

    template_format_str = "<div><h3>{heading}</h3>{content}</div>"


class BlockDictParamComponent(BlockComponent):
    """Block component with a dict parameter alongside other keyword params."""

    heading = StrParam("Heading", required=False, default="Hello")
    attrs = DictParam("Extra attributes", required=False, default={"a": 1, "b": 2})

    template_format_str = "<div><h3>{heading}</h3>{content}</div>"


class BlockComponentWithPositional(BlockComponent):
    """A block component with positional args."""

    level = StrCSSClassParam(
        "Alert level", default="info", choices=["info", "warning", "error"]
    )

    class Meta:
        positional_args = ["level"]

    template_format_str = "<div class='alert-{level}'>{content}</div>"


class TestGenerateTagSignature:
    """Test suite for generate_tag_signature function."""

    def test_simple_tag_component_minimal(self):
        """Test minimal usage for a simple tag component."""
        sig = generate_tag_signature(SimpleTagComponent)
        assert sig.minimal == '{% simple_tag "foo" %}'

    def test_simple_tag_component_maximal(self):
        """Test maximal usage for a simple tag component."""
        sig = generate_tag_signature(SimpleTagComponent)
        assert sig.maximal == '{% simple_tag "foo" %}'

    def test_tag_with_optional_params_minimal(self):
        """Test minimal usage shows only required positional args."""
        sig = generate_tag_signature(TagComponentWithOptional)
        assert sig.minimal == '{% tag_component_with_optional "foo" %}'

    def test_tag_with_optional_params_maximal(self):
        """Test maximal usage includes optional parameters."""
        sig = generate_tag_signature(TagComponentWithOptional)
        # size should use first choice "small", dark should use default False
        assert "{% tag_component_with_optional" in sig.maximal
        assert '"foo"' in sig.maximal  # positional arg
        assert 'size="small"' in sig.maximal
        assert "dark=False" in sig.maximal

    def test_component_with_multiple_positional_args_minimal(self):
        """Test minimal for component with multiple required positional args."""
        sig = generate_tag_signature(TagComponentMultiplePositional)
        assert sig.minimal == '{% tag_component_multiple_positional "foo" "bar" %}'

    def test_component_with_multiple_positional_args_maximal(self):
        """Test maximal for component with multiple positional args."""
        sig = generate_tag_signature(TagComponentMultiplePositional)
        # Both are positional, so maximal should match minimal
        assert sig.maximal == '{% tag_component_multiple_positional "foo" "bar" %}'

    def test_simple_block_component_minimal(self):
        """Test minimal usage for a block component without positional args."""
        sig = generate_tag_signature(SimpleBlockComponent)
        assert (
            sig.minimal
            == f"{{% simple_block %}}{BLOCK_CONTENT_PLACEHOLDER}{{% endsimple_block %}}"
        )

    def test_simple_block_component_maximal(self):
        """Test maximal usage for a block component."""
        sig = generate_tag_signature(SimpleBlockComponent)
        # heading is optional, so maximal should show it
        assert "{% simple_block" in sig.maximal
        assert 'heading="foo"' in sig.maximal
        assert BLOCK_CONTENT_PLACEHOLDER in sig.maximal
        assert "{% endsimple_block %}" in sig.maximal

    def test_block_with_positional_args_minimal(self):
        """Test minimal for block component with positional args."""
        sig = generate_tag_signature(BlockComponentWithPositional)
        # level has default, so minimal might not include it (check required attribute)
        # Actually, level has choices and default, so it uses the default
        assert "info" in sig.minimal

    def test_block_with_positional_args_maximal(self):
        """Test maximal for block component with positional args."""
        sig = generate_tag_signature(BlockComponentWithPositional)
        # level has choices, should use first choice "info"
        assert "level=" in sig.maximal or "info" in sig.maximal

    def test_string_example_cycling(self):
        """Test that string examples cycle through foo, bar, baz."""

        class ThreeStringParams(TagComponent):
            """Component with three string parameters."""

            p1 = StrParam("First")
            p2 = StrParam("Second", required=False)
            p3 = StrParam("Third", required=False)

            class Meta:
                positional_args = ["p1"]

            template_format_str = "<div>{p1} {p2} {p3}</div>"

        sig = generate_tag_signature(ThreeStringParams)
        # p1 is positional so it's just the value; p2 and p3 are keyword args
        assert '"foo"' in sig.maximal  # p1 is positional, not named
        assert 'p2="bar"' in sig.maximal
        assert 'p3="baz"' in sig.maximal

    def test_usage_description_present(self):
        """Test that TagSignature has all required fields."""
        sig = generate_tag_signature(SimpleTagComponent)
        assert hasattr(sig, "minimal")
        assert hasattr(sig, "maximal")
        assert hasattr(sig, "minimal_html")
        assert hasattr(sig, "maximal_html")
        assert isinstance(sig.minimal, str)
        assert isinstance(sig.maximal, str)
        assert isinstance(sig.minimal_html, str)
        assert isinstance(sig.maximal_html, str)


class TestGenerateCurrentTagSignature:
    """Test suite for generate_current_tag_signature function."""

    def test_block_component_uses_content_value_when_present(self):
        """Current signature should render explicit block content from kwargs."""
        sig = generate_current_tag_signature(
            SimpleBlockComponent,
            {"heading": "Hello", "content": "Custom body"},
        )

        assert "Custom body" in sig.minimal
        assert "content=" not in sig.minimal
        assert "{% endsimple_block %}" in sig.minimal

    def test_block_component_uses_placeholder_when_content_missing(self):
        """Current signature should fall back to BLOCK_CONTENT_PLACEHOLDER."""
        sig = generate_current_tag_signature(SimpleBlockComponent, {})

        assert BLOCK_CONTENT_PLACEHOLDER in sig.minimal
        assert "...content..." not in sig.minimal

    def test_tag_component_current_signature(self):
        """generate_current_tag_signature works for non-block components."""
        sig = generate_current_tag_signature(SimpleTagComponent, {"name": "hello"})
        assert '{% simple_tag "hello" %}' == sig.minimal

    def test_tag_component_current_no_args(self):
        """Non-block component with empty kwargs renders just the tag."""
        sig = generate_current_tag_signature(SimpleTagComponent, {})
        assert "{% simple_tag %}" == sig.minimal


# ---------------------------------------------------------------------------
# Additional coverage: format helpers and edge-case generate_tag_signature
# ---------------------------------------------------------------------------


class TestTagSignatureEdgeCases:
    def test_bool_positional_arg(self):
        """BoolParam positional arg → _format_positional_arg bool branch."""
        sig = generate_tag_signature(BoolPositionalComponent)
        # The minimal has no required bool positional, but maximal has default=True
        assert "True" in sig.maximal

    def test_int_keyword_arg(self):
        """IntParam with default → _format_param_for_tag non-str/bool fallback."""
        sig = generate_tag_signature(IntKwargComponent)
        assert "count=42" in sig.maximal

    def test_int_positional_arg(self):
        """IntParam positional → _format_positional_arg non-str/bool fallback."""
        sig = generate_tag_signature(IntPositionalComponent)
        assert "42" in sig.minimal

    def test_block_no_params_empty_args_str(self):
        """Block component with no params → maximal has no arg string."""
        sig = generate_tag_signature(BlockNoParamsComponent)
        assert "{% block_no_params %}" in sig.minimal

    def test_block_multi_kwarg_multiline(self):
        """Block component with 2+ keyword params → multiline format."""
        sig = generate_tag_signature(BlockMultiKwargComponent)
        assert "{% block_multi_kwarg" in sig.maximal
        assert "heading" in sig.maximal
        assert "level" in sig.maximal

    def test_block_dict_param_multiline(self):
        """A dict param's closing brace must not end the opening tag early."""
        sig = generate_tag_signature(BlockDictParamComponent)
        assert sig.maximal == (
            "{% block_dict_param\n"
            '  heading="Hello"\n'
            "  attrs={'a': 1, 'b': 2}\n"
            "%}\n"
            f"{BLOCK_CONTENT_PLACEHOLDER}\n"
            "{% endblock_dict_param %}"
        )

    def test_block_dict_param_current_multiline(self):
        """Current signature for a block with a dict param keeps the dict intact."""
        sig = generate_current_tag_signature(
            BlockDictParamComponent,
            {"attrs": {"a": 1}, "heading": "Hi", "content": "Body"},
        )
        assert sig.minimal == (
            "{% block_dict_param\n"
            "  attrs={'a': 1}\n"
            '  heading="Hi"\n'
            "%}\n"
            "Body\n"
            "{% endblock_dict_param %}"
        )

    def test_required_kwarg_included_in_signatures(self):
        """Required non-positional params are included in minimal and maximal signatures."""
        sig = generate_tag_signature(RequiredKwargComponent)
        # label is required and not positional → included as keyword arg
        assert '{% required_kwarg label="foo" %}' == sig.maximal
        assert '{% required_kwarg label="foo" %}' == sig.minimal
        assert sig.minimal_spec.params.get("label") == "foo"
        assert sig.maximal_spec.params.get("label") == "foo"

    def test_bool_css_no_default_generates_true(self):
        """BoolCSSClassParam with no default returns True as example value."""
        sig = generate_tag_signature(BoolCSSNoDefaultComponent)
        assert "active=True" in sig.maximal

    def test_custom_null_value_param_skipped(self):
        """Custom param type that returns None is skipped in maximal signature."""
        sig = generate_tag_signature(CustomNullValueComponent)
        assert "count" not in sig.maximal

    def test_ghost_positional_skipped(self):
        """Positional arg not in params is gracefully skipped."""
        sig = generate_tag_signature(GhostPositionalComponent)
        assert "nonexistent" not in sig.minimal

    @pytest.mark.django_db
    def test_model_param_fallback_generates_first_instance(self):
        """ModelParam generates the most recent database instance as its fallback example."""
        from django.contrib.auth import get_user_model

        from dj_design_system.parameters.model import ModelParam

        User = get_user_model()
        User.objects.create(username="sigtest_user_1")
        user2 = User.objects.create(username="sigtest_user_2")

        class UserParam(ModelParam):
            class Meta:
                model = "auth.User"
                fields = ["username"]

        class _ModelParamComponent(TagComponent):
            template_format_str = "<div></div>"
            user = UserParam("A user", required=False)

        sig = generate_tag_signature(_ModelParamComponent)
        # It orders by -pk, so user2 should be the fallback value.
        assert sig.maximal_spec.params["user"] == user2
        # The snippet names a context variable rather than the instance's str().
        assert "user=user" in sig.maximal
        assert str(user2) not in sig.maximal

    @pytest.mark.django_db
    def test_model_instance_formats_as_param_name(self):
        """Model instances render as a variable named after the parameter, keyword or positional."""
        from django.contrib.auth import get_user_model

        from dj_design_system.services.tag_signature import (
            _format_param_for_tag,
            _format_positional_arg,
        )

        user = get_user_model().objects.create(username="Cam's account")
        assert _format_param_for_tag("author", user) == "author=author"
        assert _format_positional_arg("author", user) == "author"


# ---------------------------------------------------------------------------
# Slotted component signature tests
# ---------------------------------------------------------------------------


class SlottedBlockComponent(BlockComponent):
    """A slotted block component for testing tag signature generation."""

    title = StrParam("The title")

    class Meta:
        positional_args = ["title"]
        slots = {
            "body": Slot(required=True, description="Main body content"),
            "footer": Slot(required=False, default="Default footer"),
        }

    template_format_str = "<div>{body}{footer}</div>"


class TestSlottedTagSignature:
    """Tests for slotted component tag signature generation."""

    def test_minimal_shows_only_required_slots(self):
        """Minimal signature includes only required slots."""
        sig = generate_tag_signature(SlottedBlockComponent)
        assert '{% slot "body" %}' in sig.minimal
        assert "{% endslot %}" in sig.minimal
        assert '{% slot "footer" %}' not in sig.minimal

    def test_maximal_shows_all_slots(self):
        """Maximal signature includes all slots (required + optional)."""
        sig = generate_tag_signature(SlottedBlockComponent)
        assert '{% slot "body" %}' in sig.maximal
        assert '{% slot "footer" %}' in sig.maximal

    def test_slot_default_used_as_placeholder(self):
        """Slots with defaults use the default text as placeholder content."""
        sig = generate_tag_signature(SlottedBlockComponent)
        assert "Default footer" in sig.maximal

    def test_required_slot_sample_placeholder(self):
        """Required slots without defaults get 'Sample <name> content'."""
        sig = generate_tag_signature(SlottedBlockComponent)
        assert "Sample body content" in sig.minimal

    def test_slotted_has_end_tag(self):
        """Slotted signature includes endtag."""
        sig = generate_tag_signature(SlottedBlockComponent)
        assert "{% endslotted_block %}" in sig.minimal
        assert "{% endslotted_block %}" in sig.maximal

    def test_slotted_includes_positional_args(self):
        """Slotted signature includes positional args in the opening tag."""
        sig = generate_tag_signature(SlottedBlockComponent)
        # title is required positional
        assert '{% slotted_block "' in sig.minimal

    def test_current_signature_with_slot_kwargs(self):
        """generate_current_tag_signature handles slot__ prefixed kwargs."""
        sig = generate_current_tag_signature(
            SlottedBlockComponent,
            {"title": "Hello", "slot__body": "Custom body", "slot__footer": "My foot"},
        )
        assert '{% slot "body" %}Custom body{% endslot %}' in sig.minimal
        assert '{% slot "footer" %}My foot{% endslot %}' in sig.minimal

    def test_current_signature_without_slots_falls_back_to_required(self):
        """With no slot__ kwargs, required slots get default placeholders."""
        sig = generate_current_tag_signature(
            SlottedBlockComponent,
            {"title": "Hello"},
        )
        assert '{% slot "body" %}' in sig.minimal


class TestGalleryParameterFormatting:
    """Test formatting behaviour of the GalleryParameter wrapper."""

    def test_format_param_for_tag_with_code(self):
        from dj_design_system.data import GalleryParameter
        from dj_design_system.services.tag_signature import _format_param_for_tag

        param = GalleryParameter(value="raw_value", code="my_var")
        assert _format_param_for_tag("user", param) == "user=my_var"

    def test_format_param_for_tag_without_code(self):
        from dj_design_system.data import GalleryParameter
        from dj_design_system.services.tag_signature import _format_param_for_tag

        param = GalleryParameter(value="raw_value")
        assert _format_param_for_tag("user", param) == 'user="raw_value"'

    def test_format_positional_arg_with_code(self):
        from dj_design_system.data import GalleryParameter
        from dj_design_system.services.tag_signature import _format_positional_arg

        param = GalleryParameter(value="raw_value", code="my_var")
        assert _format_positional_arg("user", param) == "my_var"

    def test_unwrap_example(self):
        from dj_design_system.data import GalleryParameter
        from dj_design_system.services.tag_signature import _unwrap_example

        param = GalleryParameter(value="raw_value", code="my_var")
        assert _unwrap_example(param) == "raw_value"


class RequiredKeywordComponent(TagComponent):
    """Component with required keyword parameter not in positional_args."""

    title = StrParam("The title", required=True)
    subtitle = StrParam("Optional subtitle", required=False, default="Default Subtitle")

    template_format_str = "<h1>{title}</h1><p>{subtitle}</p>"


class TestRequiredKeywordParam:
    """Test handling of required keyword parameters not in positional_args (#97)."""

    def test_minimal_signature_includes_required_keyword_arg(self):
        sig = generate_tag_signature(RequiredKeywordComponent)
        assert 'title="foo"' in sig.minimal
        assert sig.minimal_spec.params.get("title") == "foo"
        assert "subtitle" not in sig.minimal
        assert "subtitle" not in sig.minimal_spec.params

    def test_maximal_signature_includes_required_keyword_arg(self):
        sig = generate_tag_signature(RequiredKeywordComponent)
        assert 'title="foo"' in sig.maximal
        assert sig.maximal_spec.params.get("title") == "foo"
        assert 'subtitle="Default Subtitle"' in sig.maximal
        assert sig.maximal_spec.params.get("subtitle") == "Default Subtitle"

    def test_maximal_signature_respects_mutually_exclusive_constraints(self):
        """Mutually exclusive params are not simultaneously emitted in maximal signature."""
        from dj_design_system.components.gallery.elements.button.button import Button

        sig = generate_tag_signature(Button)
        assert not (
            "href" in sig.maximal_spec.params and "pressed" in sig.maximal_spec.params
        )
        kwargs = dict(sig.maximal_spec.params)
        for name, val in zip(
            Button.get_positional_args(), sig.maximal_spec.positional_args
        ):
            kwargs[name] = val
        button_instance = Button(**kwargs)
        assert button_instance.render()


class TestBlockContentFromGalleryConfig:
    """Tests for usage example block content and param_defaults (#154, #162)."""

    def test_param_defaults_content_used_in_both_snippets(self):
        import warnings

        from dj_design_system.components import BlockComponent
        from dj_design_system.data import ComponentInfo
        from dj_design_system.gallery import GalleryConfig, Variant
        from dj_design_system.services.registry import component_registry

        class RichBlock(BlockComponent):
            title = StrParam("Title", default="Heading")

        cfg = GalleryConfig(
            param_defaults={"content": "<p>Default body</p>"},
            variants=[
                Variant(name="maximal", kwargs={"content": "<p>Maximal body</p>"}),
            ],
        )
        info = ComponentInfo(
            component_class=RichBlock,
            name="rich_block",
            app_label="test_app",
            relative_path="",
        )
        info.__dict__["gallery_config"] = cfg
        component_registry._components.append(info)
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", DeprecationWarning)
                sig = generate_tag_signature(RichBlock)

            assert "<p>Default body</p>" in sig.minimal
            assert "content=" not in sig.minimal
            assert sig.minimal_spec.params.get("content") == "<p>Default body</p>"

            assert "<p>Maximal body</p>" in sig.maximal
            assert "content=" not in sig.maximal
            assert sig.maximal_spec.params.get("content") == "<p>Maximal body</p>"
        finally:
            component_registry._components.remove(info)

    def test_gallery_parameter_code_used_for_block_content(self):
        from dj_design_system.components import BlockComponent
        from dj_design_system.data import ComponentInfo, GalleryParameter
        from dj_design_system.gallery import GalleryConfig, Variant
        from dj_design_system.services.registry import component_registry

        class CodeBlock(BlockComponent):
            pass

        cfg = GalleryConfig(
            variants=[
                Variant(
                    name="basic",
                    kwargs={
                        "content": GalleryParameter(
                            value="<strong>Rendered</strong>",
                            code="{{ article.body }}",
                        )
                    },
                ),
            ],
        )
        info = ComponentInfo(
            component_class=CodeBlock,
            name="code_block",
            app_label="test_app",
            relative_path="",
        )
        info.__dict__["gallery_config"] = cfg
        component_registry._components.append(info)
        try:
            sig = generate_tag_signature(CodeBlock)
            assert (
                "{% code_block %}{{ article.body }}{% endcode_block %}" in sig.minimal
            )
            assert sig.minimal_spec.params.get("content") == "<strong>Rendered</strong>"
        finally:
            component_registry._components.remove(info)

    def test_multiline_content_in_parameterless_block_tag_sits_on_own_lines(self):
        from dj_design_system.components import BlockComponent
        from dj_design_system.data import ComponentInfo
        from dj_design_system.gallery import GalleryConfig
        from dj_design_system.services.registry import component_registry

        class StackBlock(BlockComponent):
            pass

        cfg = GalleryConfig(
            param_defaults={"content": "<div>One</div>\n<div>Two</div>"},
        )
        info = ComponentInfo(
            component_class=StackBlock,
            name="stack_block",
            app_label="test_app",
            relative_path="",
        )
        info.__dict__["gallery_config"] = cfg
        component_registry._components.append(info)
        try:
            sig = generate_tag_signature(StackBlock)
            assert (
                sig.minimal
                == "{% stack_block %}\n<div>One</div>\n<div>Two</div>\n{% endstack_block %}"
            )
        finally:
            component_registry._components.remove(info)


class OptionalSlotCard(BlockComponent):
    title = StrParam("Title", required=False)

    class Meta:
        slots = {
            "body": Slot(required=True),
            "footer": Slot(required=False),
        }


class OptionalParamsComponent(TagComponent):
    template_format_str = "<p>{label} {size} {note}</p>"
    label = StrParam("Label")
    size = StrParam("Size", required=False, default="small")
    note = StrParam("Note", required=False)
    heading = StrParam("Heading", required=True)

    class Meta:
        positional_args = ["label", "note"]


def _custom_param_factory(*, param_spec, param_name: str, index: int):
    del param_spec, index
    return f"factory_{param_name}"


def _custom_slot_factory(*, slot, slot_name: str):
    del slot
    return f"Factory {slot_name}"


class TestExplicitVariantSlotsAndParams:
    """Explicitly defined variants follow their definition strictly with zero guesswork."""

    def test_omitted_optional_slot_not_rendered(self, register_gallery_component):
        register_gallery_component(
            OptionalSlotCard,
            "optional_slot_card",
            GalleryConfig(
                variants=[
                    Variant(
                        name="maximal",
                        kwargs={"title": "Hello", "slot__body": "Body text"},
                    ),
                ]
            ),
        )

        sig = generate_tag_signature(OptionalSlotCard)

        assert '{% slot "body" %}Body text{% endslot %}' in sig.maximal
        assert '{% slot "footer" %}' not in sig.maximal
        assert sig.maximal_spec.params.get("slot__body") == "Body text"
        assert "slot__footer" not in sig.maximal_spec.params

    def test_omitted_required_slot_raises_value_error(self, register_gallery_component):
        register_gallery_component(
            OptionalSlotCard,
            "optional_slot_card",
            GalleryConfig(variants=[Variant(name="maximal", kwargs={"title": "Hi"})]),
        )

        with pytest.raises(ValueError, match="missing required slot 'body'"):
            generate_tag_signature(OptionalSlotCard)

    def test_without_maximal_variant_all_slots_filled(self, register_gallery_component):
        register_gallery_component(
            OptionalSlotCard, "optional_slot_card", GalleryConfig()
        )

        sig = generate_tag_signature(OptionalSlotCard)

        assert '{% slot "footer" %}Sample footer content{% endslot %}' in sig.maximal
        assert sig.maximal_spec.params.get("slot__footer") == "Sample footer content"

    def test_omitted_optional_params_not_generated(self, register_gallery_component):
        register_gallery_component(
            OptionalParamsComponent,
            "optional_params",
            GalleryConfig(
                variants=[
                    Variant(
                        name="maximal",
                        kwargs={"label": "Hello", "heading": "Title"},
                    ),
                ]
            ),
        )

        sig = generate_tag_signature(OptionalParamsComponent)

        assert sig.maximal == '{% optional_params "Hello" heading="Title" %}'
        assert sig.maximal_spec.positional_args == ("Hello",)
        assert sig.maximal_spec.params == {"heading": "Title"}

    def test_omitted_required_params_raises_value_error(
        self, register_gallery_component
    ):
        register_gallery_component(
            OptionalParamsComponent,
            "optional_params",
            GalleryConfig(variants=[Variant(name="maximal", kwargs={"size": "big"})]),
        )

        with pytest.raises(ValueError, match="missing required parameter 'label'"):
            generate_tag_signature(OptionalParamsComponent)

    def test_without_maximal_variant_all_params_generated(
        self, register_gallery_component
    ):
        register_gallery_component(
            OptionalParamsComponent, "optional_params", GalleryConfig()
        )

        sig = generate_tag_signature(OptionalParamsComponent)

        assert 'size="small"' in sig.maximal
        assert "heading=" in sig.maximal
        assert len(sig.maximal_spec.positional_args) == 2


class TestGenerateUsageExamples:
    """Tests for generate_usage_examples resolution, suppression, and strategies."""

    def test_default_global_variants_remain_when_other_variant_defined(
        self, register_gallery_component
    ):
        register_gallery_component(
            OptionalParamsComponent,
            "optional_params",
            GalleryConfig(
                variants=[
                    Variant(
                        name="custom_doc",
                        label="Custom Doc Example",
                        description="Shown in docs.",
                        kwargs={"label": "Custom", "heading": "Head"},
                        show_in_docs=True,
                    ),
                    Variant(
                        name="nav_only",
                        label="Nav Only",
                        kwargs={"label": "Nav", "heading": "Head"},
                    ),
                ]
            ),
        )

        examples = generate_usage_examples(component_class=OptionalParamsComponent)
        assert [ex.name for ex in examples] == ["basic", "maximal", "custom_doc"]
        assert [ex.label for ex in examples] == [
            "Minimal example",
            "All parameters",
            "Custom Doc Example",
        ]
        assert examples[2].description == "Shown in docs."

    def test_component_level_doc_variants_suppression_and_selection(
        self, register_gallery_component
    ):
        register_gallery_component(
            OptionalParamsComponent,
            "optional_params",
            GalleryConfig(
                doc_variants={"maximal": False},
                variants=[
                    Variant(
                        name="basic",
                        kwargs={"label": "Only Basic", "heading": "H"},
                    ),
                ],
            ),
        )

        examples = generate_usage_examples(component_class=OptionalParamsComponent)
        assert [ex.name for ex in examples] == ["basic"]
        assert examples[0].code == '{% optional_params "Only Basic" heading="H" %}'

    def test_component_level_doc_variants_sequence_includes_custom_and_builtin(
        self, register_gallery_component
    ):
        register_gallery_component(
            OptionalSlotCard,
            "optional_slot_card",
            GalleryConfig(
                doc_variants=["basic", "all_slots", "with_footer"],
                variants=[
                    Variant(
                        name="with_footer",
                        label="Footer Example",
                        kwargs={
                            "title": "Card",
                            "slot__body": "Body",
                            "slot__footer": "Footer text",
                        },
                    ),
                ],
            ),
        )
        examples = generate_usage_examples(component_class=OptionalSlotCard)
        assert [ex.name for ex in examples] == ["basic", "all_slots", "with_footer"]
        assert [ex.label for ex in examples] == [
            "Minimal example",
            "All slots",
            "Footer Example",
        ]

    def test_defaults_and_all_slots_strategies_and_factories(
        self, settings, register_gallery_component
    ):
        settings.DJ_DESIGN_SYSTEM = {
            "GALLERY_DOC_VARIANTS": {
                "minimal": {"show_in_docs": False},
                "maximal": {"show_in_docs": False},
                "defaults": {
                    "show_in_docs": True,
                    "param_factory": _custom_param_factory,
                },
                "all_slots": {
                    "show_in_docs": True,
                    "slot_factory": _custom_slot_factory,
                },
            }
        }
        register_gallery_component(
            OptionalSlotCard, "optional_slot_card", GalleryConfig()
        )
        examples = generate_usage_examples(component_class=OptionalSlotCard)
        assert [ex.name for ex in examples] == ["defaults", "all_slots"]
        assert "Factory body" in examples[1].code
        assert "Factory footer" in examples[1].code

        register_gallery_component(
            OptionalParamsComponent, "optional_params", GalleryConfig()
        )
        param_examples = generate_usage_examples(
            component_class=OptionalParamsComponent
        )
        defaults_ex = param_examples[0]
        assert 'size="small"' in defaults_ex.code
        assert "note" not in defaults_ex.code
        assert "factory_label" in defaults_ex.code
        assert 'heading="factory_heading"' in defaults_ex.code

    def test_global_disable_applies_to_implicit_variant_unless_explicitly_enabled(
        self, settings, register_gallery_component
    ):
        register_gallery_component(
            OptionalParamsComponent,
            "optional_params",
            GalleryConfig(
                variants=[
                    Variant(
                        name="basic",
                        kwargs={"label": "Basic", "heading": "H"},
                    ),
                    Variant(
                        name="maximal",
                        kwargs={"label": "Max", "heading": "H", "size": "large"},
                    ),
                ]
            ),
        )
        settings.DJ_DESIGN_SYSTEM = {
            "GALLERY_DOC_VARIANTS": {
                "maximal": {"show_in_docs": False},
            }
        }
        examples = generate_usage_examples(component_class=OptionalParamsComponent)
        assert [ex.name for ex in examples] == ["basic"]
