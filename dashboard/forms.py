from django import forms
from enquiries.models import Quotation, Enquiry, EnquiryStatus


class QuotationCreateForm(forms.ModelForm):
    class Meta:
        model = Quotation
        fields = ['total_amount', 'currency', 'incoterm', 'payment_terms', 'valid_until', 'sales_rep_notes']
        widgets = {
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Total quote value (e.g. 1250000.00)'}),
            'currency': forms.Select(choices=[('USD', 'USD — US Dollars ($)'), ('EUR', 'EUR — Euros (€)'), ('AED', 'AED — UAE Dirhams'), ('GBP', 'GBP — British Pounds (£)')], attrs={'class': 'form-select'}),
            'incoterm': forms.Select(choices=[('CIF', 'CIF — Cost, Insurance & Freight'), ('FOB', 'FOB — Free On Board'), ('DDP', 'DDP — Delivered Duty Paid'), ('CFR', 'CFR — Cost & Freight'), ('EXW', 'EXW — Ex Works')], attrs={'class': 'form-select'}),
            'payment_terms': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 30% T/T Advance, 70% against Bill of Lading (B/L)'}),
            'valid_until': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'sales_rep_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Commercial terms, container loading schedule, warranty inclusions, or payment milestone schedule...'}),
        }


class EnquiryStatusUpdateForm(forms.Form):
    status = forms.ChoiceField(
        choices=EnquiryStatus.choices,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Add engineering note or stage transition explanation...'})
    )


class BuyerQuoteResponseForm(forms.Form):
    ACTION_CHOICES = [
        ('accept', 'Accept Quotation & Confirm Order'),
        ('negotiate', 'Request Commercial Revision / Counter-Offer'),
        ('decline', 'Decline Quotation & Close'),
    ]
    action = forms.ChoiceField(choices=ACTION_CHOICES, widget=forms.RadioSelect)
    feedback_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter revision requests, counter-pricing, or comments for the sales engineer...'})
    )
