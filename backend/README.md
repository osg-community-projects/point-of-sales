# POS System Backend

A FastAPI-based Point of Sale system backend with JWT authentication, product management, order processing, and customer management.

## Features

- **Authentication**: JWT-based authentication with user registration and login
- **Product Management**: CRUD operations for products and categories
- **Order Processing**: Create orders, manage order items, calculate totals with tax
- **Customer Management**: Store and manage customer information
- **Inventory Tracking**: Basic stock level management with automatic updates
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Run Database Migrations**
   ```bash
   # Using the helper script
   ./migrate.sh upgrade
   
   # Or using alembic directly
   source venv/bin/activate
   alembic upgrade head
   ```

4. **Run the Application**
   ```bash
   ./start.sh
   ```
   
   Or manually:
   ```bash
   source venv/bin/activate
   python run.py
   ```
   
   Or using uvicorn directly:
   ```bash
   source venv/bin/activate
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login and get access token
- `GET /api/auth/me` - Get current user info

### Products
- `GET /api/products/` - List products
- `POST /api/products/` - Create product
- `GET /api/products/{id}` - Get product by ID
- `PUT /api/products/{id}` - Update product
- `DELETE /api/products/{id}` - Deactivate product
- `GET /api/products/barcode/{barcode}` - Get product by barcode

### Categories
- `GET /api/products/categories` - List categories
- `POST /api/products/categories` - Create category
- `GET /api/products/categories/{id}` - Get category
- `PUT /api/products/categories/{id}` - Update category
- `DELETE /api/products/categories/{id}` - Delete category

### Customers
- `GET /api/customers/` - List customers
- `POST /api/customers/` - Create customer
- `GET /api/customers/{id}` - Get customer
- `PUT /api/customers/{id}` - Update customer
- `DELETE /api/customers/{id}` - Delete customer

### Orders
- `GET /api/orders/` - List orders
- `POST /api/orders/` - Create order
- `GET /api/orders/{id}` - Get order
- `PUT /api/orders/{id}` - Update order
- `POST /api/orders/{id}/complete` - Complete order
- `POST /api/orders/{id}/cancel` - Cancel order
- `GET /api/orders/number/{order_number}` - Get order by number

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Database

The application uses SQLite by default for development. The database schema is managed using Alembic migrations.

### Database Migrations

This project uses Alembic for database schema version control:

```bash
# Run all pending migrations
./migrate.sh upgrade

# Create new migration after modifying models
./migrate.sh create "Description of changes"

# Check current database version
./migrate.sh current

# View migration history
./migrate.sh history
```

For detailed migration documentation, see [DATABASE_MIGRATIONS.md](DATABASE_MIGRATIONS.md).

### Production Database

For production, update the `DATABASE_URL` in your `.env` file to use PostgreSQL or another database:

```bash
DATABASE_URL=postgresql://user:password@localhost/pos_system
```

## Authentication

The API uses JWT tokens for authentication. After registering or logging in, include the token in the Authorization header:

```
Authorization: Bearer <your_token_here>
```

## Default Tax Rate

The system applies an 8% tax rate by default. This can be modified in the `calculate_tax` function in `app/routers/orders.py`.
