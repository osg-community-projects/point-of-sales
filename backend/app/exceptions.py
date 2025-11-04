from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)

class POSException(Exception):
    """Base exception for POS system"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ProductNotFoundError(POSException):
    def __init__(self, product_id: int):
        super().__init__(f"Product with ID {product_id} not found", 404)

class InsufficientStockError(POSException):
    def __init__(self, product_name: str, available: int, requested: int):
        super().__init__(
            f"Insufficient stock for {product_name}. Available: {available}, Requested: {requested}",
            400
        )

class CustomerNotFoundError(POSException):
    def __init__(self, customer_id: int):
        super().__init__(f"Customer with ID {customer_id} not found", 404)

class OrderNotFoundError(POSException):
    def __init__(self, order_id: int):
        super().__init__(f"Order with ID {order_id} not found", 404)

class InvalidOrderStatusError(POSException):
    def __init__(self, current_status: str, action: str):
        super().__init__(f"Cannot {action} order with status: {current_status}", 400)

async def pos_exception_handler(request: Request, exc: POSException):
    """Handle custom POS exceptions"""
    logger.error(f"POS Exception: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message, "type": "pos_error"}
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    logger.error(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
            "type": "validation_error"
        }
    )

async def integrity_exception_handler(request: Request, exc: IntegrityError):
    """Handle database integrity errors"""
    logger.error(f"Database integrity error: {str(exc)}")
    
    error_message = "Database constraint violation"
    if "UNIQUE constraint failed" in str(exc):
        if "username" in str(exc):
            error_message = "Username already exists"
        elif "email" in str(exc):
            error_message = "Email already exists"
        elif "sku" in str(exc):
            error_message = "SKU already exists"
        elif "barcode" in str(exc):
            error_message = "Barcode already exists"
    
    return JSONResponse(
        status_code=400,
        content={"detail": error_message, "type": "integrity_error"}
    )

async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": "server_error"
        }
    )
