from enum import Enum


class MailFolder(str, Enum):
    """
    Provider-agnostic mail folder choices.

    These represent logical folders used by the workspace.
    Providers map these to their internal identifiers.
    """

    INBOX = "inbox"
    SENT = "sent"
    DRAFTS = "drafts"
    DELETED = "deleted"
    SPAM = "spam"
    STARRED = "starred"

    def __str__(self) -> str:
        return self.value
