# services/

The **services** package contains the **public and internal orchestration layer** of the library.

This is where the clean domain abstraction meets the real world for end users. It provides a simple, intuitive, and safe API for consuming applications while keeping internal complexity hidden.

## Purpose

- Provide a **single, easy-to-use public entry point** (`EmailReader`)
- Hide provider selection, credential setup, and internal orchestration
- Enforce consistent naming and behavior for users
- Keep internal orchestration (`EmailCore`) separate and private
- Make the library feel simple and framework-agnostic

## Structure
```
services/
├── init.py
├── email_core.py      # INTERNAL — thin orchestrator around BaseEmailProvider
└── email_reader.py    # PUBLIC — the main class users should instantiate
```

## Public API: EmailReader

**This is the only class you need to use in your project.**

Located at: `email_integration.services.email_reader.EmailReader`

### How to Use the Library in Any Project
```python
from email_integration.services.email_reader import EmailReader
from email_integration.exceptions.provider import UnsupportedProviderError

try:
    email_reader = EmailReader(
        provider="gmail",
        access_token="your_access_token_here"
    )
    
    emails = email_reader.fetch_emails(
        folder="INBOX",
        search_criteria="subject:Important",
        max_results=10
    )
    
    for email in emails:
        print(email.subject, email.sender)
        
except UnsupportedProviderError as e:
    print(f"Provider error: {e}")
except Exception as e:
    print(f"General error: {e}")
```

### Constructor Parameters
- `provider` (str): The email service provider (e.g., "gmail", "outlook")
- `access_token` (str): The access token for authenticating with the email provider

### Available Methods
- `fetch_emails()`: Retrieve emails from specified folder
- `get_email_detail()`: Get full details of a specific email
- `list_attachments()`: List attachments for a specific email
- `download_attachment()`: Download a specific attachment
- `is_token_valid()`: Check if the access token is still valid
- `list_folders()`: List supported default folders


### Error Handling
The library provides specific exception handling:


```python
from email_integration.exceptions import UnsupportedProviderError

try:
    email_reader = EmailReader(provider="unsupported", access_token="token")
except UnsupportedProviderError as e:
    print(f"Error: {e}")
```
We recommend wrapping your calls in try-except blocks to handle potential errors gracefully.

Other exceptions available in `email_integration.exceptions`:
- `EmailIntegrationError` (Base)
- `AuthError`, `InvalidAccessTokenError`, `TokenRefreshError` (Auth)
- `ProviderError`, `GmailAPIError`, `OutlookAPIError`, `UnsupportedProviderError` (Provider)
- `AttachmentError`, `AttachmentTooLargeError` (Attachment)
- `NetworkError`, `NetworkTimeoutError` (Network)
