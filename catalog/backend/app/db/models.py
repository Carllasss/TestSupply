from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    category: Mapped[str] = mapped_column(String(80), index=True)
    region: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    product_lines: Mapped[str | None] = mapped_column(String(300), nullable=True)

    contact_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(120), nullable=True)
    website: Mapped[str | None] = mapped_column(String(300), nullable=True)

    moq: Mapped[str | None] = mapped_column(String(200), nullable=True)
    price_note: Mapped[str | None] = mapped_column(String(300), nullable=True)
    certificates: Mapped[str | None] = mapped_column(String(300), nullable=True)
    delivery_terms: Mapped[str | None] = mapped_column(String(300), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_via: Mapped[str] = mapped_column(String(20), default="manual")
    status: Mapped[str] = mapped_column(String(20), default="found", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
