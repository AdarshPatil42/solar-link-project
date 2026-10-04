from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('dashboard/', views.sales_dashboard_view, name='dashboard'),
    path('enquiries/', views.sales_enquiries_list_view, name='enquiries'),
    path('enquiries/<int:pk>/', views.sales_enquiry_detail_view, name='enquiry_detail'),
    path('enquiries/<int:pk>/create-quote/', views.sales_create_quote_view, name='create_quote'),
    path('quotations/', views.sales_quotations_list_view, name='quotations'),
    path('quotations/<int:pk>/', views.sales_quotation_detail_view, name='quotation_detail'),
    path('pipeline/', views.sales_pipeline_board_view, name='pipeline'),
]
