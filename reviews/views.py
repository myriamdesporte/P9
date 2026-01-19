from itertools import chain
from django.db.models import CharField, Value
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from reviews.forms import TicketForm, ReviewForm, FollowUserForm
from reviews.models import Ticket, UserFollows, Review

User = get_user_model()


class FeedPageView(LoginRequiredMixin, View):
    template_name = 'reviews/feed.html'
    login_url = 'authentication:login'

    def get_users_viewable_tickets(self, user):
        # User tickets
        tickets = Ticket.objects.filter(user=user)

        # Tickets from followed users
        follows = UserFollows.objects.filter(user=user)
        for follow in follows:
            tickets = tickets | Ticket.objects.filter(
                user=follow.followed_user
            )

        # Remove tickets with self-review
        tickets_to_remove = Ticket.objects.none()
        for ticket in tickets:
            if Review.objects.filter(ticket=ticket, user=ticket.user).exists():
                tickets_to_remove = tickets_to_remove | Ticket.objects.filter(
                    pk=ticket.pk
                )

        tickets = tickets.exclude(
            pk__in=tickets_to_remove.values_list('pk', flat=True)
        )

        return tickets

    def get_users_viewable_reviews(self, user):
        # User reviews
        reviews = Review.objects.filter(user=user)

        # Reviews from followed users
        follows = UserFollows.objects.filter(user=user)
        for follow in follows:
            reviews = reviews | Review.objects.filter(
                user=follow.followed_user
            )

        # Reviews on user's tickets
        user_tickets = Ticket.objects.filter(user=user)
        for ticket in user_tickets:
            reviews = reviews | Review.objects.filter(ticket=ticket)

        return reviews

    def get(self, request):
        user = request.user

        tickets = self.get_users_viewable_tickets(user)
        tickets = tickets.annotate(content_type=Value('TICKET', CharField()))
        reviews = self.get_users_viewable_reviews(user)
        reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))

        feed_items = sorted(
            chain(reviews, tickets),
            key=lambda item: item.time_created,
            reverse=True
        )

        return render(request, self.template_name, {'feed_items': feed_items})


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


class SubscriptionsPageView(LoginRequiredMixin, View):
    template_name = 'reviews/subscriptions.html'
    login_url = 'authentication:login'

    def get(self, request):
        form = FollowUserForm()
        return render(request, self.template_name, {
            'form': form,
        })

    def post(self, request):
        if 'unfollow_user_id' in request.POST:
            user_id = request.POST.get('unfollow_user_id')
            try:
                user_to_unfollow = User.objects.get(id=user_id)
                UserFollows.objects.filter(
                    user=request.user,
                    followed_user=user_to_unfollow
                ).delete()
                messages.success(
                    request,
                    f"Vous ne suivez plus {user_to_unfollow.username}."
                )
            except User.DoesNotExist:
                messages.error(request, "Utilisateur introuvable.")
            return redirect('reviews:subscriptions')

        form = FollowUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']

            try:
                user_to_follow = User.objects.get(username=username)
            except User.DoesNotExist:
                messages.error(
                    request,
                    f"L'utilisateur '{username}' n'existe pas."
                )
                return render(request, self.template_name, {'form': form})

            if user_to_follow == request.user:
                messages.error(
                    request,
                    "Vous ne pouvez pas vous suivre vous-même."
                )
                return render(request, self.template_name, {'form': form})

            UserFollows.objects.get_or_create(
                user=request.user,
                followed_user=user_to_follow
            )
            messages.success(request, f"Vous suivez maintenant {username}.")
            return redirect('reviews:subscriptions')

        return render(request, self.template_name, {'form': form})


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


class TicketAndReviewCreatePageView(LoginRequiredMixin, View):
    template_name = 'reviews/ticket_and_review_create.html'
    login_url = 'authentication:login'

    def get(self, request):
        ticket_form = TicketForm()
        review_form = ReviewForm()
        return render(request, self.template_name, {
            'ticket_form': ticket_form,
            'review_form': review_form,
        })

    def post(self, request):
        ticket_form = TicketForm(request.POST, request.FILES)
        review_form = ReviewForm(request.POST)

        if ticket_form.is_valid() and review_form.is_valid():
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            ticket.save()

            review = review_form.save(commit=False)
            review.user = request.user
            review.ticket = ticket
            review.save()

            return redirect('reviews:user-posts')

        return render(request, self.template_name, {
            'ticket_form': ticket_form,
            'review_form': review_form,
        })
