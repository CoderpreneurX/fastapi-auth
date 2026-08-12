class UserAlreadyExistsError(Exception):
    """Raised when a user already exists."""


class InvalidVerificationTokenError(Exception):
    """Raised when a verification token is invalid, expired, or already used."""
