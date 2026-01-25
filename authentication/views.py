"""
Authentication and feed views for the application.
Handle user login, logout, signup, and access to the feed.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from . import forms
from django.contrib.auth import login, authenticate, logout
from django.views.generic import View


# Login view
class LoginPageView(View):
    """Display and process the user login form."""

    template_name = 'authentication/login.html'
    form_class = forms.LoginForm

    def get(self, request):
        """Display the login form or redirects authenticated users."""
        if request.user.is_authenticated:
            return redirect('reviews:feed')
        form = self.form_class()
        return render(
            request,
            self.template_name,
            context={
                'form': form,
                'message': ''
            }
        )

    def post(self, request):
        """Authenticate and log the user in."""
        form = self.form_class(request.POST)
        message = ''
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                return redirect('reviews:feed')
            else:
                message = 'Identifiants invalides.'
        return render(
            request,
            self.template_name,
            context={
                'form': form,
                'message': message
            }
        )


# Logout view
class LogoutPageView(View):
    """Log out the current user."""

    def get(self, request):
        """Log out the user and redirect to the login page."""
        logout(request)
        return redirect('authentication:login')


# Signup view
class SignupPageView(View):
    """Display and process the user signup form."""

    template_name = 'authentication/signup.html'
    form_class = forms.SignupForm

    def get(self, request):
        """Display the signup form."""
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """Create a new user account and log the user in."""
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('reviews:feed')
        return render(request, self.template_name, {'form': form})


# Feed view
class FeedPageView(LoginRequiredMixin, View):
    """Display the user feed page."""

    template_name = 'authentication/feed.html'
    login_url = 'authentication:login'

    def get(self, request):
        """Display the feed for authenticated users."""
        return render(request, self.template_name)
