"""Consolidated exception hierarchy for dj-design-system."""


class DJDesignSystemError(Exception):
    """Base exception for all errors raised by dj-design-system."""

    def __init__(self, message: str = "", *args: object) -> None:
        self.message = str(message) if message else ""
        if message or args:
            super().__init__(message, *args)
        else:
            super().__init__()


class ComponentValidationError(DJDesignSystemError):
    """Raised when a component render request payload is invalid."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class ComponentNotFoundError(DJDesignSystemError):
    """Raised when a requested component cannot be found."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class ComponentDoesNotExist(ComponentNotFoundError):
    """Raised when a component lookup finds no matching component in the registry."""


class MultipleComponentsFound(DJDesignSystemError):
    """Raised when a component lookup finds multiple matching components."""


class VariantNotFoundError(DJDesignSystemError, ValueError):
    """Raised when a requested component variant cannot be found."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class InvalidTagType(DJDesignSystemError):
    """Raised when a component class is not a TagComponent or BlockComponent."""


__all__ = [
    "ComponentDoesNotExist",
    "ComponentNotFoundError",
    "ComponentValidationError",
    "DJDesignSystemError",
    "InvalidTagType",
    "MultipleComponentsFound",
    "VariantNotFoundError",
]
