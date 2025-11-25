# E-commerce Example

Build a product catalog with categories, inventory, and orders.

## Models

### Category

```bash
python cli.py make:resource Category \
  -f name:string:required,unique,max:100 \
  -f slug:slug:required,unique \
  -f description:text:nullable \
  -f image:image:nullable \
  -f parent_id:integer:nullable,foreign:categories.id \
  -m
```

### Product

```bash
python cli.py make:resource Product \
  -f name:string:required,max:255 \
  -f slug:slug:required,unique \
  -f description:text:nullable \
  -f price:money:required,ge:0 \
  -f compare_price:money:nullable,ge:0 \
  -f sku:string:required,unique,max:50 \
  -f stock:integer:required,ge:0 \
  -f weight:float:nullable,ge:0 \
  -f is_active:boolean:required \
  -f featured:boolean:required \
  -f image:image:nullable \
  -f category_id:integer:nullable,foreign:categories.id \
  -m -p
```

### Order

```bash
python cli.py make:resource Order \
  -f order_number:string:required,unique \
  -f status:string:required,index \
  -f subtotal:money:required,ge:0 \
  -f tax:money:required,ge:0 \
  -f shipping:money:required,ge:0 \
  -f total:money:required,ge:0 \
  -f notes:text:nullable \
  -f user_id:integer:required,foreign:users.id \
  -m -p
```

### OrderItem

```bash
python cli.py make:model OrderItem \
  -f quantity:integer:required,ge:1 \
  -f price:money:required,ge:0 \
  -f total:money:required,ge:0 \
  -f order_id:integer:required,foreign:orders.id \
  -f product_id:integer:required,foreign:products.id \
  -m
```

---

## Order Status Enum

```bash
python cli.py make:enum OrderStatus
```

```python
# app/enums/order_status.py

from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

    @classmethod
    def values(cls) -> list:
        return [e.value for e in cls]
```

---

## Product Controller

```python
# app/controllers/product_controller.py

from typing import List, Optional
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.models.product import Product, ProductCreate, ProductUpdate
from app.utils.pagination import paginate, PaginationParams
from app.utils.exceptions import NotFoundException, BadRequestException


class ProductController:

    @staticmethod
    async def get_active_products(
        session: AsyncSession,
        page: int = 1,
        per_page: int = 20,
        category_id: Optional[int] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        search: Optional[str] = None,
        in_stock: bool = False,
        featured: bool = False
    ):
        query = select(Product).where(
            Product.deleted_at.is_(None),
            Product.is_active == True
        )

        if category_id:
            query = query.where(Product.category_id == category_id)
        if min_price:
            query = query.where(Product.price >= min_price)
        if max_price:
            query = query.where(Product.price <= max_price)
        if search:
            query = query.where(
                or_(
                    Product.name.ilike(f"%{search}%"),
                    Product.description.ilike(f"%{search}%"),
                    Product.sku.ilike(f"%{search}%")
                )
            )
        if in_stock:
            query = query.where(Product.stock > 0)
        if featured:
            query = query.where(Product.featured == True)

        params = PaginationParams(page=page, per_page=per_page)
        return await paginate(session, query, params)

    @staticmethod
    async def update_stock(
        session: AsyncSession,
        product_id: int,
        quantity: int
    ) -> Product:
        """Update product stock (positive to add, negative to subtract)"""
        product = await ProductController.get_by_id(session, product_id)
        if not product:
            raise NotFoundException("Product not found")

        new_stock = product.stock + quantity
        if new_stock < 0:
            raise BadRequestException("Insufficient stock")

        product.stock = new_stock
        product.touch()
        await session.flush()
        return product

    @staticmethod
    async def check_availability(
        session: AsyncSession,
        items: List[dict]
    ) -> List[dict]:
        """Check if products are available in requested quantities"""
        unavailable = []

        for item in items:
            product = await ProductController.get_by_id(
                session, item["product_id"]
            )
            if not product:
                unavailable.append({
                    "product_id": item["product_id"],
                    "error": "Product not found"
                })
            elif product.stock < item["quantity"]:
                unavailable.append({
                    "product_id": item["product_id"],
                    "error": f"Only {product.stock} available",
                    "available": product.stock
                })

        return unavailable
```

---

## Order Service

