from __future__ import annotations

import base64

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from email_integration.core.constant import (DEFAULT_PAGE_SIZE,
                                             GOOGLE_OAUTH_SCOPE_GMAIL_READONLY,
                                             MAX_ATTACHMENT_SIZE_BYTES,
                                             MAX_PAGE_SIZE, MIN_PAGE_SIZE)
from email_integration.domain.interfaces.base_provider import BaseEmailProvider
from email_integration.domain.models.attachment import Attachment
from email_integration.domain.models.email_detail import EmailDetail
from email_integration.domain.models.email_filter import EmailSearchFilter
from email_integration.domain.models.email_message import EmailMessage
from email_integration.domain.models.folders import MailFolder
from email_integration.exceptions.attachment import AttachmentTooLargeError
from email_integration.exceptions.auth import InvalidAccessTokenError
from email_integration.exceptions.network import NetworkTimeoutError
from email_integration.exceptions.provider import GmailAPIError
from email_integration.providers.registry import ProviderRegistry

from .folder_mapping import GMAIL_FOLDER_MAP
from .normalizer import GmailNormalizer
from .query_builder import GmailQueryBuilder


class GmailProvider(BaseEmailProvider):
    """
    Gmail read-only provider (adapter).
    """

    def __init__(self) -> None:
        self._client = None

    def set_credentials(self, access_token: str) -> None:
        """
        Set or update OAuth credentials.

        Args:
            access_token: Google OAuth access token

        Raises:
            InvalidAccessTokenError: If token format is invalid
        """
        if not access_token or not isinstance(access_token, str):
            raise InvalidAccessTokenError("Access token must be a non-empty string")
        
        self._client = self._build_client(access_token)

    # -------------------------
    # Internal
    # -------------------------

    def _build_client(self, token: str):
        """Build Gmail API client from access token"""
        try:
            credentials = Credentials(
                token=token,
                scopes=[GOOGLE_OAUTH_SCOPE_GMAIL_READONLY],
            )
            return build("gmail", "v1", credentials=credentials)
        except Exception as exc:  # noqa: BLE001 (intentional boundary)
            raise InvalidAccessTokenError("Invalid Gmail token")

    # -------------------------
    # Token
    # -------------------------

    def is_token_valid(self) -> bool:
        try:
            self._client.users().getProfile(userId="me").execute()
            return True
        except TimeoutError as exc:
            raise NetworkTimeoutError() from exc
        except HttpError as exc:
            if exc.resp.status == 401:
                return False
            raise GmailAPIError(exc.reason) from exc

    # -------------------------
    # Inbox
    # -------------------------

    def fetch_emails(
        self,
        *,
        page_size: int = DEFAULT_PAGE_SIZE,
        cursor: str | None = None,
        folder: MailFolder | None = None,
        filters: EmailSearchFilter | None = None,
    ) -> tuple[list[EmailMessage], str | None]:
        
        page_size = max(MIN_PAGE_SIZE, min(page_size, MAX_PAGE_SIZE))
        label = None
        if folder:
            try:
                label = GMAIL_FOLDER_MAP[folder]
            except KeyError:
                raise GmailAPIError(f"Folder '{folder}' not supported in Gmail")

        query: str | None = None
        if filters:
            query = GmailQueryBuilder.build(filters)

        try:
            response = (
                self._client.users()
                .messages()
                .list(
                    userId="me",
                    labelIds=[label] if label else None,
                    q=query,
                    maxResults=page_size,
                    pageToken=cursor,
                )
                .execute()
            )
        except TimeoutError as exc:
            raise NetworkTimeoutError() from exc
        except HttpError as exc:
            if exc.resp.status == 401:
                raise InvalidAccessTokenError("Access token expired")
            raise GmailAPIError(exc.reason) from exc

        emails: list[EmailMessage] = []

        for msg in response.get("messages", []):
            try:
                raw = (
                    self._client.users()
                    .messages()
                    .get(
                        userId="me",
                        id=msg["id"],
                        format="full",
                        metadataHeaders=["Subject", "From"],
                    )
                    .execute()
                )
            except TimeoutError as exc:
                raise NetworkTimeoutError() from exc
            except HttpError as exc:
                raise GmailAPIError(exc.reason) from exc

            emails.append(
                GmailNormalizer.to_email_message(
                    raw,
                    folder=folder,
                )
            )

        return emails, response.get("nextPageToken")

    # -------------------------
    # Email detail
    # -------------------------

    def fetch_email_detail(
        self,
        *,
        message_id: str,
    ) -> EmailDetail:

        try:
            raw = (
                self._client.users()
                .messages()
                .get(
                    userId="me",
                    id=message_id,
                    format="full",
                )
                .execute()
            )
        except TimeoutError as exc:
            raise NetworkTimeoutError() from exc
        except HttpError as exc:
            if exc.resp.status == 401:
                raise InvalidAccessTokenError("Access token expired") from exc
            raise GmailAPIError(exc.reason) from exc

        attachments = GmailNormalizer.extract_attachments(raw)

        return GmailNormalizer.to_email_detail(
            raw,
            attachments=attachments,
        )

    # -------------------------
    # Folders
    # -------------------------

    def list_folders(self) -> list[MailFolder]:
        return list(GMAIL_FOLDER_MAP.keys())

    # -------------------------
    # Attachments
    # -------------------------

    def list_attachments(
        self,
        *,
        message_id: str,
    ) -> list[Attachment]:

        try:
            raw = (
                self._client.users()
                .messages()
                .get(userId="me", id=message_id)
                .execute()
            )
        except TimeoutError as exc:
            raise NetworkTimeoutError() from exc
        except HttpError as exc:
            raise GmailAPIError(exc.reason) from exc

        return GmailNormalizer.extract_attachments(raw)

    def download_attachment(
        self,
        *,
        message_id: str,
        attachment_id: str,
    ) -> bytes:

        try:
            attachment = (
                self._client.users()
                .messages()
                .attachments()
                .get(
                    userId="me",
                    messageId=message_id,
                    id=attachment_id,
                )
                .execute()
            )
        except TimeoutError as exc:
            raise NetworkTimeoutError() from exc
        except HttpError as exc:
            raise GmailAPIError(exc.reason) from exc

        data = attachment.get("data")
        if not data:
            raise GmailAPIError("Attachment data missing")

        content = base64.urlsafe_b64decode(data)

        if len(content) > MAX_ATTACHMENT_SIZE_BYTES:
            raise AttachmentTooLargeError("Attachment too large")

        return content
    
    def __repr__(self):
        return "GmailProvider()"

ProviderRegistry.register("gmail", GmailProvider)