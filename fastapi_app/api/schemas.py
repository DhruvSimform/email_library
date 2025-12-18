from pydantic import BaseModel
from datetime import datetime


class BaseAuthRequest(BaseModel):
    provider: str
    access_token: str




class EmailSearchFilterSchema(BaseModel):
    """
    API-level schema for advanced email search filters.

    This schema is used by FastAPI to accept filter input
    from clients (UI / frontend / API consumers).

    Notes:
    - Mirrors the domain EmailSearchFilter
    - Contains no provider-specific logic
    - All fields are optional
    - Converted to domain model before use
    """

    # =========================
    # Address-based filters
    # =========================
    # Filters emails by sender and recipients
    # Example:
    #   from_address="user@example.com"
    #   to_addresses=["team@example.com", "admin@example.com"]
    from_address: str | None = None
    to_addresses: list[str] | None = None

    # =========================
    # Content-based filters
    # =========================
    # Filters emails based on subject and body content
    # Example:
    #   subject_contains="invoice"
    #   has_words=["urgent", "action"]
    subject_contains: str | None = None
    body_contains: str | None = None
    has_words: list[str] | None = None

    # =========================
    # Date-based filters
    # =========================
    # Filters emails within a specific date range
    # Example:
    #   start_date="2024-01-01T00:00:00"
    #   end_date="2024-01-31T23:59:59"
    start_date: datetime | None = None
    end_date: datetime | None = None

    # =========================
    # Attachment-based filters
    # =========================
    # Filters emails that contain attachments
    has_attachments: bool | None = None

    # =========================
    # Read / unread state filters
    # =========================
    # Filters emails by read status
    # Example:
    #   is_read=True  → read emails
    #   is_read=False → unread emails
    is_read: bool | None = None


class InboxRequest(BaseAuthRequest):
    page_size: int = 10
    cursor: str | None = None
    folder: str | None = None

    # 🔍 Advanced search filters
    filters: EmailSearchFilterSchema | None = None

class EmailDetailRequest(BaseAuthRequest):
    message_id: str


class AttachmentListRequest(BaseAuthRequest):
    message_id: str


class AttachmentDownloadRequest(BaseAuthRequest):
    message_id: str
    attachment_id: str
