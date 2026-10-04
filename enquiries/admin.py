from django.contrib import admin
from .models import Enquiry, EnquiryItem, EnquiryStatusHistory, Quotation, QuotationItem


class EnquiryItemInline(admin.TabularInline):
    model = EnquiryItem
    extra = 1


class EnquiryStatusHistoryInline(admin.TabularInline):
    model = EnquiryStatusHistory
    extra = 0
    readonly_fields = ('from_status', 'to_status', 'changed_by', 'timestamp')


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display = ('enquiry_number', 'company_name', 'full_name', 'country', 'project_type', 'required_capacity', 'status', 'assigned_sales_rep', 'created_at')
    list_filter = ('status', 'project_type', 'created_at')
    search_fields = ('enquiry_number', 'company_name', 'full_name', 'email', 'project_name')
    readonly_fields = ('enquiry_number', 'created_at', 'updated_at')
    inlines = [EnquiryItemInline, EnquiryStatusHistoryInline]


class QuotationItemInline(admin.TabularInline):
    model = QuotationItem
    extra = 1


@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ('quote_number', 'enquiry', 'sales_rep', 'total_amount', 'currency', 'status', 'valid_until', 'created_at')
    list_filter = ('status', 'currency')
    search_fields = ('quote_number', 'enquiry__enquiry_number', 'sales_rep__username')
    readonly_fields = ('quote_number', 'created_at', 'updated_at')
    inlines = [QuotationItemInline]
