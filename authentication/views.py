from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from . import forms
from django.contrib.auth import login, authenticate, logout
from django.views.generic import View

# Login view
class LoginPageView(View):
    template_name = 'authentication/login.html'
    form_class = forms.LoginForm

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('reviews:feed')
        form = self.form_class()
        return render(request, self.template_name, context={'form': form, 'message': ''})

    def post(self, request):
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
        return render(request, self.template_name, context={'form': form, 'message': message})

# Logout view
class LogoutPageView(View):
    def get(self, request):
        logout(request)
        return redirect('authentication:login')

# Signup view
class SignupPageView(View):
    template_name = 'authentication/signup.html'
    form_class = forms.SignupForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('reviews:feed')
        return render(request, self.template_name, {'form': form})

# Feed view
class FeedPageView(LoginRequiredMixin, View):
    template_name = 'authentication/feed.html'
    login_url = 'authentication:login'

    def get(self, request):
        return render(request, self.template_name)
