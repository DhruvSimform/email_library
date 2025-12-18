from .base import EmailIntegrationError

from .auth import (
    AuthError,
    InvalidAccessTokenError,
    TokenRefreshError,
)

from .provider import (
    ProviderError,
    GmailAPIError,
    OutlookAPIError,
    UnsupportedProviderError,
)

from .attachment import (
    AttachmentError,
    AttachmentTooLargeError,
)

from .network import (
    NetworkError,
    NetworkTimeoutError,
)

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
