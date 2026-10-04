import csv
from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from accounts.decorators import buyer_required, sales_required, admin_required
from accounts.models import UserProfile, UserRole, SavedProduct
from catalog.models import Product, Category
from certifications.models import Certification
from enquiries.models import Enquiry, EnquiryItem, EnquiryStatusHistory, EnquiryStatus, ProjectType, Quotation, QuotationItem
from .forms import QuotationCreateForm, EnquiryStatusUpdateForm, BuyerQuoteResponseForm


# ==========================================
# DISPATCHER
# ==========================================
@login_required
def index_view(request):
    """Fallback index that delegates based on user role."""
    from accounts.views import dashboard_redirect_view
    return dashboard_redirect_view(request)


# ==========================================
# BUYER PORTAL VIEWS
# ==========================================
@buyer_required
def buyer_dashboard_view(request):
    """
    Overview workspace for international buyers:
    Key metrics, recent enquiries, latest quotations, and saved wishlist items.
    """
    user_enquiries = Enquiry.objects.filter(buyer=request.user)
    total_enquiries = user_enquiries.count()
    active_enquiries = user_enquiries.exclude(status__in=[EnquiryStatus.APPROVED, EnquiryStatus.REJECTED, EnquiryStatus.CLOSED]).count()
    
    received_quotations = Quotation.objects.filter(enquiry__buyer=request.user)
    total_quotations = received_quotations.count()
    pending_quotes = received_quotations.filter(status=Quotation.QuotationStatus.SENT).count()

    saved_products = SavedProduct.objects.filter(user=request.user).select_related('product__category')
    total_saved = saved_products.count()

    recent_enquiries = user_enquiries.order_by('-created_at')[:5]
    latest_quotations = received_quotations.order_by('-created_at')[:4]

    context = {
        'profile': request.user.profile,
        'total_enquiries': total_enquiries,
        'active_enquiries': active_enquiries,
        'total_quotations': total_quotations,
        'pending_quotes': pending_quotes,
        'total_saved': total_saved,
        'recent_enquiries': recent_enquiries,
        'latest_quotations': latest_quotations,
        'saved_products_preview': saved_products[:4],
    }
    return render(request, 'dashboard/buyer/index.html', context)


@buyer_required
def buyer_saved_products_view(request):
    """
    Full wishlist of saved equipment with 1-click RFQ creation.
    """
    saved_items = SavedProduct.objects.filter(user=request.user).select_related('product__category').prefetch_related('product__specifications__attribute')
    return render(request, 'dashboard/buyer/saved_products.html', {'saved_items': saved_items})


@buyer_required
def buyer_enquiries_list_view(request):
    """
    List of all project enquiries submitted by this buyer with status filtering.
    """
    enquiries = Enquiry.objects.filter(buyer=request.user).prefetch_related('items__product')
    
    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        enquiries = enquiries.filter(status=status_filter)

    q = request.GET.get('q', '').strip()
    if q:
        enquiries = enquiries.filter(
            Q(enquiry_number__icontains=q) |
            Q(project_name__icontains=q) |
            Q(shipping_destination__icontains=q)
        )

    context = {
        'enquiries': enquiries,
        'status_choices': EnquiryStatus.choices,
        'selected_status': status_filter,
        'q': q,
    }
    return render(request, 'dashboard/buyer/enquiries_list.html', context)


@buyer_required
def buyer_enquiry_detail_view(request, pk):
    """
    Buyer view of specific enquiry with 7-step timeline and line items.
    """
    enquiry = get_object_or_404(
        Enquiry.objects.select_related('assigned_sales_rep').prefetch_related('items__product', 'status_history', 'quotations'),
        id=pk
    )
    if not request.user.is_superuser and enquiry.buyer != request.user:
        messages.error(request, "You do not have permission to view that enquiry.")
        return redirect('dashboard:buyer_dashboard')

    return render(request, 'dashboard/buyer/enquiry_detail.html', {'enquiry': enquiry})


