from django.urls import path
from . import views

app_name = "reviews"

urlpatterns = [
    path('', views.FeedPageView.as_view(), name='feed'),
    path('ticket/create/', views.TicketCreatePageView.as_view(), name='ticket-create'),
]
