# Example: E-commerce API

Build an e-commerce backend with Fastpy.

## Overview

We'll create:
- Products with categories
- Shopping cart
- Orders with items
- Inventory management

## Generate Resources

```bash
# Category
python cli.py make:resource Category \
  -f name:string:required,max:100 \
  -f slug:slug:required,unique,index \
  -f parent_id:integer:foreign:categories.id,nullable \
  -m

# Product
python cli.py make:resource Product \
  -f name:string:required,max:200 \
  -f slug:slug:required,unique,index \
  -f description:text:nullable \
  -f price:money:required,min:0 \
  -f sale_price:money:nullable \
  -f sku:string:required,unique,max:50 \
  -f quantity:integer:default:0,min:0 \
  -f is_active:boolean:default:true \
  -f category_id:integer:foreign:categories.id \
  -m -p

# Cart
python cli.py make:resource Cart \
  -f user_id:integer:foreign:users.id,unique \
  -m -p

# CartItem
python cli.py make:resource CartItem \
  -f cart_id:integer:required,foreign:carts.id \
  -f product_id:integer:required,foreign:products.id \
  -f quantity:integer:required,min:1 \
  -m -p

# Order
python cli.py make:resource Order \
  -f order_number:string:required,unique,index \
  -f user_id:integer:required,foreign:users.id \
  -f status:string:default:pending \
  -f subtotal:money:required \
  -f tax:money:default:0 \
  -f total:money:required \
  -f notes:text:nullable \
  -f shipped_at:datetime:nullable \
  -m -p

# OrderItem
python cli.py make:model OrderItem \
  -f order_id:integer:required,foreign:orders.id \
  -f product_id:integer:required,foreign:products.id \
  -f quantity:integer:required,min:1 \
  -f unit_price:money:required \
  -f total:money:required \
  -m
```

## Order Status Enum

```bash
python cli.py make:enum OrderStatus
```

```python
# app/enums/order_status.py
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
```

## Cart Service

```python
# app/services/cart_service.py
from decimal import Decimal
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.product import Product
from app.utils.exceptions import NotFoundException, BadRequestException

class CartService:
    @staticmethod
    async def get_or_create(session: AsyncSession, user_id: int) -> Cart:
        result = await session.execute(
            select(Cart).where(Cart.user_id == user_id)
        )
        cart = result.scalar_one_or_none()

        if not cart:
            cart = Cart(user_id=user_id)
            session.add(cart)
            await session.commit()
            await session.refresh(cart)

        return cart

    @staticmethod
    async def add_item(
        session: AsyncSession,
        cart: Cart,
        product_id: int,
        quantity: int
    ) -> CartItem:
        # Check product exists and has stock
        product = await session.get(Product, product_id)
        if not product:
            raise NotFoundException("Product not found")

        if product.quantity < quantity:
            raise BadRequestException("Insufficient stock")

        # Check if already in cart
        result = await session.execute(
            select(CartItem)
            .where(CartItem.cart_id == cart.id)
            .where(CartItem.product_id == product_id)
        )
        item = result.scalar_one_or_none()

        if item:
            item.quantity += quantity
        else:
            item = CartItem(
                cart_id=cart.id,
                product_id=product_id,
                quantity=quantity
            )
            session.add(item)

        await session.commit()
        await session.refresh(item)
        return item

    @staticmethod
    async def get_total(session: AsyncSession, cart: Cart) -> Decimal:
        result = await session.execute(
            select(CartItem).where(CartItem.cart_id == cart.id)
        )
        items = result.scalars().all()

        total = Decimal('0')
        for item in items:
            product = await session.get(Product, item.product_id)
            price = product.sale_price or product.price
            total += price * item.quantity

        return total
```

## Order Service

