from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

from .folders import MailFolder
from .attachment import Attachment


class EmailDetail:
    """
    Domain model representing a full, read-only email.

    Used when a user opens an email.
    Provider-agnostic (Gmail / Outlook).
    Immutable after creation.
    """

    __slots__ = (
        "message_id",
        "subject",
        "sender",
        "recipients",
        "timestamp",
        "body_text",
        "body_html",
        "folder",
        "attachments",
    )

    def __init__(
        self,
        *,
        message_id: str,
        subject: str,
        sender: str,
        recipients: Iterable[str],
        timestamp: datetime,
        body_text: str,
        body_html: str | None,
        folder: MailFolder,
        attachments: Iterable[Attachment],
    ) -> None:
        object.__setattr__(self, "message_id", message_id)
        object.__setattr__(self, "subject", subject)
        object.__setattr__(self, "sender", sender)
        object.__setattr__(self, "recipients", tuple(recipients))
        object.__setattr__(self, "timestamp", timestamp)
        object.__setattr__(self, "body_text", body_text)
        object.__setattr__(self, "body_html", body_html)
        object.__setattr__(self, "folder", folder)
        object.__setattr__(self, "attachments", tuple(attachments))

    # -------------------------
    # Immutability
    # -------------------------

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("EmailDetail is immutable")

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
            "folder": self.folder.value,
            "attachments": [
                attachment.to_dict() for attachment in self.attachments
            ],
        }

    # -------------------------
    # Equality / Hash / Debug
    # -------------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EmailDetail):
            return False
        return self.message_id == other.message_id

    def __hash__(self) -> int:
        return hash(self.message_id)

    def __repr__(self) -> str:
        return (
            f"EmailDetail("
            f"id={self.message_id!r}, "
            f"subject={self.subject!r}, "
            f"sender={self.sender!r}, "
            f"timestamp={self.timestamp.isoformat()}, "
            f"folder={self.folder.value!r}, "
            f"attachments={len(self.attachments)}"
            f")"
        )
