"""
Handle reviews app views.
Handle feed display, user posts, subscriptions, tickets, and reviews.
"""

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
    """Display the feed of tickets and reviews for the current user."""

    template_name = 'reviews/feed.html'
    login_url = 'authentication:login'

    def get_users_viewable_tickets(self, user):
        """Return tickets the user can view, excluding self-reviews."""
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
        """
        Return reviews the user can view, including followed users and
        reviews on user's tickets.
        """
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
        """Display the feed page with tickets and reviews."""
        user = request.user

        tickets = self.get_users_viewable_tickets(user)
        tickets = tickets.annotate(content_type=Value('TICKET', CharField()))
        # Mark tickets with reviews
        for ticket in tickets:
            ticket.has_review = Review.objects.filter(
                ticket=ticket
            ).exists()
            ticket.show_review_button = (
                    ticket.user != user
                    and not ticket.has_review
            )

        reviews = self.get_users_viewable_reviews(user)
        reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))

        feed_items = sorted(
            chain(reviews, tickets),
            key=lambda item: item.time_created,
            reverse=True
        )

        return render(request, self.template_name, {'feed_items': feed_items})


class UserPostsPageView(LoginRequiredMixin, View):
    """Display the current user's tickets and reviews."""

    template_name = 'reviews/user_posts.html'
    login_url = 'authentication:login'

    def get(self, request):
        """
        Display the user's tickets and reviews in reverse
        chronological order
        """
        user_tickets = (Ticket.objects.filter(user=request.user))
        tickets = user_tickets.annotate(
            content_type=Value('TICKET', CharField())
        )
        user_reviews = (Review.objects.filter(user=request.user))
        reviews = user_reviews.annotate(
            content_type=Value('REVIEW', CharField())
        )

        feed_items = sorted(
            chain(reviews, tickets),
            key=lambda item: item.time_created,
            reverse=True
        )

        return render(request, self.template_name, {'feed_items': feed_items})


class SubscriptionsPageView(LoginRequiredMixin, View):
    """Display and process user's followed users."""

    template_name = 'reviews/subscriptions.html'
    login_url = 'authentication:login'

    def get(self, request):
        """Display the follow user form."""
        form = FollowUserForm()
        return render(request, self.template_name, {
            'form': form,
        })

    def post(self, request):
        """Process follow and unfollow actions for other users."""
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
    """Display and process the ticket creation form."""

    template_name = 'reviews/ticket_create.html'
    login_url = 'authentication:login'

    def get(self, request):
        """Display an empty ticket form."""
        form = TicketForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        """Create a new ticket from form data and save it."""
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return redirect('reviews:user-posts')
        return render(request, self.template_name, {'form': form})


class TicketUpdatePageView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Display and process the ticket update form for ticket owner."""

    template_name = 'reviews/ticket_create.html'
    login_url = 'authentication:login'

    def get_object(self):
        """Return the ticket to update."""
        return get_object_or_404(Ticket, id=self.kwargs['id'])

    def test_func(self):
        """Return True if current user is the ticket owner."""
        ticket = self.get_object()
        return ticket.user == self.request.user

    def get(self, request, id):
        """Display the ticket update form."""
        ticket = self.get_object()
        form = TicketForm(instance=ticket)
        return render(request, self.template_name, {'form': form})

    def post(self, request, id):
        """Update the ticket with form data."""
        ticket = self.get_object()
        form = TicketForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect('reviews:user-posts')
        return render(request, self.template_name, {'form': form})


class TicketAndReviewCreatePageView(LoginRequiredMixin, View):
    """Display and process creation of a ticket and its review."""

    template_name = 'reviews/ticket_and_review_create.html'
    login_url = 'authentication:login'

    def get(self, request):
        """Display empty ticket and review forms."""
        ticket_form = TicketForm()
        review_form = ReviewForm()
        return render(request, self.template_name, {
            'ticket_form': ticket_form,
            'review_form': review_form,
        })

    def post(self, request):
        """Create a ticket and review from form data and save both."""
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


class ReviewCreatePageView(LoginRequiredMixin, View):
    """Display and process creation of a review for a ticket."""

    template_name = 'reviews/review_create.html'
    login_url = 'authentication:login'

    def get_ticket(self, id):
        """Return the ticket for which to create the review."""
        return get_object_or_404(Ticket, id=id)

    def get(self, request, id):
        """Display the review form for a ticket."""
        ticket = self.get_ticket(id)
        form = ReviewForm()
        return render(
            request,
            self.template_name,
            {
                'ticket': ticket,
                'form': form,
            }
        )

    def post(self, request, id):
        """Create a review for a ticket from form data."""
        ticket = self.get_ticket(id)
        form = ReviewForm(request.POST, request.FILES)

        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.ticket = ticket
            review.save()
            return redirect('reviews:feed')

        return render(
            request,
            self.template_name,
            {
                'ticket': ticket,
                'form': form,
            }
        )


class ReviewUpdatePageView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Display and process the review update form for review owner."""

    template_name = 'reviews/review_create.html'
    login_url = 'authentication:login'

    def get_object(self):
        """Return the review to update."""
        return get_object_or_404(Review, id=self.kwargs['id'])

    def test_func(self):
        """Return True if current user is the review owner."""
        review = self.get_object()
        return review.user == self.request.user

    def get(self, request, id):
        """Display the review update form."""
        review = self.get_object()
        ticket = review.ticket
        form = ReviewForm(instance=review)
        return render(request, self.template_name, {
                'ticket': ticket,
                'form': form,
            })

    def post(self, request, id):
        """Update the review with form data."""
        review = self.get_object()
        ticket = review.ticket
        form = ReviewForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            form.save()
            return redirect('reviews:user-posts')
        return render(request, self.template_name, {
                'ticket': ticket,
                'form': form,
            })


class DeletePageView(LoginRequiredMixin, UserPassesTestMixin, View):
    """Display and process deletion of a ticket or review."""

    template_name = 'reviews/delete_confirm.html'
    login_url = 'authentication:login'
    model = None

    def get_object(self):
        """Return the object to delete."""
        return get_object_or_404(self.model, id=self.kwargs['id'])

    def test_func(self):
        """Return True if current user is the owner of the object."""
        item = self.get_object()
        return item.user == self.request.user

    def get(self, request, id):
        """Display the deletion confirmation page."""
        item = self.get_object()
        item.object_type = item._meta.model_name
        return render(request, self.template_name, {'item': item})

    def post(self, request, id):
        """Delete the object and redirect to user's posts."""
        item = self.get_object()
        item.delete()
        return redirect('reviews:user-posts')
