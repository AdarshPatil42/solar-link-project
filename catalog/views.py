from django.shortcuts import render

def product_list_view(request):
    return render(request, 'catalog/list.html')

def product_detail_view(request, slug):
    return render(request, 'catalog/detail.html', {'slug': slug})
