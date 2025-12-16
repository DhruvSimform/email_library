from .base import EmailIntegrationError


class AttachmentError(EmailIntegrationError):
    """Base class for attachment-related errors."""

    default_message = "Attachment error"


class AttachmentTooLargeError(AttachmentError):
    """
    Raised when attachment exceeds allowed size.
    """

    default_message = "Attachment size exceeds allowed limit"
