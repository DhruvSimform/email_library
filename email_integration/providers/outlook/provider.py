from __future__ import annotations

import requests
from requests.exceptions import RequestException, HTTPError

from email_integration.domain.interfaces.base_provider import BaseEmailProvider
from email_integration.domain.models.email_message import EmailMessage
from email_integration.domain.models.email_detail import EmailDetail
from email_integration.domain.models.attachment import Attachment
from email_integration.domain.models.folders import MailFolder

from email_integration.exceptions.auth import InvalidAccessTokenError
from email_integration.exceptions.provider import OutlookAPIError
from email_integration.exceptions.attachment import AttachmentTooLargeError
from email_integration.exceptions.network import NetworkTimeoutError

from .normalizer import OutlookNormalizer
from .folder_mapping import OUTLOOK_FOLDER_MAP


MAX_ATTACHMENT_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB
GRAPH_API_BASE_URL = "https://graph.microsoft.com/v1.0"


class OutlookProvider(BaseEmailProvider):
    """
    Outlook read-only provider (adapter) using Microsoft Graph API.
    """

    def __init__(self, access_token: str) -> None:
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    # -------------------------
    # Internal
    # -------------------------

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: dict | None = None,
        timeout: int = 30,
    ) -> dict:
        url = f"{GRAPH_API_BASE_URL}{endpoint}"
        return self._make_request_url(url, method, params, timeout)

    def _make_request_url(
        self,
        url: str,
        method: str = "GET",
        params: dict | None = None,
        timeout: int = 30,
    ) -> dict:
        """
        IMPORTANT:
        - When calling @odata.nextLink, params MUST be None
        - nextLink URLs are opaque and must be used as-is
        """
        try:
            if params is None:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    timeout=timeout,
                )
            else:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    params=params,
                    timeout=timeout,
                )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout as exc:
            raise NetworkTimeoutError("Request timed out") from exc

        except HTTPError as exc:
            if exc.response.status_code == 401:
                raise InvalidAccessTokenError(
                    "Access token expired or invalid"
                ) from exc
            raise OutlookAPIError(
                f"HTTP {exc.response.status_code}: {exc.response.text}"
            ) from exc

        except RequestException as exc:
            raise OutlookAPIError(f"Request failed: {str(exc)}") from exc

    def _is_valid_nextlink(self, cursor: str) -> bool:
        if not cursor or not isinstance(cursor, str):
            return False

        return (
            cursor.startswith("https://graph.microsoft.com/")
            and "/messages" in cursor
            and ("$" in cursor or "%24" in cursor)
        )

    # -------------------------
    # Token
    # -------------------------

    def is_token_valid(self) -> bool:
        try:
            self._make_request("GET", "/me")
            return True
        except InvalidAccessTokenError:
            return False
        except OutlookAPIError:
            return False

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

        page_size = max(1, min(page_size, 100))

        if cursor and self._is_valid_nextlink(cursor):
            response = self._make_request_url(cursor)
        else:
            folder_name = OUTLOOK_FOLDER_MAP[folder]
            endpoint = f"/me/mailFolders/{folder_name}/messages"

            params = {
                "$top": page_size,
                "$select": (
                    "id,subject,from,receivedDateTime,"
                    "bodyPreview,hasAttachments"
                ),
                "$expand": "attachments($select=id,name,size,contentType)",
                "$orderby": "receivedDateTime desc",
            }

            response = self._make_request("GET", endpoint, params)

        emails: list[EmailMessage] = []

        for msg_data in response.get("value", []):
            emails.append(
                OutlookNormalizer.to_email_message(
                    msg_data,
                    folder=folder,
                )
            )

        next_cursor = response.get("@odata.nextLink")

        return emails, next_cursor

    # -------------------------
    # Email detail
    # -------------------------

    def fetch_email_detail(
        self,
        *,
        message_id: str,
        folder: MailFolder = MailFolder.INBOX,
    ) -> EmailDetail:

        endpoint = f"/me/messages/{message_id}"
        params = {
            "$expand": "attachments",
            "$select": (
                "id,subject,from,toRecipients,"
                "receivedDateTime,body,bodyPreview,attachments"
            ),
        }

        raw = self._make_request("GET", endpoint, params)

        attachments = OutlookNormalizer.extract_attachments(raw)

        return OutlookNormalizer.to_email_detail(
            raw,
            folder=folder,
            attachments=attachments,
        )

    # -------------------------
    # Folders
    # -------------------------

    def list_folders(self) -> list[MailFolder]:
        return list(OUTLOOK_FOLDER_MAP.keys())

    # -------------------------
    # Attachments
    # -------------------------

    def list_attachments(
        self,
        *,
        message_id: str,
    ) -> list[Attachment]:

        endpoint = f"/me/messages/{message_id}/attachments"
        params = {
            "$select": "id,name,size,contentType",
        }

        response = self._make_request("GET", endpoint, params)

        attachments: list[Attachment] = []

        for attachment_data in response.get("value", []):
            attachments.append(
                Attachment(
                    attachment_id=attachment_data.get("id", ""),
                    filename=attachment_data.get("name", ""),
                    size_bytes=attachment_data.get("size", 0),
                    mime_type=attachment_data.get("contentType", ""),
                )
            )

        return attachments

    def download_attachment(
        self,
        *,
        message_id: str,
        attachment_id: str,
    ) -> bytes:

        endpoint = f"/me/messages/{message_id}/attachments/{attachment_id}"
        params = {
            "$select": "contentBytes,size",
        }

        attachment_data = self._make_request("GET", endpoint, params)

        size = attachment_data.get("size", 0)
        if size > MAX_ATTACHMENT_SIZE_BYTES:
            raise AttachmentTooLargeError("Attachment too large")

        content_bytes = attachment_data.get("contentBytes")
        if not content_bytes:
            raise OutlookAPIError("Attachment content missing")

        return OutlookNormalizer.parse_attachment_content(attachment_data)
