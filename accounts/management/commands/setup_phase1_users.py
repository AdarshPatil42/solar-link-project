from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile, UserRole


class Command(BaseCommand):
    help = 'Seeds initial demonstration users for Admin, Sales Executive, and Buyer roles'

    def handle(self, *args, **options):
        # 1. Administrator
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@solarlink.io',
                'first_name': 'SolarLink',
                'last_name': 'Administrator',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        admin_user.set_password('admin123')
        admin_user.save()
        admin_profile = admin_user.profile
        admin_profile.role = UserRole.ADMIN
        admin_profile.company_name = 'SolarLink Global Operations'
        admin_profile.country = 'Germany'
        admin_profile.job_title = 'Chief Operations Director'
        admin_profile.save()
        self.stdout.write(self.style.SUCCESS('Admin user ready: admin / admin123'))

        # 2. Sales Executive
        sales_user, created = User.objects.get_or_create(
            username='sales_alex',
            defaults={
                'email': 'alex.vance@solarlink.io',
                'first_name': 'Alex',
                'last_name': 'Vance',
                'is_staff': True,
            }
        )
        sales_user.set_password('solarlink123')
        sales_user.save()
        sales_profile = sales_user.profile
        sales_profile.role = UserRole.SALES
        sales_profile.company_name = 'SolarLink Trade Desk'
        sales_profile.country = 'Germany'
        sales_profile.job_title = 'Senior Export Sales Representative'
        sales_profile.phone = '+49 30 9876543'
        sales_profile.save()
        self.stdout.write(self.style.SUCCESS('Sales user ready: sales_alex / solarlink123'))

        # 3. Buyer
        buyer_user, created = User.objects.get_or_create(
            username='buyer_tariq',
            defaults={
                'email': 'tariq@gulfenergy.ae',
                'first_name': 'Tariq',
                'last_name': 'Al-Mansoor',
            }
        )
        buyer_user.set_password('solarlink123')
        buyer_user.save()
        buyer_profile = buyer_user.profile
        buyer_profile.role = UserRole.BUYER
        buyer_profile.company_name = 'Gulf Renewable Infrastructure'
        buyer_profile.country = 'United Arab Emirates'
        buyer_profile.job_title = 'Director of EPC Procurement'
        buyer_profile.phone = '+971 4 800 5544'
        buyer_profile.save()
        self.stdout.write(self.style.SUCCESS('Buyer user ready: buyer_tariq / solarlink123'))
