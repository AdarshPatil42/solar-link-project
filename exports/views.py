from django.shortcuts import render
from .models import Country, ShippingTerm, ExportDocument


def info_view(request):
    """
    Export terms, Incoterms reference, international destinations, and required documentation checklists.
    """
    shipping_terms = ShippingTerm.objects.all().order_by('sort_order')
    
    # Destination countries with region filtering
    region = request.GET.get('region', '').strip()
    countries = Country.objects.filter(is_active=True).order_by('sort_order', 'name')
    if region:
        countries = countries.filter(region__icontains=region)

    export_docs = ExportDocument.objects.all().order_by('sort_order')

    # Distinct regions for filtering
    regions = Country.objects.filter(is_active=True).values_list('region', flat=True).distinct().order_by('region')

    context = {
        'shipping_terms': shipping_terms,
        'countries': countries,
        'export_docs': export_docs,
        'regions': regions,
        'selected_region': region,
    }
    return render(request, 'export/info.html', context)
