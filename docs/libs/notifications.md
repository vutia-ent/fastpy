# Notify Facade

Multi-channel notifications (mail, database, Slack, SMS).

## Creating Notifications

```python
from fastpy_cli.libs import Notification

class OrderShippedNotification(Notification):
    def __init__(self, order):
        self.order = order

    def via(self, notifiable) -> list:
        """Define delivery channels."""
        return ['mail', 'database']

    def to_mail(self, notifiable) -> dict:
        """Mail representation."""
        return {
            'subject': f'Order #{self.order.id} has shipped!',
            'template': 'notifications/order_shipped',
            'data': {
                'order': self.order,
                'tracking_url': self.order.tracking_url
            }
        }

    def to_database(self, notifiable) -> dict:
        """Database representation."""
        return {
            'type': 'order_shipped',
            'data': {
                'order_id': self.order.id,
                'tracking_number': self.order.tracking_number
            }
        }
```

## Sending Notifications

```python
from fastpy_cli.libs import Notify

# Send to single user
Notify.send(user, OrderShippedNotification(order))

# Send to multiple users
Notify.send(users, OrderShippedNotification(order))

# Send immediately (skip queue)
Notify.send_now(user, OrderShippedNotification(order))

# Delay notification (seconds)
Notify.later(3600, user, OrderShippedNotification(order))
```

## Channels

### Mail Channel

```python
def to_mail(self, notifiable) -> dict:
    return {
        'subject': 'Welcome!',
        'template': 'welcome',
        'data': {'name': notifiable.name}
    }
```

### Database Channel

```python
def to_database(self, notifiable) -> dict:
    return {
        'type': 'welcome',
        'data': {'message': 'Welcome to our app!'}
    }
```

### Slack Channel

```python
def to_slack(self, notifiable) -> dict:
    return {
        'channel': '#notifications',
        'text': f'New order #{self.order.id}!',
        'blocks': [
            {
                'type': 'section',
                'text': {
                    'type': 'mrkdwn',
                    'text': f'*Order #{self.order.id}*\nTotal: ${self.order.total}'
                }
            }
        ]
    }
```

### SMS Channel

```python
def to_sms(self, notifiable) -> str:
    return f'Your order #{self.order.id} has shipped!'
```

### Broadcast Channel (WebSocket)

```python
def to_broadcast(self, notifiable) -> dict:
    return {
        'event': 'order.shipped',
        'data': {
            'order_id': self.order.id,
            'status': 'shipped'
        }
    }
```

## Conditional Channels

```python
def via(self, notifiable) -> list:
    channels = ['database']

    if notifiable.email_notifications:
        channels.append('mail')

    if notifiable.sms_notifications:
        channels.append('sms')

    return channels
```

## Conditional Sending

```python
def should_send(self, notifiable, channel: str) -> bool:
    """Determine if notification should be sent."""
    if channel == 'mail':
        return notifiable.email_verified

    if channel == 'sms':
        return notifiable.phone_verified

    return True
```

## On-Demand Notifications

Send to anonymous recipients:

```python
# Send to email without user
Notify.route('mail', 'guest@example.com') \
    .notify(OrderConfirmation(order))

# Multiple channels
Notify.route('mail', 'admin@example.com') \
    .route('slack', '#orders') \
    .notify(NewOrderNotification(order))
```

## Queue Configuration

```python
class OrderShippedNotification(Notification):
    # Queue name
    queue = 'notifications'

    # Delay in seconds
    delay = 0

    def __init__(self, order):
        self.order = order

    # Set queue per notification
    def on_queue(self, queue: str):
        self.queue = queue
        return self

    # Set delay
    def with_delay(self, seconds: int):
        self.delay = seconds
        return self
```

## Testing

```python
from fastpy_cli.libs import Notify

# Enable fake mode
Notify.fake()

# Send notifications
Notify.send(user, OrderShippedNotification(order))

# Assertions
Notify.assert_sent_to(user, OrderShippedNotification)
Notify.assert_sent_to(user, OrderShippedNotification, count=1)
Notify.assert_not_sent_to(user, OtherNotification)
Notify.assert_nothing_sent()
Notify.assert_count(1)
```

## Complete Example

```python
from fastpy_cli.libs import Notify, Notification

# Define notifications
class WelcomeNotification(Notification):
    def via(self, notifiable) -> list:
        return ['mail', 'database']

    def to_mail(self, notifiable) -> dict:
        return {
            'subject': 'Welcome to Our App!',
            'template': 'notifications/welcome',
            'data': {'name': notifiable.name}
        }

    def to_database(self, notifiable) -> dict:
        return {
            'type': 'welcome',
            'data': {'message': 'Welcome! Get started by completing your profile.'}
        }


class NewCommentNotification(Notification):
    def __init__(self, comment):
        self.comment = comment

    def via(self, notifiable) -> list:
        channels = ['database']

        # Only email if user wants notifications
        if notifiable.notify_comments:
            channels.append('mail')

        return channels

    def to_mail(self, notifiable) -> dict:
        return {
            'subject': f'{self.comment.author.name} commented on your post',
            'template': 'notifications/new_comment',
            'data': {
                'comment': self.comment,
                'post': self.comment.post
            }
        }

    def to_database(self, notifiable) -> dict:
        return {
            'type': 'new_comment',
            'data': {
                'comment_id': self.comment.id,
                'post_id': self.comment.post_id,
                'author_name': self.comment.author.name
            }
        }


class OrderStatusNotification(Notification):
    def __init__(self, order, status: str):
        self.order = order
        self.status = status

    def via(self, notifiable) -> list:
        channels = ['mail', 'database']

        # Add SMS for important statuses
        if self.status in ['shipped', 'delivered']:
            channels.append('sms')

        return channels

    def to_mail(self, notifiable) -> dict:
        templates = {
            'confirmed': 'notifications/order_confirmed',
            'shipped': 'notifications/order_shipped',
            'delivered': 'notifications/order_delivered'
        }

        return {
            'subject': f'Order #{self.order.id} {self.status}',
            'template': templates.get(self.status, 'notifications/order_update'),
            'data': {'order': self.order, 'status': self.status}
        }

    def to_sms(self, notifiable) -> str:
        messages = {
            'shipped': f'Your order #{self.order.id} has shipped! Track: {self.order.tracking_url}',
            'delivered': f'Your order #{self.order.id} has been delivered!'
        }
        return messages.get(self.status, f'Order #{self.order.id} update: {self.status}')

    def to_database(self, notifiable) -> dict:
        return {
            'type': f'order_{self.status}',
            'data': {
                'order_id': self.order.id,
                'status': self.status
            }
        }


# Usage in services
class UserService:
    def register(self, data: dict) -> User:
        user = User.create(**data)
        Notify.send(user, WelcomeNotification())
        return user


class CommentService:
    def create(self, post_id: int, author: User, content: str) -> Comment:
        comment = Comment.create(
            post_id=post_id,
            author=author,
            content=content
        )

        # Notify post author
        post = Post.find(post_id)
        if post.author_id != author.id:
            Notify.send(post.author, NewCommentNotification(comment))

        return comment


class OrderService:
    def update_status(self, order: Order, status: str):
        order.status = status
        order.save()

        Notify.send(order.user, OrderStatusNotification(order, status))
```
