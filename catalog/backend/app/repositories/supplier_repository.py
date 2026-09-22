from sqlalchemy import and_, distinct, or_, select
from sqlalchemy.orm import Session

from app.core.query_terms import significant_terms
from app.db.models import Supplier
from app.schemas.supplier import SupplierCreate


class SupplierRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_suppliers(
        self,
        category: str | None = None,
        region: str | None = None,
        query: str | None = None,
        has_price: bool | None = None,
        has_moq: bool | None = None,
    ) -> list[Supplier]:
        stmt = select(Supplier)
        if category:
            stmt = stmt.where(Supplier.category == category)
        if region:
            stmt = stmt.where(Supplier.region == region)
        if query:
            # Every significant word must appear *somewhere* (name, description
            # or product_lines — not necessarily the same field), so
            # "мясо оптом" matches a supplier whose product_lines just say
            # "говядина, свинина" isn't the goal here — it matches one whose
            # text literally contains "мясо" (generic filler words like
            # "оптом" are dropped, they wouldn't discriminate anyway).
            stmt = stmt.where(
                and_(
                    *(
                        or_(
                            Supplier.name.ilike(f"%{term}%"),
                            Supplier.description.ilike(f"%{term}%"),
                            Supplier.product_lines.ilike(f"%{term}%"),
                        )
                        for term in significant_terms(query)
                    )
                )
            )
        if has_price is not None:
            stmt = stmt.where(Supplier.price_note.is_not(None) if has_price else Supplier.price_note.is_(None))
        if has_moq is not None:
            stmt = stmt.where(Supplier.moq.is_not(None) if has_moq else Supplier.moq.is_(None))
        stmt = stmt.order_by(Supplier.created_at.desc())
        return list(self.db.execute(stmt).scalars().all())

    def get(self, supplier_id: int) -> Supplier | None:
        return self.db.get(Supplier, supplier_id)

    def get_many(self, ids: list[int]) -> list[Supplier]:
        if not ids:
            return []
        stmt = select(Supplier).where(Supplier.id.in_(ids))
        by_id = {s.id: s for s in self.db.execute(stmt).scalars().all()}
        return [by_id[i] for i in ids if i in by_id]

    def create(self, data: SupplierCreate, created_via: str, source_url: str | None = None, status: str = "found") -> Supplier:
        supplier = Supplier(**data.model_dump(), created_via=created_via, source_url=source_url, status=status)
        self.db.add(supplier)
        self.db.commit()
        self.db.refresh(supplier)
        return supplier

    def categories(self) -> list[str]:
        stmt = select(distinct(Supplier.category)).order_by(Supplier.category)
        return [row[0] for row in self.db.execute(stmt).all()]

    def regions(self) -> list[str]:
        stmt = select(distinct(Supplier.region)).order_by(Supplier.region)
        return [row[0] for row in self.db.execute(stmt).all()]

    def count(self) -> int:
        return self.db.query(Supplier).count()

    def known_websites(self) -> list[str]:
        stmt = select(Supplier.website).where(Supplier.website.is_not(None))
        return [row[0] for row in self.db.execute(stmt).all()]

    def known_names(self) -> list[str]:
        return [row[0] for row in self.db.execute(select(Supplier.name)).all()]

    def known_phones(self) -> list[str]:
        stmt = select(Supplier.contact_phone).where(Supplier.contact_phone.is_not(None))
        return [row[0] for row in self.db.execute(stmt).all()]
