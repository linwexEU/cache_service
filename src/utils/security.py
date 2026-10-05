import hashlib


class Security:
    """Deterministic content hashing used as payload identity (same output → same id)."""

    def hash(self, password: str) -> str:
        """sha256 hex: stable across restarts, so payload ids survive redeploys."""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()


security = Security()
