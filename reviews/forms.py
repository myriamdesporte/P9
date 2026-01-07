from django import forms
from .models import Ticket, Review


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['headline', 'rating', 'body']
        widgets = {
            'body': forms.Textarea(attrs={'rows': 4}),
            'rating': forms.RadioSelect(
                choices=[(i, str(i)) for i in range(6)]
            ),
        }
