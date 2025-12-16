from typing import List, Optional, Tuple

from email_integration.domain.models.email_message import EmailMessage
from email_integration.domain.models.email_detail import EmailDetail
from email_integration.domain.models.attachment import Attachment
from email_integration.domain.models.folders import MailFolder

from email_integration.services.email_core import EmailCore
from email_integration.providers.gmail.provider import GmailProvider
from email_integration.providers.outlook.provider import OutlookProvider


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
    ):
        provider = provider.lower()

        if provider == "gmail":
            provider_instance = GmailProvider(access_token)
        elif provider == "outlook":
            provider_instance = OutlookProvider(access_token)
        else:
            raise ValueError(f"Unsupported provider: {provider}")

        self._core = EmailCore(provider_instance)

    # =========================
    # Inbox
    # =========================

    def get_inbox(
        self,
        *,
        page_size: int = 10,
        cursor: Optional[str] = None,
        folder: MailFolder = MailFolder.INBOX,
    ) -> Tuple[List[EmailMessage], Optional[str]]:
        """
        Fetch inbox emails with pagination.
        """
        return self._core.fetch_inbox(
            page_size=page_size,
            cursor=cursor,
            folder=folder,
        )

    # =========================
    # Email Detail
    # =========================

    def get_email_detail(
        self,
        *,
        message_id: str,
        folder: MailFolder = MailFolder.INBOX,
    ) -> EmailDetail:
        """
        Fetch full details of a single email.
        """
        return self._core.fetch_email_detail(
            message_id=message_id,
            folder=folder,
        )

    # =========================
    # Folders
    # =========================

    def get_folders(self) -> List[MailFolder]:
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
    ) -> List[Attachment]:
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
