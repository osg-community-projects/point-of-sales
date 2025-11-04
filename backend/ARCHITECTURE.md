# POS System Backend Architecture

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── database.py            # Database connection and session
│   ├── models.py              # SQLAlchemy models
│   ├── schemas.py             # Pydantic schemas for validation
│   ├── auth.py                # Authentication utilities
│   ├── dependencies.py        # Common FastAPI dependencies
│   ├── exceptions.py          # Custom exceptions and handlers
│   ├── crud/                  # CRUD operations
│   │   ├── __init__.py
│   │   ├── base.py           # Base CRUD class
│   │   ├── crud_user.py      # User CRUD operations
│   │   ├── crud_product.py   # Product CRUD operations
│   │   ├── crud_customer.py  # Customer CRUD operations
│   │   └── crud_order.py     # Order CRUD operations
│   ├── services/             # Business logic layer
│   │   ├── __init__.py
│   │   └── order_service.py  # Order business logic
│   └── routers/              # API endpoints
│       ├── __init__.py
│       ├── auth.py           # Authentication endpoints
│       ├── products.py       # Product management endpoints
│       ├── customers.py      # Customer management endpoints
│       └── orders.py         # Order processing endpoints
├── main.py                   # FastAPI application entry point
├── run.py                    # Development server runner
├── start.sh                  # Startup script with venv activation
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
├── .env.example              # Environment variables template
├── .gitignore               # Git ignore rules
└── README.md                # Project documentation
```

## Architecture Principles

### 1. **Layered Architecture**
- **Presentation Layer**: FastAPI routers handle HTTP requests/responses
- **Business Logic Layer**: Services contain domain logic and business rules
- **Data Access Layer**: CRUD modules handle database operations
- **Data Layer**: SQLAlchemy models define database schema

### 2. **Separation of Concerns**
- **Models**: Define database structure and relationships
- **Schemas**: Handle data validation and serialization
- **CRUD**: Provide reusable database operations
- **Services**: Implement business logic and complex operations
- **Routers**: Handle HTTP routing and request/response formatting

### 3. **Dependency Injection**
- Database sessions injected via FastAPI dependencies
- Authentication handled through dependency injection
- Common query parameters centralized in dependencies module

### 4. **Configuration Management**
- Centralized configuration using Pydantic Settings
- Environment-based configuration with .env files
- Type-safe configuration with validation

### 5. **Error Handling**
- Custom exception classes for domain-specific errors
- Global exception handlers for consistent error responses
- Proper HTTP status codes and error messages

## Key Components

### Configuration (`app/config.py`)
- Centralized settings management
- Environment variable handling
- Type validation for configuration values

### Database (`app/database.py`)
- SQLAlchemy engine and session management
- Database connection configuration
- Session dependency for dependency injection

### Models (`app/models.py`)
- SQLAlchemy ORM models
- Database relationships and constraints
- Automatic timestamps and indexing

### Schemas (`app/schemas.py`)
- Pydantic models for request/response validation
- Data serialization and deserialization
- Type hints and validation rules

### CRUD Operations (`app/crud/`)
- Base CRUD class with common operations
- Model-specific CRUD classes with specialized methods
- Reusable database query patterns

### Services (`app/services/`)
- Business logic implementation
- Complex operations spanning multiple models
- Domain-specific validation and processing

### Authentication (`app/auth.py`)
- JWT token generation and validation
- Password hashing and verification
- User authentication and authorization

### Exception Handling (`app/exceptions.py`)
- Custom exception classes
- Global exception handlers
- Consistent error response format

### API Routers (`app/routers/`)
- RESTful API endpoints
- Request/response handling
- Authentication and authorization checks

## Benefits of This Architecture

1. **Maintainability**: Clear separation of concerns makes code easier to maintain
2. **Testability**: Each layer can be tested independently
3. **Scalability**: Modular structure allows for easy extension
4. **Reusability**: CRUD and service layers promote code reuse
5. **Type Safety**: Pydantic schemas provide runtime type checking
6. **Configuration**: Centralized configuration management
7. **Error Handling**: Consistent error responses across the API

## Development Workflow

1. **Models**: Define database schema in `models.py`
2. **Schemas**: Create Pydantic schemas for validation
3. **CRUD**: Implement database operations in CRUD modules
4. **Services**: Add business logic in service modules
5. **Routers**: Create API endpoints using services and CRUD
6. **Tests**: Write tests for each layer independently

This architecture follows FastAPI best practices and provides a solid foundation for a scalable Point of Sale system.
