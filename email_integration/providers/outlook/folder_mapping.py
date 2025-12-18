from email_integration.domain.models.folders import MailFolder

# Maps domain-level folders to Outlook folder names
OUTLOOK_FOLDER_MAP: dict[MailFolder, str] = {
    MailFolder.INBOX: "inbox",
    MailFolder.SENT: "sentitems",
    MailFolder.DRAFTS: "drafts",
    MailFolder.DELETED: "deleteditems",
    MailFolder.SPAM: "junkemail",
    MailFolder.STARRED: "inbox",  # Outlook uses flags for starred emails

}