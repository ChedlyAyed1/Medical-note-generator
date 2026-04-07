class DomainError(Exception):
    """Base exception for domain-level failures."""


class InvalidStateError(DomainError):
    """Raised when a workflow step is called in the wrong state."""


class ExternalServiceError(DomainError):
    """Raised when an upstream service cannot complete a request."""
