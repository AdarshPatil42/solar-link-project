from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('catalog/', include('catalog.urls')),
    path('enquiry/', include('enquiries.urls')),
    path('certifications/', include('certifications.urls')),
    path('export-info/', include('exports.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('', include('pages.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
