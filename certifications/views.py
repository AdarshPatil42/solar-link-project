from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import ComplianceStandard, Certification, LabReport, StandardCategory


def index_view(request):
    """
    Public compliance standards repository, notified certificates, and laboratory test reports.
    """
    standards = ComplianceStandard.objects.filter(is_active=True).prefetch_related('certifications__products')
    
    # Category filter
    cat_filter = request.GET.get('category', '').strip()
    if cat_filter:
        standards = standards.filter(category=cat_filter)

    # Search filter
    q = request.GET.get('q', '').strip()
    if q:
        standards = standards.filter(
            Q(name__icontains=q) |
            Q(issuing_body__icontains=q) |
            Q(description__icontains=q)
        )

    certifications = Certification.objects.filter(is_valid=True).select_related('standard').prefetch_related('products')
    lab_reports = LabReport.objects.select_related('product').order_by('-test_date')

    context = {
        'standards': standards,
        'certifications': certifications,
        'lab_reports': lab_reports,
        'categories': StandardCategory.choices,
        'selected_category': cat_filter,
        'q': q,
    }
    return render(request, 'certifications/index.html', context)
