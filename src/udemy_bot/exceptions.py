class BotError(Exception):
    """Base exception for bot-related failures."""


class AuthStateMissingError(BotError):
    """Raised when required Playwright auth state is missing."""


class SelectorNotConfiguredError(BotError):
    """Raised when a placeholder selector is still present."""
