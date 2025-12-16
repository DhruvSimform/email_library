from __future__ import annotations

from datetime import datetime
from typing import Any

from .folders import MailFolder
from .attachment import Attachment

class EmailMessage:
    """
    Domain model representing a read-only email summary.

    Used for inbox / list views.
    Provider-agnostic.
    Immutable after creation.
    """

    __slots__ = (
        "message_id",
        "subject",
        "sender",
        "timestamp",
        "preview",
        "folder",
        "attachments",
    )

    def __init__(
        self,
        *,
        message_id: str,
        subject: str,
        sender: str,
        timestamp: datetime,
        preview: str,
        folder: MailFolder,
        attachments: list[Attachment],
    ) -> None:
        object.__setattr__(self, "message_id", message_id)
        object.__setattr__(self, "subject", subject)
        object.__setattr__(self, "sender", sender)
        object.__setattr__(self, "timestamp", timestamp)
        object.__setattr__(self, "preview", preview)
        object.__setattr__(self, "folder", folder)
        object.__setattr__(
            self,
            "attachments",
            tuple(attachments),  # enforce immutability
        )

    # -------------------------
    # Immutability
    # -------------------------

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("EmailMessage is immutable")

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
            "folder": self.folder.value,
            "attachments": [
                attachment.to_dict() for attachment in self.attachments
            ],
            "has_attachments": bool(self.attachments),
            "attachment_count": len(self.attachments),
        }