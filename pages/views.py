from django.shortcuts import render, redirect
from django.contrib import messages
from .models import TeamMember, FAQ, FAQCategory, TeamDepartment
from .forms import ContactForm
from catalog.models import Category, Product
from exports.models import Country


def home_view(request):
    """
    High-converting homepage featuring the hero banner, technology categories,
    featured products, export countries reach, and direct RFQ call-to-actions.
    """
    categories = Category.objects.filter(is_active=True).order_by('sort_order')
    featured_products = Product.objects.filter(is_featured=True, is_active=True).select_related('category').prefetch_related('specifications__attribute')[:6]
    export_countries = Country.objects.filter(is_active=True).order_by('sort_order')[:8]
    team_preview = TeamMember.objects.filter(is_active=True).order_by('order')[:3]

    context = {
        'categories': categories,
        'featured_products': featured_products,
        'export_countries': export_countries,
        'team_preview': team_preview,
        'stats': {
            'megawatts_exported': '520+ MW',
            'countries_served': '18+ Nations',
            'quality_standard': '100% IEC Tested',
            'rfq_turnaround': '24-48 Hours',
        }
    }
    return render(request, 'home/index.html', context)


def about_view(request):
    """
    Company background, renewable energy expertise, export credentials,
    the 7-step 'How It Works' workflow, and executive team showcase.
    """
    team_members = TeamMember.objects.filter(is_active=True).order_by('order')
    departments = TeamDepartment.choices

    context = {
        'team_members': team_members,
        'departments': departments,
    }
    return render(request, 'about/about.html', context)


def contact_view(request):
    """
    International sales desk contact form, direct WhatsApp integration,
    business hours, and interactive categorized FAQ accordion.
    """
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_msg = form.save()
            messages.success(
                request,
                f"Thank you, {contact_msg.full_name}! Your message has been received by our international trade desk. A sales engineer will respond shortly."
            )
            return redirect('pages:contact')
        else:
            messages.error(request, "Please correct the errors in the form below.")
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {
                'full_name': request.user.get_full_name() or request.user.username,
                'email': request.user.email,
                'company': getattr(request.user.profile, 'company_name', ''),
                'phone': getattr(request.user.profile, 'phone', ''),
            }
        # Prefill subject if query param passed (e.g. ?subject=Certificate+Verification)
        subject_param = request.GET.get('subject')
        if subject_param:
            initial_data['subject'] = subject_param

        form = ContactForm(initial=initial_data)

    faqs = FAQ.objects.filter(is_published=True).order_by('order')
    faq_categories = FAQCategory.choices

    context = {
        'form': form,
        'faqs': faqs,
        'faq_categories': faq_categories,
    }
    return render(request, 'contact/contact.html', context)