@buyer_required
def buyer_quotations_list_view(request):
    """
    List of formal commercial quotations received by the buyer.
    """
    quotations = Quotation.objects.filter(enquiry__buyer=request.user).select_related('enquiry', 'sales_rep').prefetch_related('items')
    return render(request, 'dashboard/buyer/quotations_list.html', {'quotations': quotations})


@buyer_required
def buyer_quotation_detail_view(request, pk):
    """
    Detailed commercial quotation review with interactive Accept, Negotiate, or Decline actions.
    """
    quotation = get_object_or_404(
        Quotation.objects.select_related('enquiry', 'sales_rep').prefetch_related('items__product'),
        id=pk
    )
    if not request.user.is_superuser and quotation.enquiry.buyer != request.user:
        messages.error(request, "You do not have permission to access that quotation.")
        return redirect('dashboard:buyer_dashboard')

    if request.method == 'POST':
        form = BuyerQuoteResponseForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            feedback = form.cleaned_data['feedback_notes']
            quotation.buyer_feedback = feedback

            if action == 'accept':
                quotation.status = Quotation.QuotationStatus.ACCEPTED
                quotation.enquiry.status = EnquiryStatus.APPROVED
                msg = f"Quotation {quotation.quote_number} ACCEPTED! Order confirmed. Our trade desk will issue final bilateral sales contracts."
            elif action == 'negotiate':
                quotation.status = Quotation.QuotationStatus.NEGOTIATING
                quotation.enquiry.status = EnquiryStatus.NEGOTIATION
                msg = f"Commercial revision request sent for {quotation.quote_number}. Your sales representative will review your adjustments."
            elif action == 'decline':
                quotation.status = Quotation.QuotationStatus.DECLINED
                quotation.enquiry.status = EnquiryStatus.REJECTED
                msg = f"Quotation {quotation.quote_number} was declined."

            quotation.save()
            quotation.enquiry.save()

            # Record in audit log
            EnquiryStatusHistory.objects.create(
                enquiry=quotation.enquiry,
                from_status=EnquiryStatus.QUOTATION_SENT,
                to_status=quotation.enquiry.status,
                changed_by=request.user,
                comment=f"Buyer response on {quotation.quote_number} ({action.upper()}): {feedback or 'No comment provided'}"
            )

            messages.success(request, msg)
            return redirect('dashboard:buyer_quotation_detail', pk=quotation.id)
    else:
        form = BuyerQuoteResponseForm()

    context = {
        'quotation': quotation,
        'enquiry': quotation.enquiry,
        'items': quotation.items.all(),
        'form': form,
    }
    return render(request, 'dashboard/buyer/quotation_detail.html', context)


# ==========================================
# SALES EXECUTIVE WORKSPACE VIEWS
# ==========================================
@sales_required
def sales_dashboard_view(request):
    """
    Sales Executive command center: assigned leads, deals in negotiation,
    pending quotations, won orders, and conversion rate.
    """
    is_admin_user = request.user.is_superuser or getattr(request.user.profile, 'is_admin', False)

    if is_admin_user:
        assigned_enquiries = Enquiry.objects.all()
        quotes = Quotation.objects.all()
    else:
        assigned_enquiries = Enquiry.objects.filter(assigned_sales_rep=request.user)
        quotes = Quotation.objects.filter(sales_rep=request.user)

    total_leads = assigned_enquiries.count()
    pending_review = assigned_enquiries.filter(status__in=[EnquiryStatus.REQUESTED, EnquiryStatus.ASSIGNED, EnquiryStatus.UNDER_REVIEW]).count()
    quotes_prepared = assigned_enquiries.filter(status__in=[EnquiryStatus.QUOTATION_PREPARED, EnquiryStatus.QUOTATION_SENT]).count()
    negotiations = assigned_enquiries.filter(status=EnquiryStatus.NEGOTIATION).count()
    won_deals = assigned_enquiries.filter(status=EnquiryStatus.APPROVED).count()

    conversion_rate = f"{(won_deals / total_leads * 100):.1f}%" if total_leads > 0 else "0%"

    urgent_leads = assigned_enquiries.filter(
        status__in=[EnquiryStatus.REQUESTED, EnquiryStatus.ASSIGNED, EnquiryStatus.UNDER_REVIEW]
    ).order_by('-created_at')[:6]

    recent_quotes = quotes.select_related('enquiry').order_by('-created_at')[:5]

    context = {
        'profile': request.user.profile,
        'total_leads': total_leads,
        'pending_review': pending_review,
        'quotes_prepared': quotes_prepared,
        'negotiations': negotiations,
        'won_deals': won_deals,
        'conversion_rate': conversion_rate,
        'urgent_leads': urgent_leads,
        'recent_quotes': recent_quotes,
    }
    return render(request, 'dashboard/sales/index.html', context)


