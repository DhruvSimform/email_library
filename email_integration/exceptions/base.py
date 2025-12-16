
class EmailIntegrationError(Exception):
    """
    Base exception for the email integration SDK.

    All custom exceptions MUST inherit from this.
    """

    default_message = "Email integration error occurred"

    def __init__(self, message: str | None = None):
        super().__init__(message or self.default_message)
