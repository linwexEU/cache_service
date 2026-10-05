from src.exceptions.base import AppError


class DifferentLengthError(AppError):
    """Input lists differ in length; mapped to HTTP 400 since interleaving is undefined."""
    pass


class TransformedStringNotFoundError(AppError):
    """Unknown payload id on GET; mapped to HTTP 404 instead of leaking internals."""
    pass
