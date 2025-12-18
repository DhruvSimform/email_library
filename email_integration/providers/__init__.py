# Import providers so registration happens
from email_integration.providers.gmail.provider import GmailProvider  # noqa
from email_integration.providers.outlook.provider import \
    OutlookProvider  # noqa

# Providers are registered in their respective modules
