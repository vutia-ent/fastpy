"""
HasEvents - Model Lifecycle Events.

Provides Laravel-style model events for hooking into model lifecycle.

Events:
    - creating/created: Before/after INSERT
    - updating/updated: Before/after UPDATE
    - saving/saved: Before/after INSERT or UPDATE
    - deleting/deleted: Before/after DELETE
    - restoring/restored: Before/after restore from soft delete

Usage:
    class User(BaseModel, HasEvents, table=True):
        @classmethod
        def booted(cls):
            # Register event handlers
            cls.creating(lambda user: setattr(user, 'uuid', str(uuid4())))
            cls.created(lambda user: send_welcome_email(user))

    # Or use an Observer class
    class UserObserver(ModelObserver):
        def creating(self, user):
            user.uuid = str(uuid4())

        def created(self, user):
            send_welcome_email(user)

    User.observe(UserObserver())
"""
from typing import Any, Callable, ClassVar, Dict, List, Optional, Type, TypeVar

T = TypeVar("T")


class ModelObserver:
    """
    Base class for model observers.

    Observers group related event handlers for a model.

    Usage:
        class UserObserver(ModelObserver):
            def creating(self, user: User) -> None:
                user.uuid = str(uuid4())

            def created(self, user: User) -> None:
                Mail.to(user.email).send('welcome', {'user': user})

            def updating(self, user: User) -> None:
                pass

            def updated(self, user: User) -> None:
                Cache.forget(f'user:{user.id}')

            def deleting(self, user: User) -> bool:
                # Return False to cancel deletion
                if user.is_admin:
                    return False
                return True

            def deleted(self, user: User) -> None:
                # Cleanup after deletion
                Storage.delete(user.avatar_path)

        # Register the observer
        User.observe(UserObserver())
    """

    def retrieved(self, model: Any) -> None:
        """Called after a model is retrieved from the database."""
        pass

    def creating(self, model: Any) -> Optional[bool]:
        """Called before a model is created. Return False to cancel."""
        pass

    def created(self, model: Any) -> None:
        """Called after a model is created."""
        pass

    def updating(self, model: Any) -> Optional[bool]:
        """Called before a model is updated. Return False to cancel."""
        pass

    def updated(self, model: Any) -> None:
        """Called after a model is updated."""
        pass

    def saving(self, model: Any) -> Optional[bool]:
        """Called before a model is saved (create or update). Return False to cancel."""
        pass

    def saved(self, model: Any) -> None:
        """Called after a model is saved (create or update)."""
        pass

    def deleting(self, model: Any) -> Optional[bool]:
        """Called before a model is deleted. Return False to cancel."""
        pass

    def deleted(self, model: Any) -> None:
        """Called after a model is deleted."""
        pass

    def restoring(self, model: Any) -> Optional[bool]:
        """Called before a soft-deleted model is restored. Return False to cancel."""
        pass

    def restored(self, model: Any) -> None:
        """Called after a soft-deleted model is restored."""
        pass

    def force_deleting(self, model: Any) -> Optional[bool]:
        """Called before a model is force deleted. Return False to cancel."""
        pass

    def force_deleted(self, model: Any) -> None:
        """Called after a model is force deleted."""
        pass


class EventDispatcher:
    """Manages event handlers for a model class."""

    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
        self._observers: List[ModelObserver] = []

    def register(self, event: str, handler: Callable) -> None:
        """Register a handler for an event."""
        if event not in self._handlers:
            self._handlers[event] = []
        self._handlers[event].append(handler)

    def observe(self, observer: ModelObserver) -> None:
        """Register an observer."""
        self._observers.append(observer)

    def dispatch(self, event: str, model: Any) -> bool:
        """
        Dispatch an event to all handlers.

        Returns False if any handler returns False (to cancel the operation).
        """
        # Call observer methods first
        for observer in self._observers:
            handler = getattr(observer, event, None)
            if handler:
                result = handler(model)
                if result is False:
                    return False

        # Call registered handlers
        handlers = self._handlers.get(event, [])
        for handler in handlers:
            result = handler(model)
            if result is False:
                return False

        return True

    def clear(self, event: Optional[str] = None) -> None:
        """Clear handlers for an event or all events."""
        if event:
            self._handlers.pop(event, None)
        else:
            self._handlers.clear()
            self._observers.clear()


