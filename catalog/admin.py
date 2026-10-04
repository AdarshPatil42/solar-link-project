from django.contrib import admin
from .models import Category, Product, ProductImage, SpecificationAttribute, ProductSpecification


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 2


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon_name', 'is_active', 'sort_order')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_active', 'sort_order')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_code', 'category', 'brand', 'is_featured', 'is_active', 'created_at')
    list_filter = ('category', 'brand', 'is_featured', 'is_active')
    search_fields = ('name', 'product_code', 'brand', 'short_description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductSpecificationInline]


@admin.register(SpecificationAttribute)
class SpecificationAttributeAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit', 'description')
    search_fields = ('name',)
