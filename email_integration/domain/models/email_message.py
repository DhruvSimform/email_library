from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable, Literal

from .attachment import Attachment
from .folders import MailFolder

InboxClassification = Literal["primary", "other"]


@dataclass(frozen=True, slots=True, kw_only=True)
class EmailMessage:
    """
    Domain model representing a read-only email summary.

    Used for inbox / list views.
    Provider-agnostic.
    Immutable after creation.
    """

    message_id: str
    subject: str
    sender: str
    timestamp: datetime
    preview: str
    folder: MailFolder
    attachments: Iterable[Attachment]

    # Inbox classification (provider-specific metadata)
    # Gmail   → "primary"
    # Outlook → "focused" | "other"
    inbox_classification: InboxClassification | None = None

    def __post_init__(self) -> None:
        # Normalize to tuple to guarantee immutability
        object.__setattr__(self, "attachments", tuple(self.attachments))

    # -------------------------
    # Serialization
    # -------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "message_id": self.message_id,
            "subject": self.subject,
            "sender": self.sender,
            "timestamp": self.timestamp.isoformat(),
            "preview": self.preview,
            "folder": self.folder.value if self.folder else None,
            "inbox_classification": self.inbox_classification,
            "attachments": [
                attachment.to_dict() for attachment in self.attachments
            ],
            "has_attachments": bool(self.attachments),
            "attachment_count": len(self.attachments),
        }
