from __future__ import annotations

from email_integration.domain.models.email_filter import EmailSearchFilter
from email_integration.domain.models.folders import (
    MailFolder,
)

from .folder_mapping import (GMAIL_FOLDER_MAP)


class GmailQueryBuilder:
    """
    Translates provider-agnostic EmailSearchFilter
    into Gmail search query syntax.
    """

    @staticmethod
    def build(filters: EmailSearchFilter) -> str | None:
        query: list[str] = []

        # =========================
        # Folder constraint (Gmail)
        # =========================
        if filters.folder and filters.folder in GMAIL_FOLDER_MAP:
            gmail_label = GMAIL_FOLDER_MAP[filters.folder]
            query.append(f"in:{gmail_label.lower()}")

        # =========================
        # Address-based filters
        # =========================
        if filters.from_address:
            query.append(f"from:{filters.from_address}")

        if filters.to_addresses:
            for address in filters.to_addresses:
                query.append(f"to:{address}")

        # =========================
        # Content-based filters
        # =========================
        if filters.subject_contains:
            query.append(f"subject:{filters.subject_contains}")

        if filters.body_contains:
            query.append(filters.body_contains)

        if filters.has_words:
            query.extend(filters.has_words)

        # =========================
        # Attachment-based filters
        # =========================
        if filters.has_attachments is True:
            query.append("has:attachment")

        # =========================
        # Read / unread state
        # =========================
        if filters.is_read is True:
            query.append("is:read")
        elif filters.is_read is False:
            query.append("is:unread")

        # =========================
        # Date-based filters
        # =========================
        if filters.start_date:
            query.append(f"after:{int(filters.start_date.timestamp())}")

        if filters.end_date:
            query.append(f"before:{int(filters.end_date.timestamp())}")

        return " ".join(query) if query else None