from email_integration.domain.models.folders import MailFolder

# Maps domain-level folders to Gmail labels
GMAIL_FOLDER_MAP: dict[MailFolder, str] = {
    MailFolder.INBOX: "INBOX",
    MailFolder.SENT: "SENT",
    MailFolder.DRAFTS: "DRAFT",
    MailFolder.DELETED: "TRASH",
    MailFolder.SPAM: "SPAM",
    MailFolder.STARRED: "STARRED",

}
