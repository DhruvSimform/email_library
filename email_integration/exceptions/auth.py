from .base import EmailIntegrationError


class AuthError(EmailIntegrationError):
    """Base class for authentication-related errors."""

    default_message = "Authentication error"


class InvalidAccessTokenError(AuthError):
    """
    Raised when an access token is invalid or expired.
    """

    default_message = "Access token is invalid or expired"

class TokenRefreshError(AuthError):
    """
    Raised when there is an error refreshing the access token.
    """

    default_message = "Failed to refresh access token"

    def __init__(self, message: str | None = None, original_exception: Exception | None = None):
        super().__init__(message or self.default_message)
        self.original_exception = original_exception    