class HasEvents:
    """
    Mixin that provides model lifecycle events.

    Override the `booted` classmethod to register event handlers:

        class User(BaseModel, HasEvents, table=True):
            @classmethod
            def booted(cls):
                cls.creating(lambda user: setattr(user, 'uuid', str(uuid4())))

    Or use observers for complex logic:

        User.observe(UserObserver())

    Events (in order of execution):
        For create: saving -> creating -> [INSERT] -> created -> saved
        For update: saving -> updating -> [UPDATE] -> updated -> saved
        For delete: deleting -> [DELETE] -> deleted
        For restore: restoring -> [RESTORE] -> restored
    """

    # Event dispatcher per model class
    _event_dispatcher: ClassVar[Optional[EventDispatcher]] = None
    _booted: ClassVar[bool] = False

    @classmethod
    def _get_dispatcher(cls) -> EventDispatcher:
        """Get or create the event dispatcher for this class."""
        if cls._event_dispatcher is None:
            cls._event_dispatcher = EventDispatcher()
        return cls._event_dispatcher

    @classmethod
    def _boot_if_needed(cls) -> None:
        """Boot the model if not already booted."""
        if not cls._booted:
            cls._booted = True
            cls.booted()

    @classmethod
    def booted(cls) -> None:
        """
        Override this method to register event handlers.

        Called once when the model class is first used.

        Example:
            @classmethod
            def booted(cls):
                cls.creating(lambda model: setattr(model, 'uuid', str(uuid4())))
                cls.created(lambda model: log.info(f"Created {model}"))
        """
        pass

    # ==========================================================================
    # EVENT REGISTRATION METHODS
    # ==========================================================================

    @classmethod
    def creating(cls, handler: Callable) -> None:
        """Register a handler for the 'creating' event."""
        cls._get_dispatcher().register('creating', handler)

    @classmethod
    def created(cls, handler: Callable) -> None:
        """Register a handler for the 'created' event."""
        cls._get_dispatcher().register('created', handler)

    @classmethod
    def updating(cls, handler: Callable) -> None:
        """Register a handler for the 'updating' event."""
        cls._get_dispatcher().register('updating', handler)

    @classmethod
    def updated(cls, handler: Callable) -> None:
        """Register a handler for the 'updated' event."""
        cls._get_dispatcher().register('updated', handler)

    @classmethod
    def saving(cls, handler: Callable) -> None:
        """Register a handler for the 'saving' event."""
        cls._get_dispatcher().register('saving', handler)

    @classmethod
    def saved(cls, handler: Callable) -> None:
        """Register a handler for the 'saved' event."""
        cls._get_dispatcher().register('saved', handler)

    @classmethod
    def deleting(cls, handler: Callable) -> None:
        """Register a handler for the 'deleting' event."""
        cls._get_dispatcher().register('deleting', handler)

    @classmethod
    def deleted(cls, handler: Callable) -> None:
        """Register a handler for the 'deleted' event."""
        cls._get_dispatcher().register('deleted', handler)

    @classmethod
    def restoring(cls, handler: Callable) -> None:
        """Register a handler for the 'restoring' event."""
        cls._get_dispatcher().register('restoring', handler)

    @classmethod
    def restored(cls, handler: Callable) -> None:
        """Register a handler for the 'restored' event."""
        cls._get_dispatcher().register('restored', handler)

    @classmethod
    def observe(cls, observer: ModelObserver) -> None:
        """
        Register an observer for this model.

        Example:
            User.observe(UserObserver())
        """
        cls._get_dispatcher().observe(observer)

    @classmethod
    def flush_event_listeners(cls) -> None:
        """Remove all event listeners."""
        cls._get_dispatcher().clear()
        cls._booted = False

    # ==========================================================================
    # EVENT FIRING METHODS (called by BaseModel)
    # ==========================================================================

    def fire_model_event(self, event: str) -> bool:
        """
        Fire a model event.

        Returns False if the event was cancelled by a handler.
        """
        self.__class__._boot_if_needed()
        return self.__class__._get_dispatcher().dispatch(event, self)

    def fire_creating(self) -> bool:
        """Fire creating and saving events. Returns False if cancelled."""
        if not self.fire_model_event('saving'):
            return False
        return self.fire_model_event('creating')

    def fire_created(self) -> None:
        """Fire created and saved events."""
        self.fire_model_event('created')
        self.fire_model_event('saved')

    def fire_updating(self) -> bool:
        """Fire updating and saving events. Returns False if cancelled."""
        if not self.fire_model_event('saving'):
            return False
        return self.fire_model_event('updating')

    def fire_updated(self) -> None:
        """Fire updated and saved events."""
        self.fire_model_event('updated')
        self.fire_model_event('saved')

    def fire_deleting(self) -> bool:
        """Fire deleting event. Returns False if cancelled."""
        return self.fire_model_event('deleting')

    def fire_deleted(self) -> None:
        """Fire deleted event."""
        self.fire_model_event('deleted')

    def fire_restoring(self) -> bool:
        """Fire restoring event. Returns False if cancelled."""
        return self.fire_model_event('restoring')

    def fire_restored(self) -> None:
        """Fire restored event."""
        self.fire_model_event('restored')
