from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views import View
from reviews.forms import TicketForm


class FeedPageView(LoginRequiredMixin, View):
    template_name = 'reviews/feed.html'
    login_url = 'authentication:login'

    def get(self, request):
        return render(request, self.template_name)

class TicketCreatePageView(LoginRequiredMixin, View):
    template_name = 'reviews/ticket_create.html'
    login_url = 'authentication:login'

    def get(self, request):
        form = TicketForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return redirect('reviews:feed')
        return render(request, self.template_name, {'form': form})
