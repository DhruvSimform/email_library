from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable

from .folders import MailFolder
from .attachment import Attachment


@dataclass(frozen=True, slots=True, kw_only=True)
class EmailDetail:
    """
    Domain model representing a full, read-only email.
    """

    message_id: str
    subject: str
    sender: str
    recipients: Iterable[str]
    timestamp: datetime
    body_text: str
    body_html: str | None
    attachments: Iterable[Attachment]

    def __post_init__(self) -> None:
        object.__setattr__(self, "recipients", tuple(self.recipients))
        object.__setattr__(self, "attachments", tuple(self.attachments))

    # -------------------------
    # Serialization
    # -------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "message_id": self.message_id,
            "subject": self.subject,
            "sender": self.sender,
            "recipients": list(self.recipients),
            "timestamp": self.timestamp.isoformat(),
            "body_text": self.body_text,
            "body_html": self.body_html,
            "attachments": [
                attachment.to_dict() for attachment in self.attachments
            ],
        }
