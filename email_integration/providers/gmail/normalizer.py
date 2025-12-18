from __future__ import annotations

import base64
from datetime import datetime, timezone

from email_integration.domain.models.email_message import EmailMessage
from email_integration.domain.models.email_detail import EmailDetail
from email_integration.domain.models.attachment import Attachment
from email_integration.domain.models.folders import MailFolder


class GmailNormalizer:
    """
    Converts Gmail API responses into domain models.
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
        headers = {
            h["name"].lower(): h["value"]
            for h in raw.get("payload", {}).get("headers", [])
        }

        attachments = GmailNormalizer.extract_attachments(raw)

        # Gmail label-based inbox classification
        label_ids = raw.get("labelIds", [])
        if "CATEGORY_PROMOTIONS"  in label_ids or "CATEGORY_SOCIAL" in label_ids:
            inbox_classification = "other"
        else:
            inbox_classification = "primary"

        return EmailMessage(
            message_id=raw["id"],
            subject=headers.get("subject", ""),
            sender=headers.get("from", ""),
            timestamp = datetime.fromtimestamp(
                int(raw["internalDate"]) / 1000,
                tz=timezone.utc,
            ),
            preview=raw.get("snippet", ""),
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
        headers = {
            h["name"].lower(): h["value"]
            for h in raw.get("payload", {}).get("headers", [])
        }

        body_text = ""
        body_html: str | None = None

        def walk(parts: list[dict]) -> None:
            nonlocal body_text, body_html

            for part in parts:
                data = part.get("body", {}).get("data")
                if data:
                    decoded = base64.urlsafe_b64decode(
                        data
                    ).decode("utf-8", errors="ignore")

                    match part.get("mimeType"):
                        case "text/plain":
                            body_text = decoded
                        case "text/html":
                            body_html = decoded

                if "parts" in part:
                    walk(part["parts"])

        walk(raw.get("payload", {}).get("parts", []))

        return EmailDetail(
            message_id=raw["id"],
            subject=headers.get("subject", ""),
            sender=headers.get("from", ""),
            recipients=headers.get("to", "").split(", "),
            timestamp = datetime.fromtimestamp(
                int(raw["internalDate"]) / 1000,
                tz=timezone.utc,
            ),
            body_text=body_text,
            body_html=body_html,
            attachments=attachments,
        )

    # -------------------------
    # Attachments
    # -------------------------

    @staticmethod
    def extract_attachments(raw: dict) -> list[Attachment]:
        attachments: list[Attachment] = []

        def walk(parts: list[dict]) -> None:
            for part in parts:
                body = part.get("body", {})

                if part.get("filename") and body.get("attachmentId"):
                    attachments.append(
                        Attachment(
                            attachment_id=body["attachmentId"],
                            filename=part["filename"],
                            size_bytes=body.get("size", 0),
                            mime_type=part.get("mimeType", ""),
                        )
                    )

                if "parts" in part:
                    walk(part["parts"])

        walk(raw.get("payload", {}).get("parts", []))
        return attachments
