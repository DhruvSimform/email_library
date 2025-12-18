"""Interfaces (protocols/abstract base classes) for providers."""

from typing import Iterable, Protocol

from ..models import EmailMessage


class EmailProvider(Protocol):
    """Provider interface for sending/receiving emails."""

    def send(self, message: EmailMessage) -> None:
        ...

    def fetch(self) -> Iterable[EmailMessage]:
        ...
