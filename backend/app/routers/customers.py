from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Customer, User
from app.schemas import Customer as CustomerSchema, CustomerCreate, CustomerUpdate
from app.auth import get_current_active_user

router = APIRouter()

@router.post("/", response_model=CustomerSchema)
async def create_customer(
    customer: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check if email already exists
    if customer.email:
        existing_customer = db.query(Customer).filter(Customer.email == customer.email).first()
        if existing_customer:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    db_customer = Customer(**customer.dict())
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer

@router.get("/", response_model=List[CustomerSchema])
async def read_customers(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Customer)
    
    if search:
        query = query.filter(
            (Customer.name.contains(search)) |
            (Customer.email.contains(search)) |
            (Customer.phone.contains(search))
        )
    
    customers = query.offset(skip).limit(limit).all()
    return customers

@router.get("/{customer_id}", response_model=CustomerSchema)
async def read_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@router.put("/{customer_id}", response_model=CustomerSchema)
async def update_customer(
    customer_id: int,
    customer_update: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    update_data = customer_update.dict(exclude_unset=True)
    
    # Check for duplicate email if being updated
    if "email" in update_data and update_data["email"]:
        existing_customer = db.query(Customer).filter(
            Customer.email == update_data["email"],
            Customer.id != customer_id
        ).first()
        if existing_customer:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    for field, value in update_data.items():
        setattr(customer, field, value)
    
    db.commit()
    db.refresh(customer)
    return customer

@router.delete("/{customer_id}")
async def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Check if customer has orders
    from app.models import Order
    orders_count = db.query(Order).filter(Order.customer_id == customer_id).count()
    if orders_count > 0:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete customer with existing orders"
        )
    
    db.delete(customer)
    db.commit()
    return {"message": "Customer deleted successfully"}
