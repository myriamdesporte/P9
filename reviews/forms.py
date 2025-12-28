from django import forms
from .models import Ticket


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
