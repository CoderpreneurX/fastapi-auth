from pwdlib import PasswordHash


class Hashing:
    """Generic hashing utility."""

    _password_hash = PasswordHash.recommended()

    @classmethod
    def hash(cls, value: str) -> str:
        """Hash a string."""
        return cls._password_hash.hash(value)

    @classmethod
    def verify(cls, value: str, hashed_value: str) -> bool:
        """Verify a string against its hash."""
        return cls._password_hash.verify(value, hashed_value)
