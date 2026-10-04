from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Count
from accounts.decorators import buyer_required, sales_required, admin_required
from accounts.models import SavedProduct, UserRole
from enquiries.models import Enquiry, EnquiryItem, EnquiryStatusHistory, EnquiryStatus, Quotation, QuotationItem
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
# ADMIN PLACEHOLDER (Prepared for Phase 5)
# ==========================================
@admin_required
def admin_dashboard_view(request):
    return render(request, 'dashboard/admin.html', {'profile': request.user.profile})