@sales_required
def sales_enquiries_list_view(request):
    """
    List of assigned leads with search, filter by status, and quick inspection.
    """
    is_admin_user = request.user.is_superuser or getattr(request.user.profile, 'is_admin', False)
    if is_admin_user:
        leads = Enquiry.objects.all().select_related('buyer', 'assigned_sales_rep').prefetch_related('items__product')
    else:
        leads = Enquiry.objects.filter(assigned_sales_rep=request.user).select_related('buyer').prefetch_related('items__product')

    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        leads = leads.filter(status=status_filter)

    q = request.GET.get('q', '').strip()
    if q:
        leads = leads.filter(
            Q(enquiry_number__icontains=q) |
            Q(project_name__icontains=q) |
            Q(company_name__icontains=q) |
            Q(full_name__icontains=q) |
            Q(country__icontains=q)
        )

    context = {
        'leads': leads,
        'status_choices': EnquiryStatus.choices,
        'selected_status': status_filter,
        'q': q,
    }
    return render(request, 'dashboard/sales/enquiries_list.html', context)


@sales_required
def sales_enquiry_detail_view(request, pk):
    """
    Lead workspace: examine technical requirements, update deal stage,
    log engineering comments, and jump to Quotation Builder.
    """
    is_admin_user = request.user.is_superuser or getattr(request.user.profile, 'is_admin', False)
    enquiry = get_object_or_404(
        Enquiry.objects.select_related('buyer', 'assigned_sales_rep').prefetch_related('items__product', 'status_history', 'quotations'),
        id=pk
    )

    if not is_admin_user and enquiry.assigned_sales_rep != request.user:
        messages.error(request, "This lead is assigned to another sales executive.")
        return redirect('sales:dashboard')

    if request.method == 'POST' and 'update_status' in request.POST:
        status_form = EnquiryStatusUpdateForm(request.POST)
        if status_form.is_valid():
            old_status = enquiry.status
            new_status = status_form.cleaned_data['status']
            comment = status_form.cleaned_data['comment']

            enquiry.status = new_status
            enquiry.save()

            EnquiryStatusHistory.objects.create(
                enquiry=enquiry,
                from_status=old_status,
                to_status=new_status,
                changed_by=request.user,
                comment=comment or f"Stage updated by {request.user.get_full_name() or request.user.username}"
            )

            messages.success(request, f"Lead stage updated to '{enquiry.get_status_display()}'.")
            return redirect('sales:enquiry_detail', pk=enquiry.id)
    else:
        status_form = EnquiryStatusUpdateForm(initial={'status': enquiry.status})

    existing_quotation = enquiry.quotations.first()

    context = {
        'enquiry': enquiry,
        'status_form': status_form,
        'existing_quotation': existing_quotation,
    }
    return render(request, 'dashboard/sales/enquiry_detail.html', context)


