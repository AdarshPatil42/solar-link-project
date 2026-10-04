from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from accounts.models import UserProfile, UserRole


class AccountsAndRBACTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Create Admin
        self.admin_user = User.objects.create_user(
            username='test_admin',
            email='admin@test.com',
            password='Password123!',
            is_staff=True,
            is_superuser=True
        )
        self.admin_user.profile.role = UserRole.ADMIN
        self.admin_user.profile.save()

        # Create Sales
        self.sales_user = User.objects.create_user(
            username='test_sales',
            email='sales@test.com',
            password='Password123!'
        )
        self.sales_user.profile.role = UserRole.SALES
        self.sales_user.profile.save()

        # Create Buyer
        self.buyer_user = User.objects.create_user(
            username='test_buyer',
            email='buyer@test.com',
            password='Password123!'
        )
        self.buyer_user.profile.role = UserRole.BUYER
        self.buyer_user.profile.save()

    def test_profile_auto_creation_and_roles(self):
        """Test that every new User automatically gets a linked UserProfile"""
        new_user = User.objects.create_user(
            username='brand_new',
            email='new@test.com',
            password='Password123!'
        )
        self.assertTrue(hasattr(new_user, 'profile'))
        self.assertEqual(new_user.profile.role, UserRole.BUYER)
        self.assertTrue(new_user.profile.is_buyer)
        self.assertFalse(new_user.profile.is_sales)
        self.assertFalse(new_user.profile.is_admin)

    def test_login_and_logout(self):
        """Test standard login and logout redirects"""
        response = self.client.post(reverse('accounts:login'), {
            'username': 'test_buyer',
            'password': 'Password123!'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)

        logout_response = self.client.get(reverse('accounts:logout'), follow=True)
        self.assertEqual(logout_response.status_code, 200)
        self.assertFalse(logout_response.context['user'].is_authenticated)

    def test_buyer_dashboard_access_control(self):
        """Buyer should access buyer dashboard, but get redirected away from sales dashboard"""
        self.client.login(username='test_buyer', password='Password123!')
        
        # Access Buyer dashboard
        buyer_resp = self.client.get(reverse('dashboard:buyer_dashboard'))
        self.assertEqual(buyer_resp.status_code, 200)
        self.assertContains(buyer_resp, 'Buyer Portal')

        # Attempt to access Sales dashboard
        sales_resp = self.client.get(reverse('dashboard:sales_dashboard'), follow=True)
        self.assertEqual(sales_resp.status_code, 200)
        # Should be redirected to home with error message
        self.assertContains(sales_resp, "You do not have permission")

    def test_sales_dashboard_access_control(self):
        """Sales should access sales dashboard"""
        self.client.login(username='test_sales', password='Password123!')
        sales_resp = self.client.get(reverse('dashboard:sales_dashboard'))
        self.assertEqual(sales_resp.status_code, 200)
        self.assertContains(sales_resp, 'Sales Workspace')

    def test_admin_has_universal_access(self):
        """Superuser/Admin should access admin dashboard, buyer dashboard, and sales dashboard"""
        self.client.login(username='test_admin', password='Password123!')
        
        admin_resp = self.client.get(reverse('dashboard:admin_dashboard'))
        self.assertEqual(admin_resp.status_code, 200)

        sales_resp = self.client.get(reverse('dashboard:sales_dashboard'))
        self.assertEqual(sales_resp.status_code, 200)

        buyer_resp = self.client.get(reverse('dashboard:buyer_dashboard'))
        self.assertEqual(buyer_resp.status_code, 200)

    def test_user_registration_form(self):
        """Test registration endpoint creates buyer account and logs user in"""
        payload = {
            'username': 'registered_buyer',
            'first_name': 'Hassan',
            'last_name': 'Kamal',
            'email': 'hassan@solaregypt.com',
            'company_name': 'Cairo Solar Energy',
            'country': 'Egypt',
            'phone': '+20 100 1234567',
            'role': UserRole.BUYER,
            'password': 'SecurePassword2026!',
            'password_confirm': 'SecurePassword2026!'
        }
        resp = self.client.post(reverse('accounts:register'), payload, follow=True)
        self.assertEqual(resp.status_code, 200)
        
        created_user = User.objects.get(username='registered_buyer')
        self.assertEqual(created_user.profile.company_name, 'Cairo Solar Energy')
        self.assertEqual(created_user.profile.country, 'Egypt')
        self.assertEqual(created_user.profile.role, UserRole.BUYER)
