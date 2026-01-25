"""
Define the reviews app configuration and ensure signals are loaded on startup.
"""
from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    """Configure the reviews app and load signals on ready."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reviews'

    def ready(self):
        """Import signals to connect model events."""
        import reviews.signals  # noqa: F401