@sales_required
def sales_create_quote_view(request, pk):
    """
    Dynamic Quotation Builder: Sales executive inputs price, payment terms,
    Incoterm, and valid expiry date. Automatically creates Quotation and QuotationItems.
    """
    is_admin_user = request.user.is_superuser or getattr(request.user.profile, 'is_admin', False)
    enquiry = get_object_or_404(Enquiry.objects.prefetch_related('items__product'), id=pk)

    if not is_admin_user and enquiry.assigned_sales_rep != request.user:
        messages.error(request, "You can only generate quotations for your assigned leads.")
        return redirect('sales:dashboard')

    if request.method == 'POST':
        form = QuotationCreateForm(request.POST)
        if form.is_valid():
            quotation = form.save(commit=False)
            quotation.enquiry = enquiry
            quotation.sales_rep = request.user
            quotation.status = Quotation.QuotationStatus.SENT
            quotation.save()

            # Create quotation items from enquiry items
            for item in enquiry.items.all():
                unit_price = item.target_price_usd or 0.00
                if unit_price == 0 and quotation.total_amount > 0 and item.quantity > 0:
                    unit_price = round(quotation.total_amount / item.quantity, 2)

                QuotationItem.objects.create(
                    quotation=quotation,
                    product=item.product,
                    quantity=item.quantity,
                    unit_price=unit_price,
                    subtotal=unit_price * item.quantity,
                    specifications_summary=f"{item.product.brand} - {item.product.display_power or ''}"
                )

            # Update Enquiry Status
            old_status = enquiry.status
            enquiry.status = EnquiryStatus.QUOTATION_SENT
            enquiry.save()

            # Audit History
            EnquiryStatusHistory.objects.create(
                enquiry=enquiry,
                from_status=old_status,
                to_status=EnquiryStatus.QUOTATION_SENT,
                changed_by=request.user,
                comment=f"Official Quotation {quotation.quote_number} ({quotation.currency} {quotation.total_amount:,.2f} {quotation.incoterm}) dispatched to buyer."
            )

            messages.success(request, f"Official Quotation {quotation.quote_number} generated and delivered to buyer!")
            return redirect('sales:quotation_detail', pk=quotation.id)
    else:
        # Pre-fill initial form values based on enquiry
        initial_data = {
            'incoterm': enquiry.preferred_incoterm or 'CIF',
            'valid_until': date.today() + timedelta(days=30),
            'payment_terms': '30% T/T Advance on Order Confirmation, 70% against Bill of Lading (B/L)',
            'sales_rep_notes': f"Commercial offer for {enquiry.project_name} delivered to {enquiry.shipping_destination}.",
        }
        form = QuotationCreateForm(initial=initial_data)

    context = {
        'form': form,
        'enquiry': enquiry,
    }
    return render(request, 'dashboard/sales/create_quotation.html', context)


@sales_required
def sales_quotations_list_view(request):
    """
    List of all quotations issued by this sales rep.
    """
    is_admin_user = request.user.is_superuser or getattr(request.user.profile, 'is_admin', False)
    if is_admin_user:
        quotes = Quotation.objects.all().select_related('enquiry', 'sales_rep')
    else:
        quotes = Quotation.objects.filter(sales_rep=request.user).select_related('enquiry')

    return render(request, 'dashboard/sales/quotations_list.html', {'quotes': quotes})


@sales_required
def sales_quotation_detail_view(request, pk):
    """
    Sales view of a generated quotation with itemized breakdown and buyer feedback.
    """
    is_admin_user = request.user.is_superuser or getattr(request.user.profile, 'is_admin', False)
    quotation = get_object_or_404(
        Quotation.objects.select_related('enquiry__buyer', 'sales_rep').prefetch_related('items__product'),
        id=pk
    )

    if not is_admin_user and quotation.sales_rep != request.user:
        messages.error(request, "Permission denied.")
        return redirect('sales:dashboard')

    return render(request, 'dashboard/sales/quotation_detail.html', {'quotation': quotation, 'enquiry': quotation.enquiry})


