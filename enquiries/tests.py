from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from enquiries.models import Enquiry, EnquiryItem, EnquiryStatusHistory, EnquiryStatus, ProjectType
from catalog.models import Category, Product
from accounts.models import UserRole


class EnquiriesModuleTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Sales Rep
        self.sales_user = User.objects.create_user(username='sales_rep_1', password='Password123!')
        self.sales_user.profile.role = UserRole.SALES
        self.sales_user.profile.save()

        # Category & Product
        self.category = Category.objects.create(name='Modules', slug='modules')
        self.product = Product.objects.create(
            name='HeliosPro 550W',
            product_code='HP-550',
            category=self.category,
            brand='Helios',
            power_watts=550
        )

        # Existing enquiry for tracking tests
        self.existing_enquiry = Enquiry.objects.create(
            full_name='Tariq Al-Mansoor',
            company_name='Gulf Energy',
            email='tariq@gulfenergy.ae',
            phone='+971 4 800 5544',
            country='United Arab Emirates',
            project_name='50 MW Solar Farm',
            project_type=ProjectType.UTILITY,
            required_capacity='50 MW',
            project_location='Abu Dhabi',
            shipping_destination='Jebel Ali Port',
            preferred_incoterm='CIF',
            message='Detailed request',
            status=EnquiryStatus.QUOTATION_SENT,
            assigned_sales_rep=self.sales_user
        )
        EnquiryItem.objects.create(
            enquiry=self.existing_enquiry,
            product=self.product,
            quantity=90000
        )
        EnquiryStatusHistory.objects.create(
            enquiry=self.existing_enquiry,
            from_status='SUBMITTED',
            to_status=EnquiryStatus.QUOTATION_SENT,
            comment='Official formal quotation sent'
        )

    def test_enquiry_landing_view(self):
        """Test enquiry landing page renders options"""
        response = self.client.get(reverse('enquiries:landing'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Commercial Procurement Engine')
        self.assertContains(response, 'Project RFQ')
        self.assertContains(response, 'Bulk Container Request')

    def test_submit_project_enquiry(self):
        """Test submitting project enquiry generates unique ENQ number and redirects to tracking"""
        payload = {
            'full_name': 'Ali Hassan',
            'company_name': 'Cairo Clean Power',
            'email': 'ali@cairoclean.eg',
            'phone': '+20 100 9876543',
            'country': 'Egypt',
            'project_name': 'Aswan 20 MW Rooftop Array',
            'project_type': ProjectType.COMMERCIAL,
            'required_capacity': '20 MWp',
            'project_location': 'Aswan, Egypt',
            'shipping_destination': 'Alexandria Port',
            'preferred_incoterm': 'CIF',
            'product': self.product.id,
            'quantity': 36000,
            'message': 'Need tier-1 bifacial panels with 30-year performance guarantee.'
        }
        response = self.client.post(reverse('enquiries:project'), payload, follow=True)
        self.assertEqual(response.status_code, 200)

        created_enq = Enquiry.objects.filter(email='ali@cairoclean.eg').first()
        self.assertIsNotNone(created_enq)
        self.assertTrue(created_enq.enquiry_number.startswith('ENQ-'))
        self.assertEqual(created_enq.assigned_sales_rep, self.sales_user)
        self.assertEqual(created_enq.items.count(), 1)
        self.assertEqual(created_enq.status_history.count(), 1)
        self.assertContains(response, created_enq.enquiry_number)
        self.assertContains(response, 'Lifecycle Progress Tracker')

    def test_submit_bulk_quote_request(self):
        """Test submitting bulk quote request creates multi-component enquiry"""
        payload = {
            'full_name': 'David O’Connor',
            'company_name': 'Sydney Solar Wholesale',
            'email': 'david@sydneysolar.com.au',
            'phone': '+61 2 9876 5432',
            'country': 'Australia',
            'shipping_destination': 'Port of Sydney Botany',
            'preferred_incoterm': 'FOB',
            'items_specification': '• 20,000 pcs 550W Panels\n• 50 units 50kW String Inverters'
        }
        response = self.client.post(reverse('enquiries:bulk_quote'), payload, follow=True)
        self.assertEqual(response.status_code, 200)

        bulk_enq = Enquiry.objects.filter(email='david@sydneysolar.com.au').first()
        self.assertIsNotNone(bulk_enq)
        self.assertEqual(bulk_enq.project_type, ProjectType.DISTRIBUTION)
        self.assertContains(response, bulk_enq.enquiry_number)

    def test_status_tracking_lookup(self):
        """Test status tracking page with valid ENQ reference number"""
        response = self.client.get(
            reverse('enquiries:status'),
            {'enquiry_number': self.existing_enquiry.enquiry_number}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.existing_enquiry.enquiry_number)
        self.assertContains(response, '50 MW Solar Farm')
        self.assertContains(response, 'Quotation Sent to Buyer')
        self.assertContains(response, 'HeliosPro 550W')
        self.assertContains(response, 'Official formal quotation sent')
