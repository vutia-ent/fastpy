# Queue Facade

Job queuing for background processing.

## Supported Connections

- `sync` (default) - Immediate execution
- `redis` - Redis queue
- `database` - Database queue

## Creating Jobs

```python
from fastpy_cli.libs import Job

class SendEmailJob(Job):
    def __init__(self, user_id: int, template: str):
        self.user_id = user_id
        self.template = template

    def handle(self):
        user = get_user(self.user_id)
        send_email(user.email, self.template)

    def failed(self, exception: Exception):
        # Handle failure (optional)
        log_error(f"Failed to send email: {exception}")
```

## Dispatching Jobs

```python
from fastpy_cli.libs import Queue

# Push job to queue
Queue.push(SendEmailJob(user_id=1, template='welcome'))

# Delay job (seconds)
Queue.later(60, SendEmailJob(user_id=1, template='reminder'))

# Push to specific queue
Queue.on('emails').push(SendEmailJob(user_id=1, template='welcome'))
```

## Job Configuration

```python
class ProcessOrderJob(Job):
    # Queue name
    queue = 'orders'

    # Connection name
    connection = 'redis'

    # Delay in seconds
    delay = 0

    # Number of retries
    tries = 3

    # Timeout in seconds
    timeout = 60

    # Seconds to wait before retry
    retry_after = 90

    def handle(self):
        # Process order
        pass
```

## Job Lifecycle Hooks

```python
class MyJob(Job):
    def before(self):
        # Before job execution
        log.info("Starting job")

    def handle(self):
        # Main job logic
        pass

    def after(self):
        # After successful execution
        log.info("Job completed")

    def failed(self, exception: Exception):
        # On failure
        log.error(f"Job failed: {exception}")
```

## Job Chaining

Run jobs sequentially:

```python
Queue.chain([
    ProcessOrderJob(order_id=1),
    SendConfirmationJob(order_id=1),
    UpdateInventoryJob(order_id=1),
])
```

## Job Batching

Group jobs together:

```python
batch = Queue.batch([
    ProcessImageJob(image_id=1),
    ProcessImageJob(image_id=2),
    ProcessImageJob(image_id=3),
])

# Add callbacks
batch.then(lambda: print("All jobs completed"))
batch.on_success(lambda: notify_user())
batch.on_failure(lambda: alert_admin())
```

## Bulk Dispatch

```python
jobs = [
    SendEmailJob(user_id=1, template='welcome'),
    SendEmailJob(user_id=2, template='welcome'),
    SendEmailJob(user_id=3, template='welcome'),
]

Queue.bulk(jobs)
```

## Queue Operations

```python
# Get queue size
size = Queue.size('emails')

# Clear queue
Queue.clear('emails')

# Pop next job
job = Queue.pop('emails')
```

## Worker

```python
# Process jobs
Queue.work(
    queue='default',
    sleep=3.0,      # Sleep between jobs
    max_jobs=100,   # Max jobs to process
    timeout=60      # Job timeout
)
```

## Using Specific Connection

```python
# Use Redis
Queue.using('redis').push(MyJob())

# Get connection
redis_queue = Queue.connection('redis')
```

## Configuration

```bash
# Sync (default - immediate execution)
QUEUE_CONNECTION=sync

# Redis
QUEUE_CONNECTION=redis
REDIS_URL=redis://localhost:6379/0

# Database
QUEUE_CONNECTION=database
```

## Testing

```python
from fastpy_cli.libs import Queue

# Enable fake mode
Queue.fake()

# Dispatch jobs
Queue.push(SendEmailJob(user_id=1, template='welcome'))

# Assertions
Queue.assert_pushed(SendEmailJob)
Queue.assert_pushed(SendEmailJob, count=1)
Queue.assert_not_pushed(OtherJob)
Queue.assert_nothing_pushed()

# Assert with properties
Queue.assert_pushed_with(SendEmailJob, user_id=1, template='welcome')
```

## Complete Example

```python
from fastpy_cli.libs import Queue, Job
from app.models import Order, User

class ProcessOrderJob(Job):
    queue = 'orders'
    tries = 3
    timeout = 120

    def __init__(self, order_id: int):
        self.order_id = order_id

    def handle(self):
        order = Order.find(self.order_id)

        # Process payment
        payment_result = process_payment(order)

        if not payment_result.success:
            raise PaymentFailedException(payment_result.error)

        # Update order status
        order.status = 'paid'
        order.save()

    def failed(self, exception: Exception):
        order = Order.find(self.order_id)
        order.status = 'failed'
        order.error_message = str(exception)
        order.save()

        # Notify admin
        notify_admin(f"Order {self.order_id} failed: {exception}")


class OrderService:
    def create_order(self, user: User, items: list) -> Order:
        order = Order.create(user=user, items=items, status='pending')

        # Queue processing
        Queue.push(ProcessOrderJob(order_id=order.id))

        # Queue follow-up emails
        Queue.chain([
            SendOrderConfirmationJob(order_id=order.id),
            Queue.later(3600, SendOrderFollowUpJob(order_id=order.id)),
        ])

        return order
```