@sales_required
def sales_pipeline_board_view(request):
    """
    Visual Kanban Deal Pipeline:
    Categorizes all active enquiries into columns:
    [REQUESTED / NEW] -> [ASSIGNED] -> [UNDER_REVIEW] -> [QUOTATION_PREPARED] -> [QUOTATION_SENT] -> [NEGOTIATION] -> [WON / APPROVED]
    """
    is_admin_user = request.user.is_superuser or getattr(request.user.profile, 'is_admin', False)
    if is_admin_user:
        all_leads = Enquiry.objects.all().select_related('assigned_sales_rep').prefetch_related('items')
    else:
        all_leads = Enquiry.objects.filter(assigned_sales_rep=request.user).prefetch_related('items')

    pipeline_stages = [
        ('NEW / REQUESTED', EnquiryStatus.REQUESTED, all_leads.filter(status=EnquiryStatus.REQUESTED)),
        ('ASSIGNED', EnquiryStatus.ASSIGNED, all_leads.filter(status=EnquiryStatus.ASSIGNED)),
        ('UNDER REVIEW', EnquiryStatus.UNDER_REVIEW, all_leads.filter(status=EnquiryStatus.UNDER_REVIEW)),
        ('QUOTE PREPARED', EnquiryStatus.QUOTATION_PREPARED, all_leads.filter(status=EnquiryStatus.QUOTATION_PREPARED)),
        ('QUOTE SENT', EnquiryStatus.QUOTATION_SENT, all_leads.filter(status=EnquiryStatus.QUOTATION_SENT)),
        ('NEGOTIATION', EnquiryStatus.NEGOTIATION, all_leads.filter(status=EnquiryStatus.NEGOTIATION)),
        ('WON / APPROVED', EnquiryStatus.APPROVED, all_leads.filter(status=EnquiryStatus.APPROVED)),
    ]

    context = {
        'pipeline_stages': pipeline_stages,
        'total_deals': all_leads.count(),
    }
    return render(request, 'dashboard/sales/pipeline.html', context)


# ==========================================
# PHASE 5: ADMIN CONTROL CENTER & ANALYTICS
# ==========================================
@admin_required
def admin_dashboard_view(request):
    """
    Executive Admin Operations Hub & Analytics Command:
    High-level platform KPIs, catalog distributions, RFQ application breakdown,
    pipeline deal conversion metrics, and 5x CSV export actions.
    """
    # 1. Executive Topline Metrics
    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    total_certifications = Certification.objects.count()
    total_buyers = UserProfile.objects.filter(role=UserRole.BUYER).count()
    total_sales_reps = UserProfile.objects.filter(role=UserRole.SALES).count()
    
    total_enquiries = Enquiry.objects.count()
    won_enquiries = Enquiry.objects.filter(status=EnquiryStatus.APPROVED).count()
    in_negotiation = Enquiry.objects.filter(status=EnquiryStatus.NEGOTIATION).count()
    under_review = Enquiry.objects.filter(status__in=[EnquiryStatus.REQUESTED, EnquiryStatus.ASSIGNED, EnquiryStatus.UNDER_REVIEW]).count()
    
    total_quotes = Quotation.objects.count()
    quote_aggregates = Quotation.objects.aggregate(total_val=Sum('total_amount'))
    total_quote_value = quote_aggregates['total_val'] or 0.00
    
    won_aggregates = Quotation.objects.filter(status=Quotation.QuotationStatus.ACCEPTED).aggregate(won_val=Sum('total_amount'))
    won_quote_value = won_aggregates['won_val'] or 0.00
    
    conversion_rate = f"{(won_enquiries / total_enquiries * 100):.1f}%" if total_enquiries > 0 else "0.0%"

    # 2. Analytics Distributions
    # A. Enquiries by Project Type
    project_types_data = []
    for code, label in ProjectType.choices:
        cnt = Enquiry.objects.filter(project_type=code).count()
        pct = round((cnt / total_enquiries * 100), 1) if total_enquiries > 0 else 0
        project_types_data.append({'code': code, 'label': label, 'count': cnt, 'percentage': pct})
    project_types_data.sort(key=lambda x: x['count'], reverse=True)

    # B. Products by Category
    categories_data = []
    for cat in Category.objects.annotate(p_count=Count('products')):
        pct = round((cat.p_count / total_products * 100), 1) if total_products > 0 else 0
        categories_data.append({'name': cat.name, 'count': cat.p_count, 'percentage': pct})
    categories_data.sort(key=lambda x: x['count'], reverse=True)

    # C. Pipeline Deal Stages Breakdown
    stages_data = []
    for code, label in EnquiryStatus.choices:
        cnt = Enquiry.objects.filter(status=code).count()
        stages_data.append({'code': code, 'label': label, 'count': cnt})

    # D. Top Destination Export Markets
    top_destinations = Enquiry.objects.values('country').annotate(count=Count('id')).order_by('-count')[:5]

    # 3. Recent Activity Lists
    recent_enquiries = Enquiry.objects.select_related('buyer', 'assigned_sales_rep').order_by('-created_at')[:5]
    recent_quotations = Quotation.objects.select_related('enquiry', 'sales_rep').order_by('-created_at')[:5]
    recent_buyers = User.objects.filter(profile__role=UserRole.BUYER).select_related('profile').order_by('-date_joined')[:5]

    context = {
        'profile': request.user.profile,
        'total_products': total_products,
        'total_categories': total_categories,
        'total_certifications': total_certifications,
        'total_buyers': total_buyers,
        'total_sales_reps': total_sales_reps,
        'total_enquiries': total_enquiries,
        'won_enquiries': won_enquiries,
        'in_negotiation': in_negotiation,
        'under_review': under_review,
        'total_quotes': total_quotes,
        'total_quote_value': total_quote_value,
        'won_quote_value': won_quote_value,
        'conversion_rate': conversion_rate,
        'project_types_data': project_types_data,
        'categories_data': categories_data,
        'stages_data': stages_data,
        'top_destinations': top_destinations,
        'recent_enquiries': recent_enquiries,
        'recent_quotations': recent_quotations,
        'recent_buyers': recent_buyers,
    }
    return render(request, 'dashboard/admin.html', context)


