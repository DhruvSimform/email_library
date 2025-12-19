"""
Email Reader Test Script
Tests various email reading functionalities including fetching emails,
getting details, listing and downloading attachments.
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path to support direct script execution
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from email_integration.domain.models.folders import MailFolder
from email_integration.services.email_reader import EmailReader
from email_integration.domain.models import EmailSearchFilter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
PROVIDER = "outlook"  # Example provider
ACCESS_TOKEN = ""
FOLDER: MailFolder | None = MailFolder.INBOX  # e.g., "MailFolder.INBOX" or None for all folders

FILTER_PARAMS = EmailSearchFilter(has_attachments=True)

MESSAGE_ID = ""
ATTACHMENT_ID = ""

# Configuration flags for test functions
RUN_FETCH_EMAILS = False
RUN_EMAIL_DETAIL = False
RUN_LIST_ATTACHMENTS = False
RUN_DOWNLOAD_ATTACHMENT = True
RUN_LIST_FOLDERS = False

def validate_config() -> bool:
    """Validate required configuration before running tests."""
    if not ACCESS_TOKEN:
        logger.error("ACCESS_TOKEN is not configured. Set EMAIL_ACCESS_TOKEN environment variable.")
        return False
    if not PROVIDER:
        logger.error("PROVIDER is not configured. Set EMAIL_PROVIDER environment variable.")
        return False
    return True


def get_emails() -> None:
    """Fetch and display a list of emails."""
    try:
        logger.info(f"Fetching emails from {PROVIDER}...")
        reader = EmailReader(
            provider=PROVIDER,
            access_token=ACCESS_TOKEN,
        )
        emails, next_cursor = reader.fetch_emails(
            page_size=10,
            cursor=None,
            folder=FOLDER,
            filters=FILTER_PARAMS,
        )
        
        logger.info(f"Successfully fetched {len(emails)} email(s)")
        for idx, email in enumerate(emails, 1):
            print(f"\n--- Email {idx} ---")
            print(email.to_dict())
        print(f"\nNext Cursor: {next_cursor}")
    except Exception as e:
        logger.error(f"Error fetching emails: {str(e)}", exc_info=True)


def get_email_detail() -> None:
    """Fetch and display details of a specific email."""
    try:
        logger.info(f"Fetching email detail for message_id: {MESSAGE_ID}...")
        reader = EmailReader(
            provider=PROVIDER,
            access_token=ACCESS_TOKEN,
        )
        detail = reader.get_email_detail(
            message_id=MESSAGE_ID,
        )
        logger.info("Successfully fetched email detail")
        print(detail.to_dict())
    except Exception as e:
        logger.error(f"Error fetching email detail: {str(e)}", exc_info=True)


def list_attachments() -> None:
    """List all attachments for a specific email."""
    try:
        logger.info(f"Listing attachments for message_id: {MESSAGE_ID}...")
        reader = EmailReader(
            provider=PROVIDER,
            access_token=ACCESS_TOKEN,
        )
        attachments = reader.get_attachments(
            message_id=MESSAGE_ID,
        )
        logger.info(f"Found {len(attachments)} attachment(s)")
        for idx, attachment in enumerate(attachments, 1):
            print(f"\n--- Attachment {idx} ---")
            print(attachment.to_dict())
    except Exception as e:
        logger.error(f"Error listing attachments: {str(e)}", exc_info=True)


def download_attachment() -> None:
    """Download a specific attachment."""
    try:
        logger.info(f"Downloading attachment: {ATTACHMENT_ID}...")
        reader = EmailReader(
            provider=PROVIDER,
            access_token=ACCESS_TOKEN,
        )
        content = reader.download_attachment(
            message_id=MESSAGE_ID,
            attachment_id=ATTACHMENT_ID,
        )
        logger.info("Successfully downloaded attachment")
        print(f"Attachment Content (first 100 bytes): {content[:100]}")
    except Exception as e:
        logger.error(f"Error downloading attachment: {str(e)}", exc_info=True)

def list_folders() -> None:
    """List all email folders."""
    try:
        logger.info(f"Listing folders for provider: {PROVIDER}...")
        reader = EmailReader(
            provider=PROVIDER,
            access_token=ACCESS_TOKEN,
        )
        folders = reader.get_folders()
        logger.info(f"Found {len(folders)} folder(s)")
        for idx, folder in enumerate(folders, 1):
            print(f"\n--- Folder {idx} ---")
            print(folder)
    except Exception as e:
        logger.error(f"Error listing folders: {str(e)}", exc_info=True)

if __name__ == "__main__":
    logger.info("Starting Email Reader Tests...")
    
    # Validate configuration
    if not validate_config():
        logger.error("Configuration validation failed. Exiting.")
        exit(1)

    
    # Run tests based on configuration flags
    if RUN_FETCH_EMAILS:
        print("\n" + "="*50)
        print("FETCHING EMAILS")
        print("="*50)
        get_emails()
    
    if RUN_EMAIL_DETAIL:
        print("\n" + "="*50)
        print("FETCHING EMAIL DETAIL")
        print("="*50)
        get_email_detail()
    
    if RUN_LIST_ATTACHMENTS:
        print("\n" + "="*50)
        print("LISTING ATTACHMENTS")
        print("="*50)
        list_attachments()
    
    if RUN_DOWNLOAD_ATTACHMENT:
        print("\n" + "="*50)
        print("DOWNLOADING ATTACHMENT")
        print("="*50)
        download_attachment()

    if RUN_LIST_FOLDERS:
        print("\n" + "="*50)
        print("LISTING FOLDERS")
        print("="*50)
        list_folders()
    
    logger.info("Email Reader Tests completed.")