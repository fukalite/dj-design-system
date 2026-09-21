class ComponentValidationError(Exception):
    """Raised when a component render request payload is invalid."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class ComponentNotFoundError(Exception):
    """Raised when a requested component cannot be found."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)
