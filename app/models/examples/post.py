"""
Example Post Model - Demonstrates all Laravel-style features.

This model showcases:
- Attribute Casting (json, boolean, datetime)
- Accessors and Mutators
- Model Events
- Query Scopes
- Mass Assignment Protection
- Soft Deletes

Usage:
    # Create with mass assignment protection
    post = await Post.create(
        title="Hello World",
        body="Content here...",
        author_id=1,
        settings={'featured': True},  # Stored as JSON
    )

    # Query with scopes
    posts = await Post.query().published().popular(1000).get()

    # Use accessor
    print(post.excerpt)  # Auto-truncated body

    # Events fire automatically
    # - creating: generates slug from title
    # - created: could send notifications
"""
from datetime import datetime, timezone
from typing import Any, ClassVar, Dict, List, Optional

from sqlmodel import Field

from app.models.base import BaseModel
from app.models.concerns import (
    HasCasts,
    HasAttributes,
    HasEvents,
    HasScopes,
    GuardsAttributes,
    ModelObserver,
    accessor,
    mutator,
)


class PostObserver(ModelObserver):
    """
    Observer for Post model events.

    Keeps event handling logic separate from the model.
    """

    def creating(self, post: "Post") -> None:
        """Generate slug from title before saving."""
        if not post.slug and post.title:
            post.slug = self._slugify(post.title)

    def created(self, post: "Post") -> None:
        """After post is created."""
        # Could send notifications, update caches, etc.
        pass

    def updating(self, post: "Post") -> None:
        """Before post is updated."""
        # Could validate changes
        pass

    def deleting(self, post: "Post") -> bool:
        """Before post is deleted."""
        # Return False to cancel deletion
        # e.g., if post.is_featured: return False
        return True

    @staticmethod
    def _slugify(text: str) -> str:
        """Convert text to URL-friendly slug."""
        import re
        text = text.lower().strip()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[-\s]+', '-', text)
        return text


class Post(BaseModel, HasCasts, HasAttributes, HasEvents, HasScopes, GuardsAttributes, table=True):
    """
    Example Post model with all Laravel-style features.
    """

    __tablename__ = "posts"

    # ==========================================================================
    # FIELDS
    # ==========================================================================

    id: Optional[int] = Field(default=None, primary_key=True)
    author_id: int = Field(foreign_key="users.id")
    title: str = Field(max_length=255)
    slug: Optional[str] = Field(default=None, max_length=255, unique=True)
    body: str = Field(default="")
    excerpt_text: Optional[str] = Field(default=None, max_length=500)

    # These will be cast automatically
    settings: Optional[str] = Field(default=None)  # JSON stored as string
    is_published: bool = Field(default=False)
    is_featured: bool = Field(default=False)
    views: int = Field(default=0)

    published_at: Optional[datetime] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)
    updated_at: Optional[datetime] = Field(default=None)
    deleted_at: Optional[datetime] = Field(default=None)

    # ==========================================================================
    # CASTS - Auto-convert types
    # ==========================================================================

    _casts: ClassVar[Dict[str, str]] = {
        'settings': 'json',           # JSON string <-> dict
        'is_published': 'boolean',    # 1/0 <-> True/False
        'is_featured': 'boolean',
        'views': 'integer',
        'published_at': 'datetime',
    }

    # ==========================================================================
    # MASS ASSIGNMENT - Security
    # ==========================================================================

    _fillable: ClassVar[List[str]] = [
        'title',
        'body',
        'excerpt_text',
        'settings',
        'author_id',
    ]

    _guarded: ClassVar[List[str]] = [
        'id',
        'slug',        # Auto-generated
        'is_featured', # Admin only
        'views',       # System managed
    ]

    # ==========================================================================
    # SERIALIZATION
    # ==========================================================================

    _hidden: ClassVar[List[str]] = [
        'deleted_at',
    ]

    _appends: ClassVar[List[str]] = [
        'excerpt',
        'is_recent',
    ]

    # ==========================================================================
    # ACCESSORS - Computed Properties
    # ==========================================================================

    @accessor
    def excerpt(self) -> str:
        """Get truncated excerpt from body."""
        if self.excerpt_text:
            return self.excerpt_text
        if self.body:
            return self.body[:200] + '...' if len(self.body) > 200 else self.body
        return ''

    @accessor
    def is_recent(self) -> bool:
        """Check if post was created in last 7 days."""
        if not self.created_at:
            return False
        now = datetime.now(timezone.utc)
        delta = now - self.created_at.replace(tzinfo=timezone.utc)
        return delta.days < 7

    @accessor
    def reading_time(self) -> int:
        """Estimated reading time in minutes."""
        if not self.body:
            return 0
        words = len(self.body.split())
        return max(1, words // 200)  # 200 words per minute

    # ==========================================================================
    # MUTATORS - Transform on Set
    # ==========================================================================

    @mutator('title')
    def clean_title(self, value: str) -> str:
        """Clean and normalize title."""
        return value.strip() if value else ''

    # ==========================================================================
    # QUERY SCOPES
    # ==========================================================================

    @classmethod
    def scope_published(cls, query):
        """Only published posts."""
        return query.where(
            cls.is_published == True,
            cls.published_at <= datetime.now(timezone.utc)
        )

    @classmethod
    def scope_draft(cls, query):
        """Only draft (unpublished) posts."""
        return query.where(cls.is_published == False)

    @classmethod
    def scope_featured(cls, query):
        """Only featured posts."""
        return query.where(cls.is_featured == True)

    @classmethod
    def scope_popular(cls, query, min_views: int = 1000):
        """Posts with at least min_views views."""
        return query.where(cls.views >= min_views)

    @classmethod
    def scope_by_author(cls, query, author_id: int):
        """Posts by a specific author."""
        return query.where(cls.author_id == author_id)

    @classmethod
    def scope_recent(cls, query, days: int = 7):
        """Posts from the last N days."""
        from datetime import timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        return query.where(cls.created_at >= cutoff)

    @classmethod
    def scope_search(cls, query, term: str):
        """Search posts by title or body."""
        search_term = f"%{term}%"
        return query.where(
            (cls.title.like(search_term)) | (cls.body.like(search_term))
        )

    # ==========================================================================
    # EVENTS
    # ==========================================================================

    @classmethod
    def booted(cls):
        """Register event handlers when model is first used."""
        # Register the observer
        cls.observe(PostObserver())

        # Or inline event handlers:
        # cls.creating(lambda post: print(f"Creating: {post.title}"))
        # cls.created(lambda post: print(f"Created: {post.id}"))

    # ==========================================================================
    # CUSTOM METHODS
    # ==========================================================================

    def publish(self) -> "Post":
        """Mark post as published."""
        self.is_published = True
        self.published_at = datetime.now(timezone.utc)
        return self

    def unpublish(self) -> "Post":
        """Mark post as unpublished (draft)."""
        self.is_published = False
        self.published_at = None
        return self

    def increment_views(self) -> "Post":
        """Increment view count."""
        self.views = (self.views or 0) + 1
        return self
