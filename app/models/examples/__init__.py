"""
Example models demonstrating Laravel-style features.

These models serve as reference implementations showing how to use:
- Attribute Casting
- Accessors and Mutators
- Model Events and Observers
- Query Scopes
- Mass Assignment Protection
- Route Model Binding

Import and study these for patterns to use in your own models.
"""
from app.models.examples.post import Post, PostObserver

__all__ = ["Post", "PostObserver"]
