from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, SavedProduct


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile Details'
    fk_name = 'user'


class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff')
    list_select_related = ('profile',)

    def get_role(self, instance):
        if hasattr(instance, 'profile'):
            return instance.profile.get_role_display()
        return '-'
    get_role.short_description = 'SolarLink Role'


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'company_name', 'country', 'phone', 'created_at')
    list_filter = ('role', 'country')
    search_fields = ('user__username', 'user__email', 'company_name', 'country')


@admin.register(SavedProduct)
class SavedProductAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    search_fields = ('user__username', 'product__name')
