---
title: E-commerce Example
description: Build an e-commerce API with products, orders, and payments
---

Build an e-commerce backend with products, categories, cart, and orders.

## Models

### Category

```bash
python cli.py make:resource Category \
  -f name:string:required,max:100 \
  -f slug:slug:required,unique \
  -f image:image:nullable \
  -f parent_id:integer:nullable,foreign:categories.id \
  -m -p
```

### Product

```bash
python cli.py make:resource Product \
  -f name:string:required,max:255 \
  -f slug:slug:required,unique \
  -f description:text:nullable \
  -f price:money:required,ge:0 \
  -f compare_price:money:nullable,ge:0 \
  -f cost:money:nullable,ge:0 \
  -f sku:string:required,unique \
  -f stock:integer:required,ge:0 \
  -f image:image:nullable \
  -f is_active:boolean:required \
  -f category_id:integer:nullable,foreign:categories.id \
  -m -p
```

### Order

```bash
python cli.py make:resource Order \
  -f order_number:string:required,unique \
  -f user_id:integer:required,foreign:users.id \
  -f status:string:required \
  -f subtotal:money:required,ge:0 \
  -f tax:money:required,ge:0 \
  -f total:money:required,ge:0 \
  -f notes:text:nullable \
  -m -p
```

### OrderItem

```bash
python cli.py make:resource OrderItem \
  -f order_id:integer:required,foreign:orders.id \
  -f product_id:integer:required,foreign:products.id \
  -f quantity:integer:required,ge:1 \
  -f price:money:required,ge:0 \
  -f total:money:required,ge:0 \
  -m -p
```

---

## Order Status Enum

```bash
python cli.py make:enum OrderStatus
```

Edit `app/enums/order_status.py`:

```python
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
```

---

## Custom Business Logic

### ProductController additions

```python
# app/controllers/product_controller.py

class ProductController:
    @staticmethod
    async def get_active(session: AsyncSession):
        """Get only active products with stock."""
        result = await session.execute(
            select(Product)
            .where(Product.is_active == True)
            .where(Product.stock > 0)
            .where(Product.deleted_at.is_(None))
        )
        return result.scalars().all()

    @staticmethod
    async def reduce_stock(session: AsyncSession, product_id: int, quantity: int):
        """Reduce product stock after order."""
        product = await cls.get_by_id(session, product_id)
        if product and product.stock >= quantity:
            product.stock -= quantity
            await session.commit()
            return True
        return False
```

### OrderController additions

```python
# app/controllers/order_controller.py
import uuid

class OrderController:
    @staticmethod
    async def create_order(session: AsyncSession, user_id: int, items: list):
        """Create order with items."""
        # Generate order number
        order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"

        # Calculate totals
        subtotal = sum(item["price"] * item["quantity"] for item in items)
        tax = subtotal * 0.1  # 10% tax
        total = subtotal + tax

        order = Order(
            order_number=order_number,
            user_id=user_id,
            status="pending",
            subtotal=subtotal,
            tax=tax,
            total=total
        )
        session.add(order)
        await session.flush()

        # Add order items
        for item in items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item["product_id"],
                quantity=item["quantity"],
                price=item["price"],
                total=item["price"] * item["quantity"]
            )
            session.add(order_item)

        await session.commit()
        return order
```

---

## API Examples

### List Products

```bash
curl http://localhost:8000/api/products?category_id=1
```

### Create Order

```bash
curl -X POST http://localhost:8000/api/orders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {"product_id": 1, "quantity": 2},
      {"product_id": 3, "quantity": 1}
    ]
  }'
```

### Update Order Status

```bash
curl -X PUT http://localhost:8000/api/orders/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "shipped"}'
```
