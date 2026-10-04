from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.buyer_dashboard_view, name='buyer_dashboard'),
    path('saved-products/', views.buyer_saved_products_view, name='saved_products'),
    path('enquiries/', views.buyer_enquiries_list_view, name='buyer_enquiries'),
    path('enquiries/<int:pk>/', views.buyer_enquiry_detail_view, name='buyer_enquiry_detail'),
    path('quotations/', views.buyer_quotations_list_view, name='buyer_quotations'),
    path('quotations/<int:pk>/', views.buyer_quotation_detail_view, name='buyer_quotation_detail'),
    path('admin-portal/', views.admin_dashboard_view, name='admin_dashboard'),
    path('sales-portal/', views.sales_dashboard_view, name='sales_dashboard'),
]

