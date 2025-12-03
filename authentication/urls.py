from django.urls import path
from . import views

app_name = "authentication"

urlpatterns = [
    path('login/', views.LoginPageView.as_view(), name='login'),
    path('logout/', views.LogoutPageView.as_view(), name='logout'),
    path('signup/', views.SignupPageView.as_view(), name='signup'),
    path('', views.FeedPageView.as_view(), name='feed'),
]
