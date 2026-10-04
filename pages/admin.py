from django.contrib import admin
from .models import ContactMessage, FAQ, TeamMember


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'company', 'subject', 'is_resolved', 'created_at')
    list_filter = ('is_resolved', 'created_at')
    search_fields = ('full_name', 'email', 'company', 'subject', 'message')
    list_editable = ('is_resolved',)


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'order', 'is_published')
    list_filter = ('category', 'is_published')
    search_fields = ('question', 'answer')
    list_editable = ('order', 'is_published')


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'designation', 'department', 'email', 'phone', 'is_active', 'order')
    list_filter = ('department', 'is_active')
    search_fields = ('name', 'designation', 'bio')
    list_editable = ('is_active', 'order')
