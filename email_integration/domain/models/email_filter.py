from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from email_integration.exceptions.filter import InvalidFilterError

from .folders import MailFolder


@dataclass(frozen=True, slots=True, kw_only=True)
class EmailSearchFilter:
    """
    Provider-agnostic email search filter.

    Represents common advanced-search fields
    across Gmail and Outlook.

    Design principles:
    - All fields are OPTIONAL
    - No provider-specific syntax
    - Immutable & safe to reuse
    - Providers translate this into native query formats
    """

    # =========================
    # Address-based filters
    # =========================
    # Used to filter emails by sender and recipients
    # Example:
    #   Gmail → from:user@example.com
    #   Outlook → from/emailAddress/address eq 'user@example.com'
    from_address: str | None = None
    to_addresses: Iterable[str] | None = None


    # =========================
    # Content-based filters
    # =========================
    # Used for full-text and subject/body matching
    # Examples:
    #   subject_contains="invoice"
    #   has_words=["urgent", "action"]
    subject_contains: str | None = None
    body_contains: str | None = None
    has_words: Iterable[str] | None = None

    # =========================
    # Date-based filters
    # =========================
    # Filters emails within a time range
    # Example:
    #   start_date = 2024-01-01
    #   end_date   = 2024-01-31
    start_date: datetime | None = None
    end_date: datetime | None = None

    # =========================
    # Attachment-based filters
    # =========================
    # Used to restrict emails with attachments
    # Providers translate to their supported units
    has_attachments: bool | None = None
   
    # =========================
    # Read / unread state filters
    # =========================
    # Used to filter emails by read status
    # Example:
    #   is_read=True  → read emails
    #   is_read=False → unread emails
    is_read: bool | None = None

    # =========================
    # Folder constraint (optional) not using as we are passing folder separately,
    # consider it as navigational parameter
    # =========================
    # Narrows search to a specific folder
    # Acts as a search constraint, not navigation
    # Example:
    #   folder=MailFolder.SENT
    # folder: MailFolder | None = None

    def __post_init__(self) -> None:
        # ========================
        # Email address validations
        # ========================
        if self.from_address is not None:
            if "@" not in self.from_address:
                raise InvalidFilterError("from_address must be a valid email format")
        
        if self.to_addresses is not None:
            to_list = tuple(self.to_addresses)
            for addr in to_list:
                if "@" not in addr:
                    raise InvalidFilterError(f"Invalid email format in to_addresses: {addr}")
            object.__setattr__(self, "to_addresses", to_list)
        
        # ========================
        # Date range validation
        # ========================
        if self.start_date is not None and self.end_date is not None:
            if self.start_date > self.end_date:
                raise InvalidFilterError(
                    "start_date cannot be greater than end_date"
                )
        
        # ========================
        # Normalize iterables
        # ========================
        if self.has_words is not None:
            object.__setattr__(self, "has_words", tuple(self.has_words))