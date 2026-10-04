from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Enquiry, EnquiryItem, EnquiryStatusHistory, EnquiryStatus, ProjectType
from .forms import ProjectEnquiryForm, BulkQuoteForm, EnquiryTrackForm
from catalog.models import Product
from accounts.models import UserRole


def landing_view(request):
    """
    Enquiry & quotation landing portal: Project RFQ, Bulk Schedule, or Tracking.
    """
    return render(request, 'enquiry/landing.html')


def project_enquiry_view(request):
    """
    Project-specific commercial enquiry form with optional product selection,
    destination port, Incoterms, and technical attachment upload.
    """
    preselected_product = None
    product_id = request.GET.get('product')
    if product_id:
        preselected_product = Product.objects.filter(id=product_id, is_active=True).first()

    if request.method == 'POST':
        form = ProjectEnquiryForm(request.POST, request.FILES)
        if form.is_valid():
            enquiry = form.save(commit=False)
            
            # Attach user if authenticated
            if request.user.is_authenticated:
                enquiry.buyer = request.user

            # Auto-assign initial sales executive if available
            sales_rep = User.objects.filter(profile__role=UserRole.SALES).first()
            if sales_rep:
                enquiry.assigned_sales_rep = sales_rep
                enquiry.status = EnquiryStatus.ASSIGNED

            enquiry.save()

            # Save linked product if provided
            product = form.cleaned_data.get('product')
            quantity = form.cleaned_data.get('quantity') or 1
            if product:
                EnquiryItem.objects.create(
                    enquiry=enquiry,
                    product=product,
                    quantity=quantity,
                    notes=f"Initial request for {product.name}"
                )

            # Audit Trail
            EnquiryStatusHistory.objects.create(
                enquiry=enquiry,
                from_status='SUBMITTED',
                to_status=enquiry.status,
                changed_by=request.user if request.user.is_authenticated else None,
                comment=f"New project enquiry submitted: {enquiry.project_name} ({enquiry.required_capacity})"
            )

            messages.success(
                request,
                f"Enquiry successfully registered! Your tracking number is {enquiry.enquiry_number}. A dedicated sales engineer has been assigned."
            )
            return redirect(f"/enquiry/status/?enquiry_number={enquiry.enquiry_number}")
        else:
            messages.error(request, "Please correct the form errors below.")
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data.update({
                'full_name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
                'company_name': getattr(request.user.profile, 'company_name', ''),
                'phone': getattr(request.user.profile, 'phone', ''),
                'country': getattr(request.user.profile, 'country', ''),
            })
        
        if preselected_product:
            initial_data['product'] = preselected_product
            initial_data['project_name'] = f"Supply of {preselected_product.name}"

        country_param = request.GET.get('country')
        if country_param:
            initial_data['country'] = country_param
            initial_data['shipping_destination'] = f"Port in {country_param}"

        subject_param = request.GET.get('subject')
        if subject_param:
            initial_data['message'] = f"Re: {subject_param}\n"

        form = ProjectEnquiryForm(initial=initial_data)

    context = {
        'form': form,
        'preselected_product': preselected_product,
    }
    return render(request, 'enquiry/project.html', context)


def bulk_quote_view(request):
    """
    Structured bulk multi-item quotation request form.
    """
    if request.method == 'POST':
        form = BulkQuoteForm(request.POST, request.FILES)
        if form.is_valid():
            # Build unified enquiry record
            enquiry = Enquiry(
                buyer=request.user if request.user.is_authenticated else None,
                full_name=form.cleaned_data['full_name'],
                company_name=form.cleaned_data['company_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                country=form.cleaned_data['country'],
                project_name=f"Bulk Container Procurement ({form.cleaned_data['company_name']})",
                project_type=ProjectType.DISTRIBUTION,
                required_capacity="Multi-Item Schedule",
                project_location=form.cleaned_data['shipping_destination'],
                shipping_destination=form.cleaned_data['shipping_destination'],
                preferred_incoterm=form.cleaned_data['preferred_incoterm'],
                expected_delivery_date=form.cleaned_data.get('target_delivery_date'),
                message=form.cleaned_data['items_specification'],
                attachment=form.cleaned_data.get('attachment'),
                status=EnquiryStatus.REQUESTED
            )

            sales_rep = User.objects.filter(profile__role=UserRole.SALES).first()
            if sales_rep:
                enquiry.assigned_sales_rep = sales_rep
                enquiry.status = EnquiryStatus.ASSIGNED

            enquiry.save()

            EnquiryStatusHistory.objects.create(
                enquiry=enquiry,
                from_status='SUBMITTED',
                to_status=enquiry.status,
                changed_by=request.user if request.user.is_authenticated else None,
                comment="Bulk quotation schedule submitted via web form."
            )

            messages.success(
                request,
                f"Bulk quotation schedule received! Your enquiry reference is {enquiry.enquiry_number}."
            )
            return redirect(f"/enquiry/status/?enquiry_number={enquiry.enquiry_number}")
        else:
            messages.error(request, "Please review the errors in the bulk quotation form.")
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data.update({
                'full_name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
                'company_name': getattr(request.user.profile, 'company_name', ''),
                'phone': getattr(request.user.profile, 'phone', ''),
                'country': getattr(request.user.profile, 'country', ''),
            })
        form = BulkQuoteForm(initial=initial_data)

    return render(request, 'enquiry/bulk_quote.html', {'form': form})


def status_tracking_view(request):
    """
    Public tracking portal: lookup an enquiry by ENQ-YYYY-XXXXX and display
    interactive step-by-step progress timeline, line items, and audit log.
    """
    enquiry = None
    query_number = request.GET.get('enquiry_number', '').strip().upper()

    if request.method == 'POST':
        track_form = EnquiryTrackForm(request.POST)
        if track_form.is_valid():
            query_number = track_form.cleaned_data['enquiry_number'].strip().upper()
    else:
        track_form = EnquiryTrackForm(initial={'enquiry_number': query_number})

    if query_number:
        enquiry = Enquiry.objects.filter(enquiry_number__iexact=query_number).select_related('assigned_sales_rep', 'buyer').prefetch_related('items__product', 'status_history').first()
        if not enquiry:
            messages.warning(request, f"No enquiry found matching reference '{query_number}'. Please check the format (e.g. ENQ-2026-00125).")

    context = {
        'track_form': track_form,
        'enquiry': enquiry,
        'query_number': query_number,
    }
    return render(request, 'enquiry/status.html', context)
