from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from .models import UserRole


def role_required(allowed_roles):
    """
    Decorator for views that checks that the logged-in user has one of the allowed roles.
    Superusers always pass.
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            profile = getattr(request.user, 'profile', None)
            if profile and profile.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            
            messages.error(request, "You do not have permission to access that area.")
            return redirect('pages:home')
        return _wrapped_view
    return decorator


def buyer_required(view_func):
    return role_required([UserRole.BUYER, UserRole.ADMIN])(view_func)


def sales_required(view_func):
    return role_required([UserRole.SALES, UserRole.ADMIN])(view_func)


def admin_required(view_func):
    return role_required([UserRole.ADMIN])(view_func)
