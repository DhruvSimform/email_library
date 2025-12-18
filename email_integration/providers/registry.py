from typing import Dict, Type
from email_integration.domain.interfaces.base_provider import BaseEmailProvider
from email_integration.exceptions.provider import UnsupportedProviderError


class ProviderRegistry:
    """Registry for email providers."""
    
    _providers: Dict[str, Type[BaseEmailProvider]] = {}

    @classmethod
    def register(cls, name: str, provider_cls: Type[BaseEmailProvider]) -> None:
        cls._providers[name.lower()] = provider_cls

    @classmethod
    def get(cls, name: str) -> BaseEmailProvider:
        provider_cls = cls._providers.get(name.lower())
        if not provider_cls:
            raise UnsupportedProviderError(f"Provider '{name}' not registered")
        return provider_cls()
# Providers are registered in their respective modules