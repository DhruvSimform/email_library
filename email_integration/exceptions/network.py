from .base import EmailIntegrationError


class NetworkError(EmailIntegrationError):
    """Base class for network-related errors."""

    default_message = "Network error occurred"


class NetworkTimeoutError(NetworkError):
    """
    Raised when a network request times out.
    """

    default_message = "Network timeout occurred"
