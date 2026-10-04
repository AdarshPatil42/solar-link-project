from django import forms
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['full_name', 'email', 'phone', 'company', 'subject', 'message']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'John Doe'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'john@company.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+971 50 123 4567'}),
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Solar Global Ltd'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Commercial equipment enquiry'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Please specify your required product models, container volume, or project location...'}),
        }
