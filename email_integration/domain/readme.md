# domain/

The **domain** package contains the **core, provider-agnostic** models and interfaces of the library.

This is the heart of the abstraction: everything here is **pure**, **immutable**, and **independent** of any email provider (Gmail, Outlook, etc.). No API clients, no network code, no credentials — just clean data structures and contracts.

## Purpose

- Define the **common language** used across all providers
- Enforce **consistency** in data shape and behavior
- Enable **type safety** and **immutability**
- Provide a **clear contract** (`BaseEmailProvider`) that all providers must follow
- Keep the domain logic **pure and testable**

## Structure
- `models/`: Immutable data models representing emails, attachments, threads, etc.
- `interfaces/`: Abstract base classes defining the contracts for email providers


## Models

All models are **frozen dataclasses** (immutable) with `slots=True` for performance and safety.

| File                  | Model                  | Description |
|-----------------------|------------------------|-------------|
| `attachment.py`       | `Attachment`           | Metadata of an email attachment: ID, filename, size (bytes), MIME type. Includes `.size_kb` and `.size_mb` helpers. |
| `email_message.py`    | `EmailMessage`         | Lightweight email summary for list/inbox views: subject, sender, timestamp, preview, folder, attachments, inbox classification. |
| `email_detail.py`     | `EmailDetail`          | Full email content: includes `body_text`, `body_html`, full recipients list. |
| `email_filter.py`     | `EmailSearchFilter`    | Provider-agnostic search criteria: from/to, subject/body contains, dates, has_attachments, is_read, etc. Includes validation. |
| `folders.py`          | `MailFolder` (Enum)    | Standardized folder names: `INBOX`, `SENT`, `DRAFTS`, `DELETED`, `SPAM`, `STARRED`. Providers map these to their internal labels/folders. |

### Key Features of Models
- **Immutable** (`frozen=True`)
- **Validated** (e.g., email format checks, date range logic)
- **Serializable** via `.to_dict()` method
- **Typed** and **self-documenting**

## Interfaces

| File                    | Interface                | Purpose |
|-------------------------|--------------------------|---------|
| `interfaces/base_provider.py` | `BaseEmailProvider` (ABC) | The **contract** that every provider (Gmail, Outlook, etc.) must implement. Defines all read-only operations: fetch emails, details, folders, attachments, token validation. |

### Required Methods in `BaseEmailProvider`
- `fetch_emails()` → returns list of `EmailMessage` + next cursor
- `fetch_email_detail(message_id)`
- `list_folders()`
- `list_attachments(message_id)`
- `download_attachment(message_id, attachment_id)`
- `set_credentials(access_token)`
- `is_token_valid()`

> Providers **must not** expose raw API responses. They **must** return only domain models and raise domain-level exceptions.

## Why This Separation Matters

- Keeps business logic clean and reusable
- Makes adding new providers easy (just implement the interface)
- Enables unit testing without network or API keys
- Ensures consistency across Gmail, Outlook, and future providers

This package is intentionally **simple and stable** — changes here are rare and deliberate.

---

**Domain-driven design at its best: pure, clear, and provider-independent.**