# ==========================================
# 5X CSV DATA EXPORT ENGINES
# ==========================================
@admin_required
def export_products_csv(request):
    """
    Exports full equipment catalog with technical attributes and specifications.
    """
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="SolarLink_Products_Export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Product Code', 'Product Name', 'Category', 'Brand',
        'Power Rating', 'Model Number', 'Short Description',
        'Warranty Terms', 'Created Date'
    ])
    
    products = Product.objects.select_related('category', 'warranty').all().order_by('category__name', 'name')
    for p in products:
        warranty_str = f"{p.warranty.warranty_years} Years ({p.warranty.warranty_type})" if hasattr(p, 'warranty') and p.warranty else "Standard Export Warranty"
        writer.writerow([
            p.product_code,
            p.name,
            p.category.name if p.category else 'General',
            p.brand,
            p.display_power or 'Certified Spec',
            p.model_number or '',
            p.short_description or '',
            warranty_str,
            p.created_at.strftime('%Y-%m-%d') if p.created_at else ''
        ])
    return response


@admin_required
def export_enquiries_csv(request):
    """
    Exports all project RFQs and equipment leads with contact and scope details.
    """
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="SolarLink_Enquiries_Export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Enquiry Ref', 'Buyer Name', 'Company Name', 'Email', 'Phone',
        'Country', 'Project Name', 'Project Type', 'Capacity',
        'Destination Port', 'Preferred Incoterm', 'Milestone Stage',
        'Assigned Sales Rep', 'Date Submitted'
    ])
    
    enquiries = Enquiry.objects.select_related('assigned_sales_rep').all().order_by('-created_at')
    for enq in enquiries:
        rep_name = enq.assigned_sales_rep.get_full_name() or enq.assigned_sales_rep.username if enq.assigned_sales_rep else 'Unassigned'
        writer.writerow([
            enq.enquiry_number,
            enq.full_name,
            enq.company_name,
            enq.email,
            enq.phone,
            enq.country,
            enq.project_name,
            enq.get_project_type_display(),
            enq.required_capacity,
            enq.shipping_destination,
            enq.preferred_incoterm,
            enq.get_status_display(),
            rep_name,
            enq.created_at.strftime('%Y-%m-%d %H:%M') if enq.created_at else ''
        ])
    return response


