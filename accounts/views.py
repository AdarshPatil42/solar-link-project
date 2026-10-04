from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm, CustomAuthenticationForm, UserProfileUpdateForm
from .models import UserRole


def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard_redirect')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to SolarLink, {user.first_name or user.username}! Your account has been registered successfully.")
            return redirect('accounts:dashboard_redirect')
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        form = RegisterForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard_redirect')

    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('accounts:dashboard_redirect')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = CustomAuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out securely.")
    return redirect('pages:home')


@login_required
def profile_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('accounts:profile')
    else:
        form = UserProfileUpdateForm(instance=profile, user=request.user)

    return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})


@login_required
def dashboard_redirect_view(request):
    """
    Directs the user to their appropriate role portal:
    - Admin -> /dashboard/admin/ or Django /admin/
    - Sales -> /sales/dashboard/
    - Buyer -> /dashboard/
    """
    profile = getattr(request.user, 'profile', None)
    if not profile:
        return redirect('pages:home')
    
    if profile.is_admin or request.user.is_superuser:
        return redirect('dashboard:admin_dashboard')
    elif profile.is_sales:
        return redirect('sales:dashboard')
    else:
        return redirect('dashboard:buyer_dashboard')
