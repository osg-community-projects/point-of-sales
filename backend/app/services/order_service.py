from typing import List
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import Order, OrderItem, Product, User
from app.schemas import OrderCreate, OrderItemCreate
from app.crud.crud_product import product as product_crud
from app.crud.crud_customer import customer as customer_crud
from app.config import settings
import uuid
from datetime import datetime

class OrderService:
    @staticmethod
    def generate_order_number() -> str:
        """Generate a unique order number"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = str(uuid.uuid4())[:8].upper()
        return f"ORD-{timestamp}-{unique_id}"

    @staticmethod
    def calculate_tax(subtotal: float, tax_rate: float = None) -> float:
        """Calculate tax amount"""
        if tax_rate is None:
            tax_rate = settings.default_tax_rate
        return round(subtotal * tax_rate, 2)

    @staticmethod
    def validate_order_items(db: Session, items: List[OrderItemCreate]) -> tuple:
        """Validate order items and return processed data"""
        if not items:
            raise HTTPException(status_code=400, detail="Order must have at least one item")
        
        subtotal = 0.0
        order_items_data = []
        
        for item in items:
            product = product_crud.get(db, id=item.product_id)
            if not product or not product.is_active:
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
        
        return subtotal, order_items_data

    @staticmethod
    def create_order_with_items(
        db: Session, 
        order_data: OrderCreate, 
        current_user: User
    ) -> Order:
        """Create order with items and update stock"""
        # Validate customer if provided
        if order_data.customer_id:
            customer = customer_crud.get(db, id=order_data.customer_id)
            if not customer:
                raise HTTPException(status_code=400, detail="Customer not found")
        
        # Validate and process order items
        subtotal, order_items_data = OrderService.validate_order_items(db, order_data.items)
        
        # Calculate totals
        tax_amount = OrderService.calculate_tax(subtotal)
        discount_amount = order_data.discount_amount or 0.0
        total_amount = subtotal + tax_amount - discount_amount
        
        if total_amount < 0:
            raise HTTPException(status_code=400, detail="Total amount cannot be negative")
        
        # Create order
        db_order = Order(
            order_number=OrderService.generate_order_number(),
            customer_id=order_data.customer_id,
            user_id=current_user.id,
            subtotal=subtotal,
            tax_amount=tax_amount,
            discount_amount=discount_amount,
            total_amount=total_amount,
            payment_method=order_data.payment_method,
            notes=order_data.notes,
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

    @staticmethod
    def cancel_order(db: Session, order: Order) -> Order:
        """Cancel order and restore stock"""
        if order.status not in ["pending"]:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot cancel order with status: {order.status}"
            )
        
        # Restore stock quantities
        order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        for item in order_items:
            product = product_crud.get(db, id=item.product_id)
            if product:
                product.stock_quantity += item.quantity
        
        order.status = "cancelled"
        db.commit()
        db.refresh(order)
        return order

    @staticmethod
    def complete_order(db: Session, order: Order) -> Order:
        """Complete an order"""
        if order.status != "pending":
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot complete order with status: {order.status}"
            )
        
        order.status = "completed"
        db.commit()
        db.refresh(order)
        return order

order_service = OrderService()
