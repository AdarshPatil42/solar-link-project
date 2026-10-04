from django.shortcuts import render

def home_view(request):
    return render(request, 'home/index.html')

def about_view(request):
    return render(request, 'about/about.html')

def contact_view(request):
    return render(request, 'contact/contact.html')
