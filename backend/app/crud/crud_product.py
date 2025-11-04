from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.crud.base import CRUDBase
from app.models import Product, Category
from app.schemas import ProductCreate, ProductUpdate, CategoryCreate, CategoryUpdate

class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    def get_by_sku(self, db: Session, *, sku: str) -> Optional[Product]:
        return db.query(Product).filter(Product.sku == sku).first()

    def get_by_barcode(self, db: Session, *, barcode: str) -> Optional[Product]:
        return db.query(Product).filter(
            Product.barcode == barcode,
            Product.is_active == True
        ).first()

    def get_multi_by_category(
        self, db: Session, *, category_id: int, skip: int = 0, limit: int = 100
    ) -> List[Product]:
        return (
            db.query(Product)
            .filter(Product.category_id == category_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def search(
        self, 
        db: Session, 
        *, 
        query: str, 
        skip: int = 0, 
        limit: int = 100,
        active_only: bool = True
    ) -> List[Product]:
        db_query = db.query(Product)
        
        if active_only:
            db_query = db_query.filter(Product.is_active == True)
        
        db_query = db_query.filter(
            or_(
                Product.name.contains(query),
                Product.description.contains(query),
                Product.sku.contains(query),
                Product.barcode.contains(query)
            )
        )
        
        return db_query.offset(skip).limit(limit).all()

    def get_low_stock(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[Product]:
        return (
            db.query(Product)
            .filter(
                Product.is_active == True,
                Product.stock_quantity <= Product.min_stock_level
            )
            .offset(skip)
            .limit(limit)
            .all()
        )

class CRUDCategory(CRUDBase[Category, CategoryCreate, CategoryUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[Category]:
        return db.query(Category).filter(Category.name == name).first()

product = CRUDProduct(Product)
category = CRUDCategory(Category)
