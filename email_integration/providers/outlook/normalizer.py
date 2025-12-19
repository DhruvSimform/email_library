from __future__ import annotations

import base64
from datetime import datetime, timezone
from typing import Any

from email_integration.domain.models.attachment import Attachment
from email_integration.domain.models.email_detail import EmailDetail
from email_integration.domain.models.email_message import EmailMessage
from email_integration.domain.models.folders import MailFolder

def _parse_recipients(items: list[dict] | None) -> list[str]:
    if not items:
        return []

    result: list[str] = []
    for item in items:
        email_data = item.get("emailAddress")
        if not email_data:
            continue

        name = email_data.get("name", "")
        email = email_data.get("address", "")
        result.append(f"{name} <{email}>" if name else email)

    return result

class OutlookNormalizer:
    """
    Converts Outlook Graph API responses into domain models.
    """

    # -------------------------
    # Inbox message
    # -------------------------

    @staticmethod
    def to_email_message(
        raw: dict,
        *,
        folder: MailFolder,
    ) -> EmailMessage:
        """
        Convert Outlook Graph API message to EmailMessage domain model.
        """
        # Extract sender information
        sender = ""
        if raw.get("from") and raw["from"].get("emailAddress"):
            sender_name = raw["from"]["emailAddress"].get("name", "")
            sender_email = raw["from"]["emailAddress"].get("address", "")
            sender = f"{sender_name} <{sender_email}>" if sender_name else sender_email

        # Parse timestamp
        timestamp = datetime.fromisoformat(
                raw["receivedDateTime"].replace("Z", "+00:00")
        ).astimezone(timezone.utc)

        # Extract attachments info (if available)
        attachments: list[Attachment] = []
        
        # Try to get attachments from expanded data first
        if raw.get("attachments"):
            for attachment in raw["attachments"]:
                attachments.append(
                    Attachment(
                        attachment_id=attachment.get("id", ""),
                        filename=attachment.get("name", ""),
                        size_bytes=attachment.get("size", 0),
                        mime_type=attachment.get("contentType", ""),
                    )
                )
        # If no expanded attachments but hasAttachments is true, create empty list
        # (attachments will be loaded when email detail is fetched)
        elif raw.get("hasAttachments", False):
            # We know there are attachments but they weren't expanded
            # Leave attachments list empty - they'll be loaded on demand
            pass

        # Outlook gives: "focused" | "other"
        raw_classification = raw.get("inferenceClassification")
        # Map to domain-level inbox classification
        inbox_classification = {"focused": "primary", "other": "other"}.get(raw_classification, "other")

        return EmailMessage(
            message_id=raw["id"],
            subject=raw.get("subject", ""),
            sender=sender,
            timestamp=timestamp,
            preview=raw.get("bodyPreview", ""),
            folder=folder,
            attachments=attachments,
            inbox_classification=inbox_classification,
        )

    # -------------------------
    # Email detail
    # -------------------------

    @staticmethod
    def to_email_detail(
        raw: dict,
        *,
        attachments: list[Attachment],
    ) -> EmailDetail:
        """
        Convert Outlook Graph API message to EmailDetail domain model.
        """
        # Extract sender information
        sender = ""
        if raw.get("from") and raw["from"].get("emailAddress"):
            sender_name = raw["from"]["emailAddress"].get("name", "")
            sender_email = raw["from"]["emailAddress"].get("address", "")
            sender = f"{sender_name} <{sender_email}>" if sender_name else sender_email

        # Extract recipients
        recipients: list[str] = _parse_recipients(raw.get("toRecipients"))
        cc: list[str] = _parse_recipients(raw.get("ccRecipients"))
        bcc: list[str] = _parse_recipients(raw.get("bccRecipients"))
       
        # Parse timestamp
        timestamp = datetime.fromisoformat(
                raw["receivedDateTime"].replace("Z", "+00:00")
        ).astimezone(timezone.utc)
        # Extract body content
        body_content = raw.get("body", {})
        body_text = ""
        body_html: str | None = None

        if body_content.get("contentType") == "text":
            body_text = body_content.get("content", "")
        elif body_content.get("contentType") == "html":
            body_html = body_content.get("content", "")
            # For HTML content, we might want to extract plain text as well
            # For simplicity, using bodyPreview as text fallback
            body_text = raw.get("bodyPreview", "")

        return EmailDetail(
            message_id=raw["id"],
            subject=raw.get("subject", ""),
            sender=sender,
            recipients=recipients,
            cc=cc,
            bcc=bcc,
            timestamp=timestamp,
            body_text=body_text,
            body_html=body_html,
            attachments=attachments,
        )

    # -------------------------
    # Attachments
    # -------------------------

    @staticmethod
    def extract_attachments(raw: dict) -> list[Attachment]:
        """
        Extract attachment metadata from Outlook Graph API message.
        """
        attachments: list[Attachment] = []
        
        if raw.get("attachments"):
            for attachment in raw["attachments"]:
                attachments.append(
                    Attachment(
                        attachment_id=attachment.get("id", ""),
                        filename=attachment.get("name", ""),
                        size_bytes=attachment.get("size", 0),
                        mime_type=attachment.get("contentType", ""),
                    )
                )
        
        return attachments

    @staticmethod
    def parse_attachment_content(raw_attachment: dict) -> bytes:
        """
        Parse attachment content from Outlook Graph API response.
        """
        content_bytes = raw_attachment.get("contentBytes")
        if content_bytes:
            return base64.b64decode(content_bytes)
        return b""