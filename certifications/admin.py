from django.contrib import admin
from .models import ComplianceStandard, Certification, LabReport, Warranty


@admin.register(ComplianceStandard)
class ComplianceStandardAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'issuing_body', 'is_active', 'sort_order')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'issuing_body', 'description')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('certificate_number', 'title', 'standard', 'issuing_organization', 'issue_date', 'expiry_date', 'is_valid')
    list_filter = ('standard', 'is_valid')
    search_fields = ('certificate_number', 'title', 'issuing_organization')
    filter_horizontal = ('products',)


@admin.register(LabReport)
class LabReportAdmin(admin.ModelAdmin):
    list_display = ('report_number', 'product', 'test_type', 'testing_laboratory', 'test_date', 'status')
    list_filter = ('status', 'test_type')
    search_fields = ('report_number', 'product__name', 'testing_laboratory', 'test_type')


@admin.register(Warranty)
class WarrantyAdmin(admin.ModelAdmin):
    list_display = ('product', 'product_warranty_years', 'performance_warranty_years', 'updated_at')
    search_fields = ('product__name', 'coverage_details')
