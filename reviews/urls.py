from django.urls import path
from . import views

app_name = "reviews"

urlpatterns = [
    path('', views.FeedPageView.as_view(), name='feed'),
    path(
        'ticket/create/',
        views.TicketCreatePageView.as_view(),
        name='ticket-create'
    ),
    path('posts/', views.UserPostsPageView.as_view(), name='user-posts'),
    path(
        'ticket/<int:id>/update/',
        views.TicketUpdatePageView.as_view(),
        name='ticket-update'
    ),
    path(
        'ticket/<int:id>/delete/',
        views.TicketDeletePageView.as_view(),
        name='ticket-delete'
    ),
    path(
        'ticket-review/create/',
        views.TicketAndReviewCreatePageView.as_view(),
        name='ticket-and-review-create'
    ),
    path(
        'subscriptions/',
        views.SubscriptionsPageView.as_view(),
        name='subscriptions'
    ),
]
