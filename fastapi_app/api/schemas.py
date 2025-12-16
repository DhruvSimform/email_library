from pydantic import BaseModel


class BaseAuthRequest(BaseModel):
    provider: str
    access_token: str


class InboxRequest(BaseAuthRequest):
    page_size: int = 10
    cursor: str | None = None
    folder: str = "inbox"


class EmailDetailRequest(BaseAuthRequest):
    message_id: str
    folder: str = "inbox"


class AttachmentListRequest(BaseAuthRequest):
    message_id: str


class AttachmentDownloadRequest(BaseAuthRequest):
    message_id: str
    attachment_id: str
