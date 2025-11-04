from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.crud.base import CRUDBase
from app.models import Customer
from app.schemas import CustomerCreate, CustomerUpdate

class CRUDCustomer(CRUDBase[Customer, CustomerCreate, CustomerUpdate]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[Customer]:
        return db.query(Customer).filter(Customer.email == email).first()

    def search(
        self, 
        db: Session, 
        *, 
        query: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Customer]:
        return (
            db.query(Customer)
            .filter(
                or_(
                    Customer.name.contains(query),
                    Customer.email.contains(query),
                    Customer.phone.contains(query)
                )
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

customer = CRUDCustomer(Customer)
