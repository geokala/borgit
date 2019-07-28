"""Exceptions for borgit borg automation tool."""


class CheckFailure(Exception):
    """Raised when integrity checks of a backup fail."""