```python
# app/services/order_service.py

from typing import List
from decimal import Decimal
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderCreate
from app.models.order_item import OrderItem
from app.controllers.product_controller import ProductController
from app.enums.order_status import OrderStatus
from app.utils.exceptions import BadRequestException


class OrderService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_order(
        self,
        user_id: int,
        items: List[dict],
        shipping: Decimal = Decimal("0"),
        notes: str = None
    ) -> Order:
        # Check availability
        unavailable = await ProductController.check_availability(
            self.session, items
        )
        if unavailable:
            raise BadRequestException(
                "Some items are unavailable",
                details={"unavailable": unavailable}
            )

        # Calculate totals
        subtotal = Decimal("0")
        order_items = []

        for item in items:
            product = await ProductController.get_by_id(
                self.session, item["product_id"]
            )
            item_total = product.price * item["quantity"]
            subtotal += item_total

            order_items.append({
                "product_id": product.id,
                "quantity": item["quantity"],
                "price": product.price,
                "total": item_total
            })

        # Calculate tax (example: 10%)
        tax = subtotal * Decimal("0.10")
        total = subtotal + tax + shipping

        # Create order
        order = Order(
            order_number=self._generate_order_number(),
            status=OrderStatus.PENDING,
            subtotal=subtotal,
            tax=tax,
            shipping=shipping,
            total=total,
            notes=notes,
            user_id=user_id
        )
        self.session.add(order)
        await self.session.flush()

        # Create order items and update stock
        for item in order_items:
            order_item = OrderItem(
                order_id=order.id,
                **item
            )
            self.session.add(order_item)

            # Decrease stock
            await ProductController.update_stock(
                self.session,
                item["product_id"],
                -item["quantity"]
            )

        await self.session.refresh(order)
        return order

    async def cancel_order(self, order_id: int) -> Order:
        order = await self._get_order(order_id)

        if order.status in [OrderStatus.SHIPPED, OrderStatus.DELIVERED]:
            raise BadRequestException("Cannot cancel shipped/delivered order")

        # Restore stock
        for item in order.items:
            await ProductController.update_stock(
                self.session,
                item.product_id,
                item.quantity
            )

        order.status = OrderStatus.CANCELLED
        order.touch()
        await self.session.flush()
        return order

    def _generate_order_number(self) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        import random
        return f"ORD-{timestamp}-{random.randint(1000, 9999)}"
```

---

## Product Routes

```python
# app/routes/product_routes.py

from typing import Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_session
from app.controllers.product_controller import ProductController

router = APIRouter()


@router.get("/")
async def get_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    min_price: Optional[Decimal] = Query(None, ge=0),
    max_price: Optional[Decimal] = Query(None, ge=0),
    search: Optional[str] = Query(None, min_length=2),
    in_stock: bool = Query(False),
    featured: bool = Query(False),
    session: AsyncSession = Depends(get_session)
):
    """Get products with filters"""
    result = await ProductController.get_active_products(
        session,
        page=page,
        per_page=per_page,
        category_id=category_id,
        min_price=min_price,
        max_price=max_price,
        search=search,
        in_stock=in_stock,
        featured=featured
    )
    return {
        "data": result.items,
        "pagination": {
            "page": result.page,
            "per_page": result.per_page,
            "total": result.total,
            "pages": result.pages
        }
    }
```

---

## Order Routes

```python
# app/routes/order_routes.py

from typing import List
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.connection import get_session
from app.services.order_service import OrderService
from app.utils.auth import get_current_active_user

router = APIRouter()


class OrderItemRequest(BaseModel):
    product_id: int
    quantity: int


class CreateOrderRequest(BaseModel):
    items: List[OrderItemRequest]
    notes: str = None


@router.post("/")
async def create_order(
    data: CreateOrderRequest,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_active_user)
):
    """Create a new order"""
    service = OrderService(session)
    order = await service.create_order(
        user_id=current_user.id,
        items=[item.model_dump() for item in data.items],
        notes=data.notes
    )
    return order


@router.post("/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_active_user)
):
    """Cancel an order"""
    service = OrderService(session)
    return await service.cancel_order(order_id)
```

---

## API Endpoints

### Products

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products/` | List with filters |
| GET | `/api/products/{id}` | Get by ID |
| GET | `/api/products/slug/{slug}` | Get by slug |
| POST | `/api/products/` | Create (admin) |
| PUT | `/api/products/{id}` | Update (admin) |
| DELETE | `/api/products/{id}` | Delete (admin) |

### Orders

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/orders/` | User's orders |
| GET | `/api/orders/{id}` | Order details |
| POST | `/api/orders/` | Create order |
| POST | `/api/orders/{id}/cancel` | Cancel order |

---

## Usage

### List Products

```bash
curl "http://localhost:8000/api/products/?category_id=1&in_stock=true&min_price=10"
```

### Create Order

```bash
curl -X POST http://localhost:8000/api/orders/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"product_id": 1, "quantity": 2},
      {"product_id": 3, "quantity": 1}
    ],
    "notes": "Please gift wrap"
  }'
```

## Next Steps

- [Blog Example](blog.md) - Content management
- [API Service Example](api-service.md) - Microservice
- [Make Commands](../commands/make.md) - Generate more
