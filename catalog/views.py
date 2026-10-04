from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Category, Product, ProductSpecification, SpecificationAttribute
from accounts.models import SavedProduct


def product_list_view(request):
    """
    Multi-dimensional searchable and filterable catalog listing.
    Supports search query, category, brand, power range, stock status, and sorting.
    """
    queryset = Product.objects.filter(is_active=True).select_related('category').prefetch_related('specifications__attribute')

    # 1. Search Query
    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(name__icontains=q) |
            Q(product_code__icontains=q) |
            Q(brand__icontains=q) |
            Q(technology_type__icontains=q) |
            Q(short_description__icontains=q) |
            Q(specifications__value__icontains=q)
        ).distinct()

    # 2. Category Filter
    selected_category = request.GET.get('category', '').strip()
    if selected_category:
        queryset = queryset.filter(category__slug=selected_category)

    # 3. Brand Filter
    selected_brand = request.GET.get('brand', '').strip()
    if selected_brand:
        queryset = queryset.filter(brand__iexact=selected_brand)

    # 4. Power Range Filter
    power_range = request.GET.get('power', '').strip()
    if power_range == 'under_500':
        queryset = queryset.filter(power_watts__gt=0, power_watts__lt=500)
    elif power_range == '500_650':
        queryset = queryset.filter(power_watts__gte=500, power_watts__lte=650)
    elif power_range == 'over_650':
        queryset = queryset.filter(power_watts__gt=650, power_watts__lt=5000)
    elif power_range == 'commercial_inverters':
        queryset = queryset.filter(power_watts__gte=5000)

    # 5. Availability
    in_stock_only = request.GET.get('in_stock', '').strip()
    if in_stock_only == '1':
        queryset = queryset.filter(in_stock=True)

    # 6. Sorting
    sort = request.GET.get('sort', 'featured')
    if sort == 'newest':
        queryset = queryset.order_by('-created_at')
    elif sort == 'name_asc':
        queryset = queryset.order_by('name')
    elif sort == 'power_desc':
        queryset = queryset.order_by('-power_watts', 'name')
    else:
        # Default: Featured first, then newest
        queryset = queryset.order_by('-is_featured', '-created_at')

    # Pagination: 6 products per page
    paginator = Paginator(queryset, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Sidebar Filter Options
    categories = Category.objects.filter(is_active=True).order_by('sort_order')
    brands = Product.objects.filter(is_active=True).values_list('brand', flat=True).distinct().order_by('brand')

    # User saved wishlist IDs
    saved_product_ids = set()
    if request.user.is_authenticated:
        saved_product_ids = set(
            SavedProduct.objects.filter(user=request.user).values_list('product_id', flat=True)
        )

    context = {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'total_count': paginator.count,
        'categories': categories,
        'brands': brands,
        'selected_category': selected_category,
        'selected_brand': selected_brand,
        'power_range': power_range,
        'in_stock_only': in_stock_only,
        'sort': sort,
        'q': q,
        'saved_product_ids': saved_product_ids,
    }
    return render(request, 'catalog/list.html', context)


def product_detail_view(request, slug):
    """
    Comprehensive product specification data sheet, compliance badges,
    lab testing records, and warranty details.
    """
    product = get_object_or_404(
        Product.objects.select_related('category', 'warranty')
        .prefetch_related(
            'specifications__attribute',
            'images',
            'certifications__standard',
            'lab_reports'
        ),
        slug=slug,
        is_active=True
    )

    # Related products from same category
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:3]

    # Wishlist status
    is_saved = False
    if request.user.is_authenticated:
        is_saved = SavedProduct.objects.filter(user=request.user, product=product).exists()

    context = {
        'product': product,
        'specifications': product.specifications.all(),
        'certifications': product.certifications.filter(is_valid=True),
        'lab_reports': product.lab_reports.all(),
        'warranty': getattr(product, 'warranty', None),
        'related_products': related_products,
        'is_saved': is_saved,
    }
    return render(request, 'catalog/detail.html', context)


@login_required
def toggle_saved_product(request, product_id):
    """
    Toggle saving/bookmarking a product in the buyer's wishlist.
    """
    product = get_object_or_404(Product, id=product_id)
    saved_item, created = SavedProduct.objects.get_or_create(user=request.user, product=product)

    if not created:
        saved_item.delete()
        is_saved = False
        message = f"Removed '{product.name}' from your saved products."
    else:
        is_saved = True
        message = f"Saved '{product.name}' to your dashboard."

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse({
            'success': True,
            'is_saved': is_saved,
            'message': message,
            'product_id': product.id,
        })

    messages.success(request, message)
    next_url = request.META.get('HTTP_REFERER') or 'catalog:list'
    return redirect(next_url)
