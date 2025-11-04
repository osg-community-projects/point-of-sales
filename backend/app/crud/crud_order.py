from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from app.crud.base import CRUDBase
from app.models import Order, OrderItem
from app.schemas import OrderCreate, OrderUpdate

class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):
    def get_by_order_number(self, db: Session, *, order_number: str) -> Optional[Order]:
        return db.query(Order).filter(Order.order_number == order_number).first()

    def get_by_customer(
        self, 
        db: Session, 
        *, 
        customer_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Order]:
        return (
            db.query(Order)
            .filter(Order.customer_id == customer_id)
            .order_by(desc(Order.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_status(
        self, 
        db: Session, 
        *, 
        status: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Order]:
        return (
            db.query(Order)
            .filter(Order.status == status)
            .order_by(desc(Order.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_date_range(
        self,
        db: Session,
        *,
        start_date: datetime,
        end_date: datetime,
        skip: int = 0,
        limit: int = 100
    ) -> List[Order]:
        return (
            db.query(Order)
            .filter(
                and_(
                    Order.created_at >= start_date,
                    Order.created_at <= end_date
                )
            )
            .order_by(desc(Order.created_at))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_recent(self, db: Session, *, limit: int = 10) -> List[Order]:
        return (
            db.query(Order)
            .order_by(desc(Order.created_at))
            .limit(limit)
            .all()
        )

order = CRUDOrder(Order)
