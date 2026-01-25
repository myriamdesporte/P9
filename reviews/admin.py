"""
Handle admin configuration for the reviews app.
"""

from django.contrib import admin

from reviews.models import Ticket, Review, UserFollows


class TicketAdmin(admin.ModelAdmin):
    """Display and filter Ticket objects in the Django admin."""

    list_display = ('title', 'user', 'time_created')
    list_filter = ('user', 'time_created')
    search_fields = ('title', 'description')


class ReviewAdmin(admin.ModelAdmin):
    """Display and filter Review objects in the Django admin."""

    list_display = ('headline', 'rating', 'user', 'ticket', 'time_created')
    list_filter = ('rating', 'user')
    search_fields = ('headline', 'body')


class UserFollowsAdmin(admin.ModelAdmin):
    """Display and filter UserFollows objects in the Django admin."""

    list_display = ('user', 'followed_user')
    search_fields = ('user__username', 'followed_user__username')


admin.site.register(Ticket, TicketAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(UserFollows, UserFollowsAdmin)
