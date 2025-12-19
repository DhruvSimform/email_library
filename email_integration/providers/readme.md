# providers/

The **providers** package contains all **provider-specific implementations** for different email services (Gmail, Outlook, etc.).

This is where the abstraction from the `domain/` layer meets real-world APIs. Each provider has its own subfolder with a consistent, repeatable structure that makes adding new providers straightforward and predictable.

## Purpose

- Implement the `BaseEmailProvider` contract defined in `domain/interfaces/base_provider.py`
- Translate provider-specific API responses into clean, unified **domain models**
- Handle provider-specific authentication, pagination, query syntax, folder mapping, and quirks
- Keep all external API dependencies and messy details isolated here
- Enable easy addition of new email providers without touching core logic

## Structure
```
providers/
├── gmail/                 # Fully implemented example
│   ├── __init__.py
│   ├── provider.py        # Main class implementing BaseEmailProvider
│   ├── normalizer.py      # Converts raw API responses → domain models
│   ├── query_builder.py   # Translates EmailSearchFilter → provider query syntax
│   ├── folder_mapping.py  # Maps MailFolder enum → provider-specific labels/IDs/folders
│   └── (optional helpers)
├── outlook/               # Same structure for Outlook
│   └── ...
├── registry.py            # ProviderRegistry — registers and instantiates providers
└── __init__.py
```

## How to Add a New Provider

Follow these steps to add support for a new email provider (e.g., Yahoo, Proton, custom IMAP, etc.):

### 1. Create a new folder
```bash
providers/newprovider/
```

### 2. Implement the provider class
Create `provider.py` that implements `BaseEmailProvider`. Implement all required methods:
- `fetch_emails()`
- `fetch_email_detail()`
- `list_folders()`
- `list_attachments()`
- `download_attachment()`
- `set_credentials()`
- `is_token_valid()`
- `__repr__()`

```python
from email_integration.domain.interfaces.base_provider import BaseEmailProvider
# Import domain models and exceptions as needed

class NewProvider(BaseEmailProvider):
    def __init__(self):
        self._client = None  # Your API client

    def set_credentials(self, access_token: str) -> None:
        # Initialize client with token
        pass

    def is_token_valid(self) -> bool:
        # Check token health
        pass

    def fetch_emails(self, *, page_size, cursor, folder, filters):
        # Call API, use QueryBuilder and Normalizer
        pass

    def fetch_email_detail(self, *, message_id):
        # ...
        pass

    def list_folders(self):
        # Return list of supported MailFolder values
        pass

    def list_attachments(self, *, message_id):
        # ...
        pass

    def download_attachment(self, *, message_id, attachment_id):
        # Enforce MAX_ATTACHMENT_SIZE_BYTES
        pass

# Auto-register the provider
from ..registry import ProviderRegistry
ProviderRegistry.register("newprovider", NewProvider)
```

### 3. Create a normalizer
Create `normalizer.py` to convert raw API responses into domain models (`EmailMessage`, `EmailDetail`, etc.).

### 4. Create a query builder
Create `query_builder.py` to translate `EmailSearchFilter` into the provider's query syntax.

### 5. Create a folder mapping
Create `folder_mapping.py` to map the standardized `MailFolder` enum to the provider's specific folder names/IDs.

### 6. Register the provider
Add your provider to `registry.py` in the `ProviderRegistry` so it can be instantiated by name.
```python
ProviderRegistry.register("newprovider", NewProvider)
```

### 7. Use in app
```python
reader = EmailReader(provider="newprovider", access_token="...")
```