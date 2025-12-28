from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from reviews.forms import TicketForm
from reviews.models import Ticket


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
            return redirect('reviews:user-posts')
        return render(request, self.template_name, {'form': form})


class UserPostsPageView(LoginRequiredMixin, View):
    template_name = 'reviews/user_posts.html'
    login_url = 'authentication:login'

    def get(self, request):
        user_tickets = (
            Ticket.objects
            .filter(user=request.user)
            .order_by('-time_created')
        )
        return render(request, self.template_name, {
            'tickets': user_tickets
        })


class TicketUpdatePageView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'reviews/ticket_create.html'
    login_url = 'authentication:login'

    def get_object(self):
        return get_object_or_404(Ticket, id=self.kwargs['id'])

    def test_func(self):
        ticket = self.get_object()
        return ticket.user == self.request.user

    def get(self, request, id):
        ticket = self.get_object()
        form = TicketForm(instance=ticket)
        return render(request, self.template_name, {'form': form})

    def post(self, request, id):
        ticket = self.get_object()
        form = TicketForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect('reviews:user-posts')
        return render(request, self.template_name, {'form': form})


class TicketDeletePageView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = 'reviews/ticket_delete_confirm.html'
    login_url = 'authentication:login'

    def get_object(self):
        return get_object_or_404(Ticket, id=self.kwargs['id'])

    def test_func(self):
        ticket = self.get_object()
        return ticket.user == self.request.user

    def get(self, request, id):
        ticket = self.get_object()
        return render(request, self.template_name, {'ticket': ticket})

    def post(self, request, id):
        ticket = self.get_object()
        ticket.delete()
        return redirect('reviews:user-posts')
