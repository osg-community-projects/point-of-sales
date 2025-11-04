from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Product, Category, User
from app.schemas import (
    Product as ProductSchema, 
    ProductCreate, 
    ProductUpdate,
    Category as CategorySchema,
    CategoryCreate,
    CategoryUpdate
)
from app.auth import get_current_active_user

router = APIRouter()

# Category endpoints
@router.post("/categories", response_model=CategorySchema)
async def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    db_category = Category(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.get("/categories", response_model=List[CategorySchema])
async def read_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    categories = db.query(Category).offset(skip).limit(limit).all()
    return categories

@router.get("/categories/{category_id}", response_model=CategorySchema)
async def read_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.put("/categories/{category_id}", response_model=CategorySchema)
async def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    update_data = category_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    return category

@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    
    # Check if category has products
    products_count = db.query(Product).filter(Product.category_id == category_id).count()
    if products_count > 0:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete category with existing products"
        )
    
    db.delete(category)
    db.commit()
    return {"message": "Category deleted successfully"}

# Product endpoints
@router.post("/", response_model=ProductSchema)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check if category exists if provided
    if product.category_id:
        category = db.query(Category).filter(Category.id == product.category_id).first()
        if not category:
            raise HTTPException(status_code=400, detail="Category not found")
    
    # Check for duplicate SKU or barcode
    if product.sku:
        existing_product = db.query(Product).filter(Product.sku == product.sku).first()
        if existing_product:
            raise HTTPException(status_code=400, detail="SKU already exists")
    
    if product.barcode:
        existing_product = db.query(Product).filter(Product.barcode == product.barcode).first()
        if existing_product:
            raise HTTPException(status_code=400, detail="Barcode already exists")
    
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/", response_model=List[ProductSchema])
async def read_products(
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    active_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Product)
    
    if active_only:
        query = query.filter(Product.is_active == True)
    
    if category_id:
        query = query.filter(Product.category_id == category_id)
    
    if search:
        query = query.filter(
            (Product.name.contains(search)) |
            (Product.description.contains(search)) |
            (Product.sku.contains(search)) |
            (Product.barcode.contains(search))
        )
    
    products = query.offset(skip).limit(limit).all()
    return products

@router.get("/{product_id}", response_model=ProductSchema)
async def read_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=ProductSchema)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check for duplicate SKU or barcode if being updated
    update_data = product_update.dict(exclude_unset=True)
    
    if "sku" in update_data and update_data["sku"]:
        existing_product = db.query(Product).filter(
            Product.sku == update_data["sku"],
            Product.id != product_id
        ).first()
        if existing_product:
            raise HTTPException(status_code=400, detail="SKU already exists")
    
    if "barcode" in update_data and update_data["barcode"]:
        existing_product = db.query(Product).filter(
            Product.barcode == update_data["barcode"],
            Product.id != product_id
        ).first()
        if existing_product:
            raise HTTPException(status_code=400, detail="Barcode already exists")
    
    # Check if category exists if being updated
    if "category_id" in update_data and update_data["category_id"]:
        category = db.query(Category).filter(Category.id == update_data["category_id"]).first()
        if not category:
            raise HTTPException(status_code=400, detail="Category not found")
    
    for field, value in update_data.items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Soft delete by setting is_active to False
    product.is_active = False
    db.commit()
    return {"message": "Product deactivated successfully"}

@router.get("/barcode/{barcode}", response_model=ProductSchema)
async def get_product_by_barcode(
    barcode: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    product = db.query(Product).filter(
        Product.barcode == barcode,
        Product.is_active == True
    ).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
