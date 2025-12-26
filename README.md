# email-library

**A clean, extensible, read-only Python library for unified access to emails across multiple providers.**

## Overview

The core library lives in `email_integration/` and provides a consistent, provider-agnostic interface for reading emails from Gmail, Outlook/Office 365, and future providers.

**Perfect for:**
- Email monitoring & alerting tools
- Backup/archiving scripts
- Analytics & reporting pipelines
- Notification systems
- Any integration requiring reliable email access

## Key Features

- **Unified API** - Single `EmailReader` entry point across all providers
- **Advanced Search** - Filter by sender, subject, body, dates, attachments, read status
- **Pagination** - Cursor-based pagination support
- **Email Details** - Lightweight summaries plus full text/HTML bodies
- **Safe Attachments** - List first, download selectively (25MB limit)
- **Standard Folders** - Normalized names (`INBOX`, `SENT`, `SPAM`)
- **Typed Models** - Immutable domain models with serialization
- **Rich Exceptions** - Hierarchical error handling
- **Extensible** - Add new providers easily

## Folder Handling

The library automatically handles provider-specific folder structures when no specific folder is provided:

**Gmail (default folders when none specified):**
- Primary inbox, Social, and Promotions categories

**Outlook (default folders when none specified):**
- Inbox (Focused and Other), Sent Items, and Junk Email

**Standardized folder mappings:**
- `INBOX` → Gmail: Primary Inbox | Outlook: Focused Inbox
- `SENT` → Gmail: Sent Items | Outlook: Sent Items
- `SPAM` → Gmail: Spam Email | Outlook: Junk Email
- `DELETED` → Gmail: Trash Items | Outlook: Deleted Items
- `DRAFTS` → Gmail: Drafts | Outlook: Drafts
- `STARRED` → Gmail: Starred | Outlook: Flagged

## Project Structure

```
email-library/
├── email_integration/              # Core library package
│   ├── core/                       # Constants & logging
│   ├── domain/                     # Models & BaseEmailProvider contract
│   ├── exceptions/                 # Custom exceptions
│   ├── providers/                  # Gmail & Outlook implementations
│   ├── services/                   # Public API (EmailReader)
│   └── tests/                      # Test script to validate functionality 
├── fastapi_app/                    # Demo: FastAPI backend
├── frontend/                       # Demo: HTML OAuth frontend and email client test UI
├── pyproject.toml
└── README.md
```

> **Note**: `fastapi_app/` and `frontend/` are demo applications only, not part of the core library.

## Quick Start

**Requirements:** Python 3.12+

**Documentation:**
- [Usage Guide](email_integration/services/readme.md) - Full API reference
- [Adding Providers](email_integration/providers/readme.md) - Extension guide
- [Domain Models](email_integration/domain/readme.md) - Core abstractions
## Demo Application

Run the included demo to test OAuth flows and library functionality:

```bash
# Start FastAPI server
uvicorn fastapi_app.main:app --reload

# Start local server for frontend (use port mentioned in OAuth callback URL JS)
# For example, if callback URL is http://localhost:3000/
python -m http.server 3000

# Open frontend/index.html in browser
# Complete OAuth flow to get access token
# Use the token in FastAPI docs to test providers
```

## Testing

You can test the library functionality using the interactive test script:

```bash
# Interactive testing with the test script
python  email_integration/tests/test_email_reader.py
```

The test script (`email_integration/tests/test_email_reader.py`) provides interactive testing for:
- Fetching emails with filters and pagination
- Getting detailed email content
- Listing and downloading attachments
- Managing email folders

Configure the script by setting your provider, access token, and test parameters at the top of the file.

## Dependencies

- google-api-python-client >= 2.187.0
- google-auth >= 2.45.0
- google-auth-httplib2 >= 0.3.0
- google-auth-oauthlib >= 1.2.2

## License

MIT License