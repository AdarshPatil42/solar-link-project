from django.shortcuts import render

def landing_view(request):
    return render(request, 'enquiry/landing.html')

def project_enquiry_view(request):
    return render(request, 'enquiry/project.html')

def bulk_quote_view(request):
    return render(request, 'enquiry/bulk_quote.html')

def status_tracking_view(request):
    return render(request, 'enquiry/status.html')
