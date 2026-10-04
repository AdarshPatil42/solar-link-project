from django.contrib import admin
from .models import Country, ShippingTerm, ExportDocument


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'region', 'flag_emoji', 'primary_ports', 'is_active', 'sort_order')
    list_filter = ('region', 'is_active')
    search_fields = ('name', 'code', 'primary_ports')
    list_editable = ('is_active', 'sort_order')


@admin.register(ShippingTerm)
class ShippingTermAdmin(admin.ModelAdmin):
    list_display = ('incoterm', 'title', 'is_recommended', 'estimated_transit_days', 'minimum_order', 'sort_order')
    list_editable = ('is_recommended', 'sort_order')
    search_fields = ('incoterm', 'title', 'seller_responsibility', 'buyer_responsibility')


@admin.register(ExportDocument)
class ExportDocumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'issuing_party', 'is_mandatory', 'sort_order')
    list_filter = ('is_mandatory',)
    search_fields = ('name', 'code', 'purpose', 'issuing_party')
    list_editable = ('is_mandatory', 'sort_order')
