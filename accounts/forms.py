from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import UserProfile, UserRole


class RegisterForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'placeholder': 'John'}))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'placeholder': 'Doe'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'buyer@company.com'}))
    company_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={'placeholder': 'Solar Solutions LLC'}))
    country = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'placeholder': 'United Arab Emirates'}))
    phone = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'placeholder': '+971 50 123 4567'}))
    role = forms.ChoiceField(
        choices=[(UserRole.BUYER, 'International Buyer / Project Developer'), (UserRole.SALES, 'SolarLink Sales Representative')],
        initial=UserRole.BUYER,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': '••••••••'}), min_length=8)
    password_confirm = forms.CharField(label="Confirm Password", widget=forms.PasswordInput(attrs={'placeholder': '••••••••'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'johndoe'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            profile = user.profile
            profile.company_name = self.cleaned_data.get('company_name', '')
            profile.country = self.cleaned_data.get('country', '')
            profile.phone = self.cleaned_data.get('phone', '')
            profile.role = self.cleaned_data.get('role', UserRole.BUYER)
            profile.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username or Email',
        'autofocus': True
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': '••••••••'
    }))


class UserProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=False)
    last_name = forms.CharField(max_length=50, required=False)
    email = forms.EmailField(required=True)

    class Meta:
        model = UserProfile
        fields = ['company_name', 'phone', 'country', 'job_title', 'bio', 'avatar']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'job_title': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
