from __future__ import annotations

from abc import ABC, abstractmethod

from ..models.email_message import EmailMessage
from ..models.email_detail import EmailDetail
from ..models.attachment import Attachment
from ..models.folders import MailFolder
from ..models.email_filter import EmailSearchFilter


class BaseEmailProvider(ABC):
    """
    Abstract base class for all email providers (Gmail, Outlook, etc.).

    Contract:
    - READ-ONLY access only
    - Provider-agnostic
    - Must return domain models only
    - Must NOT expose raw API payloads
    - Must raise domain-level exceptions (not SDK/API errors)

    methods:
    - fetch_emails
    - fetch_email_detail
    - list_folders
    - list_attachments
    - download_attachment
    - is_token_valid
    """

    # =========================
    # Core Inbox APIs
    # =========================

    @abstractmethod
    def fetch_emails(
        self,
        *,
        page_size: int = 10,
        cursor: str | None = None,
        folder: MailFolder | None = None,
        filters: EmailSearchFilter | None = None,
    ) -> tuple[list[EmailMessage], str | None]:
        """
        Fetch emails from a folder with pagination.

        Args:
            page_size: Number of emails per page
            cursor: Provider-specific opaque pagination cursor
            folder: Logical mail folder (INBOX, SENT, etc.)

        Returns:
            emails: List of EmailMessage
            next_cursor: Cursor for next page or None
        """
        raise NotImplementedError

    # =========================
    # Email Detail API
    # =========================

    @abstractmethod
    def fetch_email_detail(
        self,
        *,
        message_id: str,
    ) -> EmailDetail:
        """
        Fetch full details of a single email.

        Used when a user opens an email.
        """
        raise NotImplementedError

    # =========================
    # Folder / Label APIs
    # =========================

    @abstractmethod
    def list_folders(self) -> list[MailFolder]:
        """
        List default folders supported by the provider.
        ex: INBOX, SENT, DRAFTS, SPAM, TRASH

        Returns:
            List of MailFolder enums.
        """
        raise NotImplementedError

    # =========================
    # Attachment APIs
    # =========================

    @abstractmethod
    def list_attachments(
        self,
        *,
        message_id: str,
    ) -> list[Attachment]:
        """
        List attachments for a given email.

        Used to:
        - Display attachment metadata
        - Validate size before download
        """
        raise NotImplementedError

    @abstractmethod
    def download_attachment(
        self,
        *,
        message_id: str,
        attachment_id: str,
    ) -> bytes:
        """
        Download attachment bytes.

        Returns:
            Raw attachment bytes

        Raises:
            AttachmentTooLargeError
            NetworkTimeoutError
        """
        raise NotImplementedError

    # =========================
    # Token / Health APIs
    # =========================

    @abstractmethod
    def is_token_valid(self) -> bool:
        """
        Validate whether the OAuth access token is still valid.

        Used to trigger:
            OAuth token expired → Prompt re-auth
        """
        raise NotImplementedError
