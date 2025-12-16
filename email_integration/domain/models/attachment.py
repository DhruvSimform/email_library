from __future__ import annotations

from typing import Any


class Attachment:
    """
    Read-only attachment metadata.

    Used for listing and validating attachments
    before download.
    Immutable after creation.
    """

    __slots__ = (
        "attachment_id",
        "filename",
        "size_bytes",
        "mime_type",
    )

    def __init__(
        self,
        *,
        attachment_id: str,
        filename: str,
        size_bytes: int,
        mime_type: str,
    ) -> None:
        object.__setattr__(self, "attachment_id", attachment_id)
        object.__setattr__(self, "filename", filename)
        object.__setattr__(self, "size_bytes", size_bytes)
        object.__setattr__(self, "mime_type", mime_type)

    # -------------------------
    # Immutability
    # -------------------------

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("Attachment is immutable")

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

    # -------------------------
    # Equality / Hash / Debug
    # -------------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Attachment):
            return False
        return self.attachment_id == other.attachment_id

    def __hash__(self) -> int:
        return hash(self.attachment_id)

    def __repr__(self) -> str:
        return (
            f"Attachment("
            f"id={self.attachment_id!r}, "
            f"filename={self.filename!r}, "
            f"size_bytes={self.size_bytes}, "
            f"mime_type={self.mime_type!r}"
            f")"
        )
