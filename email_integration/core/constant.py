"""
Centralized configuration constants for email integration.
"""

# =========================
# API URLs & Endpoints
# =========================

# Microsoft Graph API
OUTLOOK_GRAPH_API_BASE_URL = "https://graph.microsoft.com/v1.0"

# Google OAuth
GOOGLE_OAUTH_SCOPE_GMAIL_READONLY = "https://www.googleapis.com/auth/gmail.readonly"
GOOGLE_OAUTH_SCOPE_GMAIL = ["https://www.googleapis.com/auth/gmail.readonly"]

# =========================
# Timeouts (seconds)
# =========================

REQUEST_TIMEOUT_SECONDS = 30

# =========================
# Pagination & Size Limits
# =========================

# Attachment limits
MAX_ATTACHMENT_SIZE_BYTES = 25 * 1024 * 1024  # 25 MB
MAX_ATTACHMENT_SIZE_MB = 25

# Page size constraints
MIN_PAGE_SIZE = 1
MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 10

GMAIL_UNDISCLOSED_RECIPIENT = "undisclosed-recipients:;"