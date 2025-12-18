from __future__ import annotations

from email_integration.domain.interfaces.base_provider import BaseEmailProvider
from email_integration.domain.models.email_message import EmailMessage
from email_integration.domain.models.email_detail import EmailDetail
from email_integration.domain.models.attachment import Attachment
from email_integration.domain.models.folders import MailFolder
from email_integration.domain.models.email_filter import EmailSearchFilter


class EmailCore:
    """
    Core orchestrator for read-only email operations.

    Responsibilities:
    - Orchestrates calls to the email provider
    - Enforces provider-agnostic behavior
    - Contains NO Gmail / Outlook specific logic
    - Contains NO framework or API layer logic

    This class is INTERNAL and should not be used directly
    by consuming applications.
    """

    def __init__(self, provider: BaseEmailProvider) -> None:
        self._provider = provider

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
        Fetch a page of emails from a folder with optional filters.
        """

        return self._provider.fetch_emails(
            page_size=page_size,
            cursor=cursor,
            folder=folder,
            filters=filters,
        )

    # =========================
    # Email Detail
    # =========================

    def fetch_email_detail(
        self,
        *,
        message_id: str,
    ) -> EmailDetail:
        """
        Fetch full details of a single email.
        """
        return self._provider.fetch_email_detail(
            message_id=message_id,
        )

    # =========================
    # Folders
    # =========================

    def list_folders(self) -> list[MailFolder]:
        """
        List supported default folders.
        """
        return self._provider.list_folders()

    # =========================
    # Attachments
    # =========================

    def list_attachments(
        self,
        *,
        message_id: str,
    ) -> list[Attachment]:
        """
        List attachments for an email.
        """
        return self._provider.list_attachments(
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
        return self._provider.download_attachment(
            message_id=message_id,
            attachment_id=attachment_id,
        )

    # =========================
    # Health / Auth
    # =========================

    def is_token_valid(self) -> bool:
        """
        Check whether the provider token is still valid.
        """
        return self._provider.is_token_valid()
