from .base import EmailIntegrationError

from .auth import (
    AuthError,
    InvalidAccessTokenError,
)

from .provider import (
    ProviderError,
    GmailAPIError,
    OutlookAPIError,
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

    # Provider
    "ProviderError",
    "GmailAPIError",
    "OutlookAPIError",

    # Attachment
    "AttachmentError",
    "AttachmentTooLargeError",

    # Network
    "NetworkError",
    "NetworkTimeoutError",
]
