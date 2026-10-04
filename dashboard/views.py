from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.decorators import buyer_required, sales_required, admin_required

@login_required
def index_view(request):
    """Fallback index that delegates based on role."""
    from accounts.views import dashboard_redirect_view
    return dashboard_redirect_view(request)

@buyer_required
def buyer_dashboard_view(request):
    return render(request, 'dashboard/buyer.html', {'profile': request.user.profile})

@sales_required
def sales_dashboard_view(request):
    return render(request, 'dashboard/sales.html', {'profile': request.user.profile})

@admin_required
def admin_dashboard_view(request):
    return render(request, 'dashboard/admin.html', {'profile': request.user.profile})
