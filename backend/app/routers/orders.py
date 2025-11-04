from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models import Order, OrderItem, Product, Customer, User
from app.schemas import Order as OrderSchema, OrderCreate, OrderUpdate
from app.auth import get_current_active_user
import uuid
from datetime import datetime

router = APIRouter()

def generate_order_number() -> str:
    """Generate a unique order number"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    unique_id = str(uuid.uuid4())[:8].upper()
    return f"ORD-{timestamp}-{unique_id}"

def calculate_tax(subtotal: float, tax_rate: float = 0.08) -> float:
    """Calculate tax amount (default 8% tax rate)"""
    return round(subtotal * tax_rate, 2)

@router.post("/", response_model=OrderSchema)
async def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Validate customer if provided
    if order.customer_id:
        customer = db.query(Customer).filter(Customer.id == order.customer_id).first()
        if not customer:
            raise HTTPException(status_code=400, detail="Customer not found")
    
    # Validate products and calculate totals
    if not order.items:
        raise HTTPException(status_code=400, detail="Order must have at least one item")
    
    subtotal = 0.0
    order_items_data = []
    
    for item in order.items:
        product = db.query(Product).filter(
            Product.id == item.product_id,
            Product.is_active == True
        ).first()
        if not product:
            raise HTTPException(
                status_code=400, 
                detail=f"Product with ID {item.product_id} not found or inactive"
            )
        
        # Check stock availability
        if product.stock_quantity < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for product {product.name}. Available: {product.stock_quantity}, Requested: {item.quantity}"
            )
        
        # Use current product price if unit_price not provided or is 0
        unit_price = item.unit_price if item.unit_price > 0 else product.price
        total_price = unit_price * item.quantity
        subtotal += total_price
        
        order_items_data.append({
            "product_id": item.product_id,
            "quantity": item.quantity,
            "unit_price": unit_price,
            "total_price": total_price,
            "product": product
        })
    
    # Calculate tax and total
    tax_amount = calculate_tax(subtotal)
    discount_amount = order.discount_amount or 0.0
    total_amount = subtotal + tax_amount - discount_amount
    
    if total_amount < 0:
        raise HTTPException(status_code=400, detail="Total amount cannot be negative")
    
    # Create order
    db_order = Order(
        order_number=generate_order_number(),
        customer_id=order.customer_id,
        user_id=current_user.id,
        subtotal=subtotal,
        tax_amount=tax_amount,
        discount_amount=discount_amount,
        total_amount=total_amount,
        payment_method=order.payment_method,
        notes=order.notes,
        status="pending"
    )
    
    db.add(db_order)
    db.flush()  # Get the order ID without committing
    
    # Create order items and update stock
    for item_data in order_items_data:
        db_order_item = OrderItem(
            order_id=db_order.id,
            product_id=item_data["product_id"],
            quantity=item_data["quantity"],
            unit_price=item_data["unit_price"],
            total_price=item_data["total_price"]
        )
        db.add(db_order_item)
        
        # Update product stock
        product = item_data["product"]
        product.stock_quantity -= item_data["quantity"]
    
    db.commit()
    db.refresh(db_order)
    return db_order

@router.get("/", response_model=List[OrderSchema])
async def read_orders(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None),
    customer_id: Optional[int] = Query(None),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Order).order_by(desc(Order.created_at))
    
    if status:
        query = query.filter(Order.status == status)
    
    if customer_id:
        query = query.filter(Order.customer_id == customer_id)
    
    if start_date:
        try:
            start_dt = datetime.fromisoformat(start_date)
            query = query.filter(Order.created_at >= start_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format")
    
    if end_date:
        try:
            end_dt = datetime.fromisoformat(end_date)
            query = query.filter(Order.created_at <= end_dt)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format")
    
    orders = query.offset(skip).limit(limit).all()
    return orders

@router.get("/{order_id}", response_model=OrderSchema)
async def read_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

@router.put("/{order_id}", response_model=OrderSchema)
async def update_order(
    order_id: int,
    order_update: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Prevent updating completed or cancelled orders
    if order.status in ["completed", "cancelled", "refunded"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot update order with status: {order.status}"
        )
    
    update_data = order_update.dict(exclude_unset=True)
    
    # Validate customer if being updated
    if "customer_id" in update_data and update_data["customer_id"]:
        customer = db.query(Customer).filter(Customer.id == update_data["customer_id"]).first()
        if not customer:
            raise HTTPException(status_code=400, detail="Customer not found")
    
    # Recalculate totals if discount is updated
    if "discount_amount" in update_data:
        new_discount = update_data["discount_amount"]
        new_total = order.subtotal + order.tax_amount - new_discount
        if new_total < 0:
            raise HTTPException(status_code=400, detail="Total amount cannot be negative")
        order.total_amount = new_total
    
    for field, value in update_data.items():
        if field != "discount_amount":  # Already handled above
            setattr(order, field, value)
    
    db.commit()
    db.refresh(order)
    return order

@router.post("/{order_id}/complete")
async def complete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status != "pending":
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot complete order with status: {order.status}"
        )
    
    order.status = "completed"
    db.commit()
    db.refresh(order)
    return {"message": "Order completed successfully", "order": order}

@router.post("/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status not in ["pending"]:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot cancel order with status: {order.status}"
        )
    
    # Restore stock quantities
    order_items = db.query(OrderItem).filter(OrderItem.order_id == order_id).all()
    for item in order_items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            product.stock_quantity += item.quantity
    
    order.status = "cancelled"
    db.commit()
    db.refresh(order)
    return {"message": "Order cancelled successfully", "order": order}

@router.get("/number/{order_number}", response_model=OrderSchema)
async def get_order_by_number(
    order_number: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    order = db.query(Order).filter(Order.order_number == order_number).first()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
