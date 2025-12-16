from .base import EmailIntegrationError


class ProviderError(EmailIntegrationError):
    """Base class for provider-related errors."""

    default_message = "Email provider error"


class GmailAPIError(ProviderError):
    """
    Raised when Gmail API returns an error.
    """

    default_message = "Gmail service error"


class OutlookAPIError(ProviderError):
    """
    Raised when Outlook (Microsoft Graph) API returns an error.
    """

    default_message = "Outlook service error"