```python
# app/services/order_service.py
import uuid
from decimal import Decimal
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.order import Order
from app.models.order_item import OrderItem
from app.models.cart_item import CartItem
from app.models.product import Product
from app.enums.order_status import OrderStatus
from app.utils.exceptions import BadRequestException

class OrderService:
    TAX_RATE = Decimal('0.10')  # 10%

    @staticmethod
    async def create_from_cart(
        session: AsyncSession,
        user_id: int,
        cart: Cart
    ) -> Order:
        # Get cart items
        result = await session.execute(
            select(CartItem).where(CartItem.cart_id == cart.id)
        )
        items = result.scalars().all()

        if not items:
            raise BadRequestException("Cart is empty")

        # Calculate totals
        subtotal = Decimal('0')
        order_items = []

        for item in items:
            product = await session.get(Product, item.product_id)

            # Check stock
            if product.quantity < item.quantity:
                raise BadRequestException(
                    f"Insufficient stock for {product.name}"
                )

            price = product.sale_price or product.price
            item_total = price * item.quantity
            subtotal += item_total

            order_items.append({
                'product_id': product.id,
                'quantity': item.quantity,
                'unit_price': price,
                'total': item_total
            })

            # Reserve stock
            product.quantity -= item.quantity

        tax = subtotal * OrderService.TAX_RATE
        total = subtotal + tax

        # Create order
        order = Order(
            order_number=f"ORD-{uuid.uuid4().hex[:8].upper()}",
            user_id=user_id,
            status=OrderStatus.PENDING,
            subtotal=subtotal,
            tax=tax,
            total=total
        )
        session.add(order)
        await session.flush()

        # Create order items
        for item_data in order_items:
            order_item = OrderItem(order_id=order.id, **item_data)
            session.add(order_item)

        # Clear cart
        for item in items:
            await session.delete(item)

        await session.commit()
        await session.refresh(order)
        return order
```

## API Routes

```python
# app/routes/cart_routes.py
from fastapi import APIRouter, Depends
from app.services.cart_service import CartService

router = APIRouter()

@router.get("/")
async def get_cart(
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_active_user)
):
    cart = await CartService.get_or_create(session, current_user.id)
    items = await CartService.get_items(session, cart)
    total = await CartService.get_total(session, cart)

    return success_response(data={
        "items": items,
        "total": str(total)
    })

@router.post("/items")
async def add_to_cart(
    data: AddToCartRequest,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_active_user)
):
    cart = await CartService.get_or_create(session, current_user.id)
    item = await CartService.add_item(
        session, cart, data.product_id, data.quantity
    )
    return success_response(data=item, message="Added to cart")

@router.post("/checkout")
async def checkout(
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_active_user)
):
    cart = await CartService.get_or_create(session, current_user.id)
    order = await OrderService.create_from_cart(session, current_user.id, cart)
    return success_response(data=order, message="Order created")
```

## Product Search

```python
@router.get("/search")
async def search_products(
    q: str = Query(..., min_length=2),
    category: Optional[int] = None,
    min_price: Optional[Decimal] = None,
    max_price: Optional[Decimal] = None,
    page: int = 1,
    session: AsyncSession = Depends(get_session)
):
    query = select(Product).where(
        Product.is_active == True,
        Product.deleted_at.is_(None)
    )

    # Text search
    query = query.where(
        or_(
            Product.name.ilike(f"%{q}%"),
            Product.description.ilike(f"%{q}%")
        )
    )

    # Filters
    if category:
        query = query.where(Product.category_id == category)
    if min_price:
        query = query.where(Product.price >= min_price)
    if max_price:
        query = query.where(Product.price <= max_price)

    params = PaginationParams(page=page)
    result = await paginate(session, query, params)
    return paginated_response(**result.__dict__)
```

## API Usage

```bash
# Add to cart
curl -X POST http://localhost:8000/api/cart/items \
  -H "Authorization: Bearer TOKEN" \
  -d '{"product_id": 1, "quantity": 2}'

# View cart
curl http://localhost:8000/api/cart \
  -H "Authorization: Bearer TOKEN"

# Checkout
curl -X POST http://localhost:8000/api/cart/checkout \
  -H "Authorization: Bearer TOKEN"

# View orders
curl http://localhost:8000/api/orders \
  -H "Authorization: Bearer TOKEN"
```