@admin_required
def export_buyers_csv(request):
    """
    Exports registered international buyers dossier with RFQ submission statistics.
    """
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="SolarLink_Buyers_Export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Username', 'Full Name', 'Email', 'Company Name',
        'Country', 'Phone', 'Job Title', 'Total RFQs Submitted', 'Date Joined'
    ])
    
    buyers = User.objects.filter(profile__role=UserRole.BUYER).select_related('profile').annotate(enquiry_count=Count('enquiries')).order_by('-date_joined')
    for b in buyers:
        profile = getattr(b, 'profile', None)
        writer.writerow([
            b.username,
            b.get_full_name() or b.username,
            b.email,
            profile.company_name if profile else '',
            profile.country if profile else '',
            profile.phone if profile else '',
            profile.job_title if profile else '',
            b.enquiry_count,
            b.date_joined.strftime('%Y-%m-%d') if b.date_joined else ''
        ])
    return response


@admin_required
def export_quotations_csv(request):
    """
    Exports issued commercial proforma quotations, currency values, and buyer decision status.
    """
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="SolarLink_Quotations_Export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Quote Ref', 'Enquiry Ref', 'Project Name', 'Buyer Company',
        'Sales Executive', 'Total Amount', 'Currency', 'Incoterm',
        'Payment Terms', 'Valid Until', 'Quotation Status', 'Issued Date'
    ])
    
    quotes = Quotation.objects.select_related('enquiry', 'sales_rep').all().order_by('-created_at')
    for q in quotes:
        rep_name = q.sales_rep.get_full_name() or q.sales_rep.username if q.sales_rep else ''
        writer.writerow([
            q.quote_number,
            q.enquiry.enquiry_number if q.enquiry else '',
            q.enquiry.project_name if q.enquiry else '',
            q.enquiry.company_name if q.enquiry else '',
            rep_name,
            f"{q.total_amount:.2f}",
            q.currency,
            q.incoterm,
            q.payment_terms,
            q.valid_until.strftime('%Y-%m-%d') if q.valid_until else '',
            q.get_status_display(),
            q.created_at.strftime('%Y-%m-%d %H:%M') if q.created_at else ''
        ])
    return response


@admin_required
def export_pipeline_csv(request):
    """
    Exports active commercial deal pipeline opportunities and current negotiation stages.
    """
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="SolarLink_Sales_Pipeline_Export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Enquiry Ref', 'Project Name', 'Client Company', 'Country',
        'Destination Port', 'Project Type', 'Capacity', 'Milestone Stage',
        'Assigned Sales Rep', 'Latest Quote Ref', 'Quote Value',
        'Incoterm', 'Last Activity'
    ])
    
    deals = Enquiry.objects.select_related('assigned_sales_rep').prefetch_related('quotations').all().order_by('status', '-updated_at')
    for d in deals:
        rep_name = d.assigned_sales_rep.get_full_name() or d.assigned_sales_rep.username if d.assigned_sales_rep else 'Unassigned'
        latest_quote = d.quotations.first()
        writer.writerow([
            d.enquiry_number,
            d.project_name,
            d.company_name or d.full_name,
            d.country,
            d.shipping_destination,
            d.get_project_type_display(),
            d.required_capacity,
            d.get_status_display(),
            rep_name,
            latest_quote.quote_number if latest_quote else 'None',
            f"{latest_quote.currency} {latest_quote.total_amount:.2f}" if latest_quote else 'Pending Quote',
            latest_quote.incoterm if latest_quote else d.preferred_incoterm,
            d.updated_at.strftime('%Y-%m-%d %H:%M') if d.updated_at else ''
        ])
    return response
