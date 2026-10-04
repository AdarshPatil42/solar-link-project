from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('buyer/', views.buyer_dashboard_view, name='buyer_dashboard'),
    path('sales/', views.sales_dashboard_view, name='sales_dashboard'),
    path('admin-portal/', views.admin_dashboard_view, name='admin_dashboard'),
]
