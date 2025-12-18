from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class Attachment:
    """
    Read-only attachment metadata.

    Used for listing and validating attachments
    before download.
    Immutable after creation.
    """

    attachment_id: str
    filename: str
    size_bytes: int
    mime_type: str

    # -------------------------
    # Convenience helpers
    # -------------------------

    @property
    def size_kb(self) -> float:
        return round(self.size_bytes / 1024, 2)

    @property
    def size_mb(self) -> float:
        return round(self.size_bytes / (1024 * 1024), 2)

    # -------------------------
    # Serialization
    # -------------------------

    def to_dict(self) -> dict[str, Any]:
        return {
            "attachment_id": self.attachment_id,
            "filename": self.filename,
            "size_bytes": self.size_bytes,
            "mime_type": self.mime_type,
        }
