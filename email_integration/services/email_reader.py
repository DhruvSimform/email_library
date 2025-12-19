from __future__ import annotations

from email_integration.domain.models.attachment import Attachment
from email_integration.domain.models.email_detail import EmailDetail
from email_integration.domain.models.email_filter import EmailSearchFilter
from email_integration.domain.models.email_message import EmailMessage
from email_integration.domain.models.folders import MailFolder
from email_integration.exceptions.provider import UnsupportedProviderError
from email_integration.providers.registry import ProviderRegistry
from email_integration.services.email_core import EmailCore
from email_integration.core.logging import logger


class EmailReader:
    """
    Public read-only email service.

    This is the main entry point for consuming applications.
    It hides:
    - Provider selection
    - Internal orchestration
    - Provider-specific complexity
    """

    def __init__(
        self,
        *,
        provider: str,
        access_token: str,
    ) -> None:
        provider_name = provider.lower()
        try:
            logger.debug(f"Initializing EmailReader with provider: {provider_name}")
            provider_instance = ProviderRegistry.get(provider_name)
        except UnsupportedProviderError as e:
            logger.error(f"Unsupported email provider: {provider_name}")
            raise UnsupportedProviderError(f"Email provider '{provider}' is not supported. Please check the spelling and try again.") from e
        provider_instance.set_credentials(access_token)
        self._core = EmailCore(provider_instance)

    # =========================
    # Inbox
    # =========================

    def fetch_emails(
        self,
        *,
        page_size: int = 10,
        cursor: str | None = None,
        folder: MailFolder | None = None,
        filters: EmailSearchFilter | None = None,
    ) -> tuple[list[EmailMessage], str | None]:
        """
        Fetch inbox emails with pagination.
        """
        return self._core.fetch_emails(
            page_size=page_size,
            cursor=cursor,
            folder=folder,
            filters=filters,
        )

    # =========================
    # Email Detail
    # =========================

    def get_email_detail(
        self,
        *,
        message_id: str,
    ) -> EmailDetail:
        """
        Fetch full details of a single email.
        """
        return self._core.fetch_email_detail(
            message_id=message_id,
        )

    # =========================
    # Folders
    # =========================

    def get_folders(self) -> list[MailFolder]:
        """
        List available default folders.
        """
        return self._core.list_folders()

    # =========================
    # Attachments
    # =========================

    def get_attachments(
        self,
        *,
        message_id: str,
    ) -> list[Attachment]:
        """
        List attachments for an email.
        """
        return self._core.list_attachments(
            message_id=message_id,
        )

    def download_attachment(
        self,
        *,
        message_id: str,
        attachment_id: str,
    ) -> bytes:
        """
        Download an attachment.
        """
        return self._core.download_attachment(
            message_id=message_id,
            attachment_id=attachment_id,
        )

    # =========================
    # Health / Auth
    # =========================

    def is_token_valid(self) -> bool:
        """
        Check whether the OAuth token is still valid.
        """
        return self._core.is_token_valid()
