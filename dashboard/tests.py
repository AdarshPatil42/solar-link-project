from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import UserProfile, UserRole, SavedProduct
from catalog.models import Category, Product
from enquiries.models import Enquiry, EnquiryItem, EnquiryStatus, ProjectType, Quotation, QuotationItem


class DashboardPhase4Tests(TestCase):
    def setUp(self):
        self.client = Client()

        # Create Buyer user
        self.buyer_user = User.objects.create_user(
            username='test_buyer',
            email='buyer@test.com',
            password='password123',
            first_name='Tariq'
        )
        self.buyer_profile = self.buyer_user.profile
        self.buyer_profile.role = UserRole.BUYER
        self.buyer_profile.company_name = 'Test EPC Solar Ltd'
        self.buyer_profile.country = 'Oman'
        self.buyer_profile.phone = '+96899999999'
        self.buyer_profile.save()

        # Create Sales user
        self.sales_user = User.objects.create_user(
            username='test_sales',
            email='sales@test.com',
            password='password123',
            first_name='Alex'
        )
        self.sales_profile = self.sales_user.profile
        self.sales_profile.role = UserRole.SALES
        self.sales_profile.company_name = 'SolarLink Export Desk'
        self.sales_profile.country = 'UAE'
        self.sales_profile.phone = '+97148007000'
        self.sales_profile.save()

        # Create Admin user
        self.admin_user = User.objects.create_user(
            username='test_admin',
            email='admin@test.com',
            password='password123',
            first_name='Admin',
            is_staff=True,
            is_superuser=True
        )
        self.admin_profile = self.admin_user.profile
        self.admin_profile.role = UserRole.ADMIN
        self.admin_profile.company_name = 'SolarLink HQ'
        self.admin_profile.country = 'Germany'
        self.admin_profile.phone = '+49301234567'
        self.admin_profile.save()

        # Create Category & Product
        self.category = Category.objects.create(name='Solar Modules', slug='solar-modules')
        self.product = Product.objects.create(
            name='580W TOPCon Bifacial',
            slug='580w-topcon-bifacial',
            category=self.category,
            brand='SolarMax',
            product_code='SM-580-TC',
            short_description='High efficiency N-type TOPCon bifacial module'
        )

        # Create Wishlist item
        SavedProduct.objects.create(user=self.buyer_user, product=self.product)

        # Create Enquiry
        self.enquiry = Enquiry.objects.create(
            buyer=self.buyer_user,
            full_name='Tariq Al-Mansoor',
            company_name='Test EPC Solar Ltd',
            email='buyer@test.com',
            phone='+96899999999',
            country='Oman',
            project_name='5MW Sohar Industrial Solar Farm',
            project_type=ProjectType.UTILITY,
            required_capacity='5 MWp',
            project_location='Sohar, Oman',
            shipping_destination='Sohar Port, Oman',
            preferred_incoterm='CIF',
            message='Need 8600 units with delivery in 60 days',
            status=EnquiryStatus.QUOTATION_SENT,
            assigned_sales_rep=self.sales_user
        )

        self.enquiry_item = EnquiryItem.objects.create(
            enquiry=self.enquiry,
            product=self.product,
            quantity=8600,
            target_price_usd=120.00,
            notes='Grade A tier-1'
        )

        # Create Quotation
        self.quotation = Quotation.objects.create(
            enquiry=self.enquiry,
            sales_rep=self.sales_user,
            total_amount=1032000.00,
            currency='USD',
            incoterm='CIF',
            payment_terms='30% T/T Advance, 70% B/L',
            valid_until=date.today() + timedelta(days=30),
            status=Quotation.QuotationStatus.SENT,
            sales_rep_notes='Includes CIF freight and cargo insurance.'
        )

        self.quotation_item = QuotationItem.objects.create(
            quotation=self.quotation,
            product=self.product,
            quantity=8600,
            unit_price=120.00,
            subtotal=1032000.00,
            specifications_summary='580W TOPCon Modules'
        )

    # ==========================
    # BUYER PORTAL TESTS
    # ==========================
    def test_buyer_dashboard_view(self):
        self.client.login(username='test_buyer', password='password123')
        response = self.client.get(reverse('dashboard:buyer_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome back, Tariq')
        self.assertContains(response, '5MW Sohar Industrial Solar Farm')
        self.assertContains(response, 'Test EPC Solar Ltd')

    def test_buyer_saved_products_view(self):
        self.client.login(username='test_buyer', password='password123')
        response = self.client.get(reverse('dashboard:saved_products'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '580W TOPCon Bifacial')

    def test_buyer_enquiries_list_view(self):
        self.client.login(username='test_buyer', password='password123')
        response = self.client.get(reverse('dashboard:buyer_enquiries'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.enquiry.enquiry_number)
        self.assertContains(response, '5MW Sohar Industrial Solar Farm')

    def test_buyer_enquiry_detail_view(self):
        self.client.login(username='test_buyer', password='password123')
        response = self.client.get(reverse('dashboard:buyer_enquiry_detail', kwargs={'pk': self.enquiry.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.enquiry.enquiry_number)
        self.assertContains(response, 'Procurement Milestone Pipeline')
        self.assertContains(response, 'Assigned Sales Engineer')

    def test_buyer_quotations_list_view(self):
        self.client.login(username='test_buyer', password='password123')
        response = self.client.get(reverse('dashboard:buyer_quotations'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.quotation.quote_number)
        self.assertContains(response, '1032000.00')

    def test_buyer_quotation_detail_view(self):
        self.client.login(username='test_buyer', password='password123')
        response = self.client.get(reverse('dashboard:buyer_quotation_detail', kwargs={'pk': self.quotation.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.quotation.quote_number)
        self.assertContains(response, 'Commercial Quotation Review')
        self.assertContains(response, 'Accept Quotation')

    def test_buyer_accept_quotation(self):
        self.client.login(username='test_buyer', password='password123')
        post_data = {
            'action': 'accept',
            'feedback_notes': 'Confirmed! Please send bilateral sales contract and proforma invoice.'
        }
        response = self.client.post(reverse('dashboard:buyer_quotation_detail', kwargs={'pk': self.quotation.id}), post_data)
        self.assertEqual(response.status_code, 302)

        self.quotation.refresh_from_db()
        self.enquiry.refresh_from_db()
        self.assertEqual(self.quotation.status, Quotation.QuotationStatus.ACCEPTED)
        self.assertEqual(self.enquiry.status, EnquiryStatus.APPROVED)
        self.assertIn('Confirmed', self.quotation.buyer_feedback)

    def test_buyer_negotiate_quotation(self):
        self.client.login(username='test_buyer', password='password123')
        post_data = {
            'action': 'negotiate',
            'feedback_notes': 'Can you provide 3% discount for 100% advance LC?'
        }
        response = self.client.post(reverse('dashboard:buyer_quotation_detail', kwargs={'pk': self.quotation.id}), post_data)
        self.assertEqual(response.status_code, 302)

        self.quotation.refresh_from_db()
        self.enquiry.refresh_from_db()
        self.assertEqual(self.quotation.status, Quotation.QuotationStatus.NEGOTIATING)
        self.assertEqual(self.enquiry.status, EnquiryStatus.NEGOTIATION)
        self.assertIn('3% discount', self.quotation.buyer_feedback)

    # ==========================
    # SALES EXECUTIVE WORKSPACE TESTS
    # ==========================
    def test_sales_dashboard_view(self):
        self.client.login(username='test_sales', password='password123')
        response = self.client.get(reverse('sales:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sales Command Center')
        self.assertContains(response, 'Alex')
        self.assertContains(response, 'Total Leads Assigned')

    def test_sales_enquiries_list_view(self):
        self.client.login(username='test_sales', password='password123')
        response = self.client.get(reverse('sales:enquiries'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.enquiry.enquiry_number)
        self.assertContains(response, '5MW Sohar Industrial Solar Farm')

    def test_sales_enquiry_detail_and_stage_update(self):
        self.client.login(username='test_sales', password='password123')
        url = reverse('sales:enquiry_detail', kwargs={'pk': self.enquiry.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Update Deal Stage')

        # Test updating stage
        post_data = {
            'update_status': '1',
            'status': EnquiryStatus.NEGOTIATION,
            'comment': 'Discussed volume discount with buyer over conference call.'
        }
        post_response = self.client.post(url, post_data)
        self.assertEqual(post_response.status_code, 302)

        self.enquiry.refresh_from_db()
        self.assertEqual(self.enquiry.status, EnquiryStatus.NEGOTIATION)

    def test_sales_create_quotation_flow(self):
        self.client.login(username='test_sales', password='password123')
        url = reverse('sales:create_quote', kwargs={'pk': self.enquiry.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Commercial Quotation Builder')

        post_data = {
            'total_amount': '1050000.00',
            'currency': 'USD',
            'incoterm': 'CIF',
            'payment_terms': '30% T/T Advance, 70% B/L',
            'valid_until': (date.today() + timedelta(days=20)).strftime('%Y-%m-%d'),
            'sales_rep_notes': 'New revised quote with optimized shipping schedule.'
        }
        post_response = self.client.post(url, post_data)
        self.assertEqual(post_response.status_code, 302)

        new_quote = Quotation.objects.filter(enquiry=self.enquiry).order_by('-created_at').first()
        self.assertIsNotNone(new_quote)
        self.assertEqual(float(new_quote.total_amount), 1050000.00)
        self.assertEqual(new_quote.status, Quotation.QuotationStatus.SENT)

    def test_sales_quotations_list_and_detail(self):
        self.client.login(username='test_sales', password='password123')
        list_resp = self.client.get(reverse('sales:quotations'))
        self.assertEqual(list_resp.status_code, 200)
        self.assertContains(list_resp, self.quotation.quote_number)

        detail_resp = self.client.get(reverse('sales:quotation_detail', kwargs={'pk': self.quotation.id}))
        self.assertEqual(detail_resp.status_code, 200)
        self.assertContains(detail_resp, self.quotation.quote_number)
        self.assertContains(detail_resp, 'Quotation Notes')

    def test_sales_pipeline_kanban(self):
        self.client.login(username='test_sales', password='password123')
        response = self.client.get(reverse('sales:pipeline'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Export Sales Deal Pipeline')
        self.assertContains(response, 'NEW / REQUESTED')
        self.assertContains(response, 'QUOTE SENT')
        self.assertContains(response, 'WON / APPROVED')

    # ==========================
    # SECURITY & RBAC RESTRICTIONS
    # ==========================
    def test_buyer_cannot_access_sales_portal(self):
        self.client.login(username='test_buyer', password='password123')
        response = self.client.get(reverse('sales:dashboard'))
        # Should be forbidden (403) or redirected
        self.assertIn(response.status_code, [302, 403])

    def test_buyer_cannot_access_admin_portal(self):
        self.client.login(username='test_buyer', password='password123')
        response = self.client.get(reverse('dashboard:admin_dashboard'))
        self.assertIn(response.status_code, [302, 403])

    def test_buyer_cannot_export_csv(self):
        self.client.login(username='test_buyer', password='password123')
        response = self.client.get(reverse('dashboard:export_products_csv'))
        self.assertIn(response.status_code, [302, 403])

    # ==========================
    # PHASE 5: ADMIN & CSV EXPORT TESTS
    # ==========================
    def test_admin_dashboard_view(self):
        self.client.login(username='test_admin', password='password123')
        response = self.client.get(reverse('dashboard:admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Global Operations &amp; Commercial Analytics')
        self.assertContains(response, 'Instant CSV Data Export Engine')
        self.assertContains(response, 'Equipment Catalog')

    def test_export_products_csv(self):
        self.client.login(username='test_admin', password='password123')
        response = self.client.get(reverse('dashboard:export_products_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
        self.assertIn('SolarLink_Products_Export.csv', response['Content-Disposition'])
        content = response.content.decode('utf-8')
        self.assertIn('Product Code,Product Name,Category', content)
        self.assertIn(self.product.product_code, content)
        self.assertIn('580W TOPCon Bifacial', content)

    def test_export_enquiries_csv(self):
        self.client.login(username='test_admin', password='password123')
        response = self.client.get(reverse('dashboard:export_enquiries_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
        self.assertIn('SolarLink_Enquiries_Export.csv', response['Content-Disposition'])
        content = response.content.decode('utf-8')
        self.assertIn('Enquiry Ref,Buyer Name,Company Name', content)
        self.assertIn(self.enquiry.enquiry_number, content)
        self.assertIn('5MW Sohar Industrial Solar Farm', content)

    def test_export_buyers_csv(self):
        self.client.login(username='test_admin', password='password123')
        response = self.client.get(reverse('dashboard:export_buyers_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
        self.assertIn('SolarLink_Buyers_Export.csv', response['Content-Disposition'])
        content = response.content.decode('utf-8')
        self.assertIn('Username,Full Name,Email', content)
        self.assertIn('test_buyer', content)
        self.assertIn('Test EPC Solar Ltd', content)

    def test_export_quotations_csv(self):
        self.client.login(username='test_admin', password='password123')
        response = self.client.get(reverse('dashboard:export_quotations_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
        self.assertIn('SolarLink_Quotations_Export.csv', response['Content-Disposition'])
        content = response.content.decode('utf-8')
        self.assertIn('Quote Ref,Enquiry Ref,Project Name', content)
        self.assertIn(self.quotation.quote_number, content)
        self.assertIn('1032000.00', content)

    def test_export_pipeline_csv(self):
        self.client.login(username='test_admin', password='password123')
        response = self.client.get(reverse('dashboard:export_pipeline_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
        self.assertIn('SolarLink_Sales_Pipeline_Export.csv', response['Content-Disposition'])
        content = response.content.decode('utf-8')
        self.assertIn('Enquiry Ref,Project Name,Client Company', content)
        self.assertIn(self.enquiry.enquiry_number, content)
        self.assertIn('5MW Sohar Industrial Solar Farm', content)
