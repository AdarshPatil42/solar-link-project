from django import forms
from .models import Enquiry, EnquiryItem, ProjectType
from catalog.models import Product


class ProjectEnquiryForm(forms.ModelForm):
    # Optional linked product and requested quantity
    product = forms.ModelChoiceField(
        queryset=Product.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text='Select specific equipment model (or leave blank for custom multi-component project)'
    )
    quantity = forms.IntegerField(
        initial=1,
        min_value=1,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantity / Units / Containers'})
    )

    class Meta:
        model = Enquiry
        fields = [
            'full_name', 'company_name', 'email', 'phone', 'country',
            'project_name', 'project_type', 'required_capacity',
            'project_location', 'expected_delivery_date', 'shipping_destination',
            'preferred_incoterm', 'message', 'attachment'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Tariq Al-Mansoor'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Gulf Energy Infrastructure LLC'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'procurement@company.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+971 4 800 5544'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. United Arab Emirates'}),
            'project_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 50 MW Utility PV Solar Farm Expansion'}),
            'project_type': forms.Select(attrs={'class': 'form-select'}),
            'required_capacity': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 50 MWp, 500 kW, 5x 40ft Containers'}),
            'project_location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Abu Dhabi, UAE'}),
            'expected_delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'shipping_destination': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Jebel Ali Port, Dubai'}),
            'preferred_incoterm': forms.Select(
                choices=[('CIF', 'CIF — Cost, Insurance & Freight'), ('FOB', 'FOB — Free On Board'), ('DDP', 'DDP — Delivered Duty Paid'), ('CFR', 'CFR — Cost & Freight'), ('EXW', 'EXW — Ex Works')],
                attrs={'class': 'form-select'}
            ),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Specify any required cell architectures, inverter string topologies, or tender deadlines...'}),
            'attachment': forms.FileInput(attrs={'class': 'form-control'}),
        }


class BulkQuoteForm(forms.Form):
    full_name = forms.CharField(max_length=120, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Name'}))
    company_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company / Enterprise'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'corporate@enterprise.com'}))
    phone = forms.CharField(max_length=40, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+49 30 123456'}))
    country = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country / Territory'}))
    
    shipping_destination = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Destination Seaport (e.g. Hamburg, Jebel Ali)'}))
    preferred_incoterm = forms.ChoiceField(
        choices=[('CIF', 'CIF — Cost, Insurance & Freight'), ('FOB', 'FOB — Free On Board'), ('DDP', 'DDP — Delivered Duty Paid'), ('EXW', 'EXW — Ex Works')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    target_delivery_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))

    # Items specification
    items_specification = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': (
                "List your bulk equipment schedule. Example:\n"
                "• 15,000 pcs - HeliosPro 550W Bifacial Modules (SL-PV-550BF)\n"
                "• 40 units - VoltCore 50kW String Inverters (SL-INV-50KS)\n"
                "• 10 sets - TerraMount Utility Ground-Mount Aluminum Racking"
            )
        }),
        help_text='Provide estimated unit counts, packaging constraints, or tender Bill of Quantities.'
    )
    attachment = forms.FileField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))


class EnquiryTrackForm(forms.Form):
    enquiry_number = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'ENQ-2026-00125', 'style': 'font-family: var(--font-mono); text-transform: uppercase;'})
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'buyer@company.com (Optional validation)'})
    )
