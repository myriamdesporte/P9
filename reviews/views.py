from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views import View

class FeedPageView(LoginRequiredMixin, View):
    template_name = 'reviews/feed.html'
    login_url = 'authentication:login'

    def get(self, request):
        return render(request, self.template_name)
