from .base import EmailIntegrationError


class AuthError(EmailIntegrationError):
    """Base class for authentication-related errors."""

    default_message = "Authentication error"


class InvalidAccessTokenError(AuthError):
    """
    Raised when an access token is invalid or expired.
    """

    default_message = "Access token is invalid or expired"
