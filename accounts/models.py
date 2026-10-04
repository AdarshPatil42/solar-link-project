from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserRole(models.TextChoices):
    BUYER = 'BUYER', 'Buyer'
    SALES = 'SALES', 'Sales Executive'
    ADMIN = 'ADMIN', 'Administrator'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.BUYER)
    company_name = models.CharField(max_length=150, blank=True, default='')
    phone = models.CharField(max_length=30, blank=True, default='')
    country = models.CharField(max_length=100, blank=True, default='')
    job_title = models.CharField(max_length=100, blank=True, default='')
    avatar = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def is_buyer(self):
        return self.role == UserRole.BUYER

    @property
    def is_sales(self):
        return self.role == UserRole.SALES

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN or self.user.is_superuser


class SavedProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_products')
    product = models.ForeignKey('catalog.Product', on_delete=models.CASCADE, related_name='saved_by_users')
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Saved Product'
        verbose_name_plural = 'Saved Products'
        unique_together = ('user', 'product')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} -> {self.product.name if hasattr(self.product, 'name') else 'Product'}"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        role = UserRole.ADMIN if instance.is_superuser else UserRole.BUYER
        UserProfile.objects.create(user=instance, role=role)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
        else:
            role = UserRole.ADMIN if instance.is_superuser else UserRole.BUYER
            UserProfile.objects.create(user=instance, role=role)
