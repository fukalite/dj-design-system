"""Tests for consolidated exception hierarchy."""

import pytest

from dj_design_system.exceptions import (
    ComponentDoesNotExist,
    ComponentNotFoundError,
    ComponentValidationError,
    DJDesignSystemError,
    InvalidTagType,
    MultipleComponentsFound,
    VariantNotFoundError,
)


class TestExceptionHierarchy:
    """Validate that all domain exceptions inherit from DJDesignSystemError."""

    @pytest.mark.parametrize(
        "exc_class",
        [
            ComponentValidationError,
            ComponentNotFoundError,
            VariantNotFoundError,
            InvalidTagType,
            ComponentDoesNotExist,
            MultipleComponentsFound,
        ],
    )
    def test_inherits_from_base_error(self, exc_class):
        assert issubclass(exc_class, DJDesignSystemError)
        assert issubclass(exc_class, Exception)

    def test_variant_not_found_is_value_error(self):
        assert issubclass(VariantNotFoundError, ValueError)

    def test_component_does_not_exist_subclasses_not_found_error(self):
        assert issubclass(ComponentDoesNotExist, ComponentNotFoundError)

    @pytest.mark.parametrize(
        "exc_class",
        [
            DJDesignSystemError,
            ComponentValidationError,
            ComponentNotFoundError,
            VariantNotFoundError,
            InvalidTagType,
            ComponentDoesNotExist,
            MultipleComponentsFound,
        ],
    )
    def test_message_attribute_available(self, exc_class):
        err = exc_class("Something went wrong")
        assert err.message == "Something went wrong"
        assert str(err) == "Something went wrong"

    def test_backwards_compatible_imports(self):
        from dj_design_system.data import InvalidTagType as DataInvalidTagType
        from dj_design_system.services.registry import (
            ComponentDoesNotExist as RegistryComponentDoesNotExist,
        )
        from dj_design_system.services.registry import (
            MultipleComponentsFound as RegistryMultipleComponentsFound,
        )

        assert DataInvalidTagType is InvalidTagType
        assert RegistryComponentDoesNotExist is ComponentDoesNotExist
        assert RegistryMultipleComponentsFound is MultipleComponentsFound
