# Event Facade

Event-driven architecture with listeners and subscribers.

## Basic Usage

```python
from fastpy_cli.libs import Event

# Register listener
Event.listen('user.registered', lambda data: send_welcome_email(data['user']))

# Dispatch event
Event.dispatch('user.registered', {'user': user})
```

## Decorator Syntax

```python
@Event.listen('user.registered')
def send_welcome(data):
    Mail.to(data['user'].email).send('welcome')

@Event.listen('order.created')
def notify_warehouse(data):
    warehouse_api.notify(data['order'])
```

## Multiple Events

```python
# Listen to multiple events
@Event.listen(['user.registered', 'user.updated'])
def log_user_activity(data):
    logger.info(f"User activity: {data}")
```

## Wildcard Listeners

```python
# Listen to all user events
Event.listen('user.*', lambda data: log_user_activity(data))

# Listen to all "created" events
Event.listen('*.created', lambda data: log_creation(data))
```

## Event Subscribers

Group related listeners in a class:

```python
class UserSubscriber:
    def subscribe(self, events):
        events.listen('user.registered', self.on_registered)
        events.listen('user.deleted', self.on_deleted)
        events.listen('user.updated', self.on_updated)

    def on_registered(self, data):
        user = data['user']
        Mail.to(user.email).send('welcome')
        logger.info(f"User registered: {user.id}")

    def on_deleted(self, data):
        user = data['user']
        Mail.to(user.email).send('goodbye')

    def on_updated(self, data):
        logger.info(f"User updated: {data['user'].id}")

# Register subscriber
Event.subscribe(UserSubscriber())
```

## Stopping Propagation

Return a value to stop other listeners:

```python
def validate_order(data):
    if not data['order'].is_valid:
        return False  # Stops propagation

Event.listen('order.created', validate_order)
Event.listen('order.created', process_order)  # Won't run if validation fails
```

## Until Pattern

Dispatch until a listener returns a non-None value:

```python
# First listener to return a value wins
result = Event.until('order.calculate_discount', {'order': order})
```

## Async Events

Queue events for async processing:

```python
# Queue event (returns job ID)
job_id = Event.dispatch_async('user.registered', {'user': user})

# Alias
Event.push('user.registered', {'user': user})
```

## Managing Listeners

```python
# Check if event has listeners
if Event.has_listeners('user.registered'):
    print('Has listeners')

# Remove all listeners for event
Event.forget('user.registered')

# Remove all listeners
Event.flush()
```

## Testing

```python
from fastpy_cli.libs import Event

# Enable fake mode
Event.fake()

# Dispatch events
Event.dispatch('user.registered', {'user': user})

# Assertions
Event.assert_dispatched('user.registered')
Event.assert_dispatched('user.registered', count=1)
Event.assert_not_dispatched('other.event')

# Assert with payload
Event.assert_dispatched_with('user.registered', user=user)
```

## Complete Example

```python
from fastpy_cli.libs import Event, Mail, Queue

# Define events
class UserEvents:
    REGISTERED = 'user.registered'
    DELETED = 'user.deleted'
    PASSWORD_CHANGED = 'user.password_changed'

class OrderEvents:
    CREATED = 'order.created'
    PAID = 'order.paid'
    SHIPPED = 'order.shipped'
    DELIVERED = 'order.delivered'


# Subscriber for user events
class UserEventSubscriber:
    def subscribe(self, events):
        events.listen(UserEvents.REGISTERED, self.on_registered)
        events.listen(UserEvents.PASSWORD_CHANGED, self.on_password_changed)

    def on_registered(self, data):
        user = data['user']

        # Send welcome email
        Mail.to(user.email).send('welcome', {'name': user.name})

        # Track analytics
        analytics.track('user_registered', {'user_id': user.id})

    def on_password_changed(self, data):
        user = data['user']

        # Send security notification
        Mail.to(user.email) \
            .subject('Password Changed') \
            .send('security/password_changed')


# Subscriber for order events
class OrderEventSubscriber:
    def subscribe(self, events):
        events.listen(OrderEvents.CREATED, self.on_created)
        events.listen(OrderEvents.PAID, self.on_paid)
        events.listen(OrderEvents.SHIPPED, self.on_shipped)

    def on_created(self, data):
        order = data['order']
        Mail.to(order.user.email).send('order/confirmation', {'order': order})

    def on_paid(self, data):
        order = data['order']
        Queue.push(ProcessOrderJob(order_id=order.id))

    def on_shipped(self, data):
        order = data['order']
        Mail.to(order.user.email).send('order/shipped', {
            'order': order,
            'tracking_number': data['tracking_number']
        })


# Register subscribers
Event.subscribe(UserEventSubscriber())
Event.subscribe(OrderEventSubscriber())


# Usage in application
class UserService:
    def register(self, data: dict) -> User:
        user = User.create(**data)
        Event.dispatch(UserEvents.REGISTERED, {'user': user})
        return user


class OrderService:
    def create(self, user: User, items: list) -> Order:
        order = Order.create(user=user, items=items)
        Event.dispatch(OrderEvents.CREATED, {'order': order})
        return order

    def mark_shipped(self, order: Order, tracking_number: str):
        order.status = 'shipped'
        order.tracking_number = tracking_number
        order.save()

        Event.dispatch(OrderEvents.SHIPPED, {
            'order': order,
            'tracking_number': tracking_number
        })
```
