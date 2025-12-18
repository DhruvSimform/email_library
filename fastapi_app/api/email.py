import base64
from fastapi import APIRouter, HTTPException

from email_integration.services.email_reader import EmailReader
from email_integration.domain.models.folders import MailFolder
from email_integration.domain.models.email_filter import EmailSearchFilter
from google.auth.exceptions import RefreshError

from email_integration.exceptions import (
    InvalidAccessTokenError,
    AttachmentTooLargeError,
    EmailIntegrationError,
    TokenRefreshError,
)

from fastapi_app.api.schemas import (
    BaseAuthRequest,
    InboxRequest,
    EmailDetailRequest,
    AttachmentListRequest,
    AttachmentDownloadRequest,
)

router = APIRouter(prefix="/email", tags=["Email"])


# =========================
# Helpers (demo-friendly)
# =========================

def get_reader(payload: BaseAuthRequest) -> EmailReader:
    return EmailReader(
        provider=payload.provider,
        access_token=payload.access_token,
    )


def handle_error(exc: Exception) -> None:
    if isinstance(exc, InvalidAccessTokenError):
        raise HTTPException(status_code=401, detail="Re-auth required")
    if isinstance(exc, AttachmentTooLargeError):
        raise HTTPException(status_code=413, detail="Attachment too large")
    if isinstance(exc, EmailIntegrationError):
        raise HTTPException(status_code=500, detail=str(exc))
    if isinstance(exc, TokenRefreshError):
        raise HTTPException(status_code=500, detail="Token refresh failed")
    if isinstance(exc, RefreshError):
        raise HTTPException(status_code=401, detail="Re-auth required")
    raise 



# =========================
# Health
# =========================

@router.post("/health")
def health(payload: BaseAuthRequest):
    try:
        reader = get_reader(payload)
        return {"valid": reader.is_token_valid()}
    except EmailIntegrationError:
        return {"valid": False}


# =========================
# Folders
# =========================

@router.post("/folders")
def list_folders(payload: BaseAuthRequest):
    try:
        reader = get_reader(payload)
        return {
            "folders": [f.value for f in reader.get_folders()]
        }
    except Exception as exc:
        handle_error(exc)


# =========================
# Inbox
# =========================

@router.post("/inbox")
def get_inbox(payload: InboxRequest):
    try:
        reader = get_reader(payload)

        # -------------------------
        # Convert API filters → domain filters
        # -------------------------
        filters = None
        if payload.filters:
            filters = EmailSearchFilter(
                **payload.filters.model_dump()
            )

        emails, next_cursor = reader.get_inbox(
            page_size=payload.page_size,
            cursor=payload.cursor,
            folder=MailFolder(payload.folder) if payload.folder else None,
            filters=filters,
        )

        return {
            "emails": [e.to_dict() for e in emails],
            "next_cursor": next_cursor,
        }
    except Exception as exc:
        handle_error(exc)


# =========================
# Email Detail
# =========================

@router.post("/detail")
def get_email_detail(payload: EmailDetailRequest):
    try:
        reader = get_reader(payload)

        detail = reader.get_email_detail(
            message_id=payload.message_id,
        )

        return detail.to_dict()
    except Exception as exc:
        handle_error(exc)


# =========================
# Attachments
# =========================

@router.post("/attachments")
def list_attachments(payload: AttachmentListRequest):
    try:
        reader = get_reader(payload)

        attachments = reader.get_attachments(
            message_id=payload.message_id,
        )

        return {
            "attachments": [a.to_dict() for a in attachments]
        }
    except Exception as exc:
        handle_error(exc)


@router.post("/attachment/download")
def download_attachment(payload: AttachmentDownloadRequest):
    try:
        reader = get_reader(payload)

        content = reader.download_attachment(
            message_id=payload.message_id,
            attachment_id=payload.attachment_id,
        )

        return {
            "size": len(content),
            "content_base64": base64.b64encode(content).decode("ascii"),
        }
    except Exception as exc:
        handle_error(exc)
