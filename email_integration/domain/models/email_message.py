from __future__ import annotations

from datetime import datetime
from typing import Any

from .folders import MailFolder


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
    ) -> None:
        object.__setattr__(self, "message_id", message_id)
        object.__setattr__(self, "subject", subject)
        object.__setattr__(self, "sender", sender)
        object.__setattr__(self, "timestamp", timestamp)
        object.__setattr__(self, "preview", preview)
        object.__setattr__(self, "folder", folder)

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
        }

    # -------------------------
    # Equality / Hash / Debug
    # -------------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, EmailMessage):
            return False
        return self.message_id == other.message_id

    def __hash__(self) -> int:
        return hash(self.message_id)

    def __repr__(self) -> str:
        return (
            f"EmailMessage("
            f"id={self.message_id!r}, "
            f"subject={self.subject!r}, "
            f"sender={self.sender!r}, "
            f"timestamp={self.timestamp.isoformat()}, "
            f"folder={self.folder.value!r}"
            f")"
        )
