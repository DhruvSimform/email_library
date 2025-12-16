from __future__ import annotations

import base64

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from email_integration.domain.interfaces.base_provider import BaseEmailProvider
from email_integration.domain.models.email_message import EmailMessage
from email_integration.domain.models.email_detail import EmailDetail
from email_integration.domain.models.attachment import Attachment
from email_integration.domain.models.folders import MailFolder

from email_integration.exceptions.auth import InvalidAccessTokenError
from email_integration.exceptions.provider import GmailAPIError
from email_integration.exceptions.attachment import AttachmentTooLargeError

from .normalizer import GmailNormalizer
from .folder_mapping import GMAIL_FOLDER_MAP


MAX_ATTACHMENT_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB


class GmailProvider(BaseEmailProvider):
    """
    Gmail read-only provider (adapter).
    """

    def __init__(self, access_token: str) -> None:
        self._client = self._build_client(access_token)

    # -------------------------
    # Internal
    # -------------------------

    def _build_client(self, token: str):
        try:
            credentials = Credentials(token=token)
            return build("gmail", "v1", credentials=credentials)
        except Exception as exc:  # noqa: BLE001 (intentional boundary)
            raise InvalidAccessTokenError("Invalid Gmail token") from exc

    # -------------------------
    # Token
    # -------------------------

    def is_token_valid(self) -> bool:
        try:
            self._client.users().getProfile(userId="me").execute()
            return True
        except HttpError as exc:
            if exc.resp.status == 401:
                return False
            raise GmailAPIError(exc.reason) from exc

    # -------------------------
    # Inbox
    # -------------------------

    def fetch_inbox(
        self,
        *,
        page_size: int = 10,
        cursor: str | None = None,
        folder: MailFolder = MailFolder.INBOX,
    ) -> tuple[list[EmailMessage], str | None]:

        label = GMAIL_FOLDER_MAP[folder]

        try:
            response = (
                self._client.users()
                .messages()
                .list(
                    userId="me",
                    labelIds=[label],
                    maxResults=page_size,
                    pageToken=cursor,
                )
                .execute()
            )
        except HttpError as exc:
            if exc.resp.status == 401:
                raise InvalidAccessTokenError("Access token expired") from exc
            raise GmailAPIError(exc.reason) from exc

        emails: list[EmailMessage] = []

        for msg in response.get("messages", []):
            raw = (
                self._client.users()
                .messages()
                .get(
                    userId="me",
                    id=msg["id"],
                    format="metadata",
                    metadataHeaders=["Subject", "From"],
                )
                .execute()
            )

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
        folder: MailFolder = MailFolder.INBOX,
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
        except HttpError as exc:
            if exc.resp.status == 401:
                raise InvalidAccessTokenError("Access token expired") from exc
            raise GmailAPIError(exc.reason) from exc

        attachments = GmailNormalizer.extract_attachments(raw)

        return GmailNormalizer.to_email_detail(
            raw,
            folder=folder,
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

        raw = (
            self._client.users()
            .messages()
            .get(userId="me", id=message_id)
            .execute()
        )

        return GmailNormalizer.extract_attachments(raw)

    def download_attachment(
        self,
        *,
        message_id: str,
        attachment_id: str,
    ) -> bytes:

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

        data = attachment.get("data")
        if not data:
            raise GmailAPIError("Attachment data missing")

        content = base64.urlsafe_b64decode(data)

        if len(content) > MAX_ATTACHMENT_SIZE_BYTES:
            raise AttachmentTooLargeError("Attachment too large")

        return content
