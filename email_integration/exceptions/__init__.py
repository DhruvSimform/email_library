from .attachment import AttachmentError, AttachmentTooLargeError
from .auth import AuthError, InvalidAccessTokenError, TokenRefreshError
from .base import EmailIntegrationError
from .network import NetworkError, NetworkTimeoutError
from .provider import (GmailAPIError, OutlookAPIError, ProviderError,
                       UnsupportedProviderError)

__all__ = [
    # Base
    "EmailIntegrationError",

    # Auth
    "AuthError",
    "InvalidAccessTokenError",
    "TokenRefreshError",

    # Provider
    "ProviderError",
    "GmailAPIError",
    "OutlookAPIError",
    "UnsupportedProviderError",

    # Attachment
    "AttachmentError",
    "AttachmentTooLargeError",

    # Network
    "NetworkError",
    "NetworkTimeoutError",
]
