from .base import EmailIntegrationError


class FilterError(EmailIntegrationError):
    """Base class for email filter-related errors."""

    default_message = "Email filter error"


class InvalidFilterError(FilterError):
    """
    Raised when email filter validation fails.
    """

    default_message = "Invalid email filter configuration"
