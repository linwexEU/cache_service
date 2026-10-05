from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, JSON

from src.db.base import Base


class TransformCache(Base):
    """One row per distinct input string; the unique input_str is what makes cache hits possible."""

    __tablename__ = "transform_cache"

    id: Mapped[int] = mapped_column(primary_key=True)
    input_str: Mapped[str] = mapped_column(String(256), unique=True, index=True, nullable=False)
    transformed_str: Mapped[str] = mapped_column(String(256), nullable=False)


class PayloadCache(Base):
    """One row per distinct generated payload; the unique hash enables payload id reuse."""

    __tablename__ = "payload_cache"

    id: Mapped[int] = mapped_column(primary_key=True)
    interleaving: Mapped[str] = mapped_column(String(256), nullable=False)
    interleaving_hash: Mapped[str] = mapped_column(
        String(256), unique=True, index=True, nullable=False
    )
