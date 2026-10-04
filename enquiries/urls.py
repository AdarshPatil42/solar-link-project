from django.urls import path
from . import views

app_name = 'enquiries'

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('project/', views.project_enquiry_view, name='project'),
    path('bulk-quote/', views.bulk_quote_view, name='bulk_quote'),
    path('status/', views.status_tracking_view, name='status'),
]
