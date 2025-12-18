from __future__ import annotations

import requests
from requests.exceptions import RequestException, HTTPError

from email_integration.domain.interfaces.base_provider import BaseEmailProvider
from email_integration.domain.models.email_message import EmailMessage
from email_integration.domain.models.email_detail import EmailDetail
from email_integration.domain.models.attachment import Attachment
from email_integration.domain.models.folders import MailFolder
from email_integration.domain.models.email_filter import EmailSearchFilter

from email_integration.exceptions.auth import InvalidAccessTokenError
from email_integration.exceptions.provider import OutlookAPIError
from email_integration.exceptions.attachment import AttachmentTooLargeError
from email_integration.exceptions.network import NetworkTimeoutError
from email_integration.providers.registry import ProviderRegistry

from .normalizer import OutlookNormalizer
from .folder_mapping import OUTLOOK_FOLDER_MAP
from .query_builder import OutlookQueryBuilder


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
        headers: dict | None = None,
    ) -> dict:
        url = f"{GRAPH_API_BASE_URL}{endpoint}"
        return self._make_request_url(url, method, params, timeout, headers)

    def _make_request_url(
        self,
        url: str,
        method: str = "GET",
        params: dict | None = None,
        timeout: int = 30,
        headers: dict | None = None,
    ) -> dict:
        """
        IMPORTANT:
        - When calling @odata.nextLink, params MUST be None
        - nextLink URLs are opaque and must be used as-is
        """
        request_headers = headers if headers is not None else self.headers
        
        try:
            if params is None:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=request_headers,
                    timeout=timeout,
                )
            else:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=request_headers,
                    params=params,
                    timeout=timeout,
                )

            response.raise_for_status()
            
            try:
                return response.json()
            except ValueError as exc:
                raise OutlookAPIError(
                    "Invalid JSON response from API"
                ) from exc

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

    def _build_outlook_endpoint(self, folder: MailFolder | None) -> str:
        """
        Builds the correct Outlook endpoint based on folder.
        """
        if folder is None:
            return "/me/messages"

        if folder not in OUTLOOK_FOLDER_MAP:
            return "/me/messages"

        return f"/me/mailFolders/{OUTLOOK_FOLDER_MAP[folder]}/messages"

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

    def fetch_emails(
        self,
        *,
        page_size: int = 10,
        cursor: str | None = None,
        folder: MailFolder | None = None,
        filters: EmailSearchFilter | None = None,
    ) -> tuple[list[EmailMessage], str | None]:

        page_size = max(1, min(page_size, 100))
        # =========================
        # Pagination via nextLink
        # =========================
        if cursor and self._is_valid_nextlink(cursor):
            response = self._make_request_url(cursor)

        else:
            endpoint = self._build_outlook_endpoint(folder)

            params = {
                "$top": page_size,
                "$select": (
                    "id,subject,from,receivedDateTime,"
                    "bodyPreview,hasAttachments,"
                    "inferenceClassification"
                ),
                "$expand": "attachments($select=id,name,size,contentType)",
            }

            # -------------------------
            # Apply filters
            # -------------------------

            special_filters: list[str] = []
            if folder == MailFolder.INBOX:
                special_filters.append("InferenceClassification eq 'Focused'")
            if folder == MailFolder.STARRED:
                special_filters.append("flag/flagStatus eq 'flagged'")
            headers = None

            # QueryBuilder auto-generates $orderby from active filter fields
            filter_params = OutlookQueryBuilder.build(
                filters or EmailSearchFilter(), 
                special_filters=special_filters if special_filters else None
            )

            # $search requires ConsistencyLevel header
            if "$search" in filter_params:
                headers = dict(self.headers)
                headers["ConsistencyLevel"] = "eventual"

            params.update(filter_params)
            response = self._make_request("GET", endpoint, params, headers=headers)

        # =========================
        # Normalize results
        # =========================
        try:
            emails: list[EmailMessage] = []
            for msg_data in response.get("value", []):
                emails.append(
                    OutlookNormalizer.to_email_message(
                        msg_data,
                        folder=folder,
                    )
                )
        except (InvalidAccessTokenError, NetworkTimeoutError):
            raise
        except Exception as exc:
            raise OutlookAPIError("Failed to process email results") from exc

        next_cursor = response.get("@odata.nextLink")
        return emails, next_cursor
    
    # -------------------------
    # Email detail
    # -------------------------

    def fetch_email_detail(
        self,
        *,
        message_id: str,
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

        try:
            attachments = OutlookNormalizer.extract_attachments(raw)
            return OutlookNormalizer.to_email_detail(
                raw,
                attachments=attachments,
            )
        except (InvalidAccessTokenError, NetworkTimeoutError):
            raise
        except Exception as exc:
            raise OutlookAPIError("Failed to parse email detail") from exc

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

        try:
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
        except (InvalidAccessTokenError, NetworkTimeoutError):
            raise
        except Exception as exc:
            raise OutlookAPIError("Failed to parse attachments") from exc

        return attachments

    def download_attachment(
        self,
        *,
        message_id: str,
        attachment_id: str,
    ) -> bytes:
        """
        Download attachment content from Outlook (Microsoft Graph).

        Notes:
        - Do NOT use $select=contentBytes (Graph limitation)
        - contentBytes is only available on fileAttachment
        """

        endpoint = f"/me/messages/{message_id}/attachments/{attachment_id}"
        attachment_data = self._make_request("GET", endpoint)

        try:
            if attachment_data.get("@odata.type") != "#microsoft.graph.fileAttachment":
                raise OutlookAPIError("Unsupported attachment type")

            size = attachment_data.get("size", 0)
            if size > MAX_ATTACHMENT_SIZE_BYTES:
                raise AttachmentTooLargeError("Attachment too large")

            content_bytes = attachment_data.get("contentBytes")
            if not content_bytes:
                raise OutlookAPIError("Attachment content missing")

            return OutlookNormalizer.parse_attachment_content(attachment_data)
        except (InvalidAccessTokenError, NetworkTimeoutError, OutlookAPIError, AttachmentTooLargeError):
            raise
        except Exception as exc:
            raise OutlookAPIError("Failed to download attachment") from exc

ProviderRegistry.register("outlook", OutlookProvider)