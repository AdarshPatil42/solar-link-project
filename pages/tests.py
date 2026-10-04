from django.test import TestCase, Client
from django.urls import reverse
from pages.models import ContactMessage, FAQ, TeamMember, TeamDepartment
from catalog.models import Category, Product


class PagesModuleTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Solar PV', slug='solar-pv')
        self.product = Product.objects.create(
            name='Test Panel 500W',
            product_code='TP-500',
            category=self.category,
            brand='TestBrand',
            is_featured=True
        )
        self.team_member = TeamMember.objects.create(
            name='Dr. Henrik Weber',
            designation='Managing Director',
            department=TeamDepartment.MANAGEMENT,
            bio='20+ years of solar leadership'
        )
        self.faq = FAQ.objects.create(
            question='What is the MOQ for container export?',
            answer='1x 20ft container.',
            is_published=True
        )

    def test_home_page_view(self):
        """Test homepage renders with hero, stats, and featured equipment"""
        response = self.client.get(reverse('pages:home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Reliable Solar & Renewable Energy Equipment')
        self.assertContains(response, 'Test Panel 500W')
        self.assertContains(response, 'Solar PV')

    def test_about_page_view(self):
        """Test about page renders credentials, 7-step process, and team members"""
        response = self.client.get(reverse('pages:about'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dr. Henrik Weber')
        self.assertContains(response, '7-Step Export Process')
        self.assertContains(response, 'Browse Certified Products')

    def test_contact_form_submission(self):
        """Test submitting contact message successfully creates ContactMessage record"""
        payload = {
            'full_name': 'Carlos Mendez',
            'email': 'carlos@mendezsolar.es',
            'phone': '+34 91 123 4567',
            'company': 'Mendez Solar S.L.',
            'subject': 'Inquiry for 10 MW TopCon modules',
            'message': 'Please provide container price CIF Valencia.'
        }
        response = self.client.post(reverse('pages:contact'), payload, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ContactMessage.objects.filter(email='carlos@mendezsolar.es').exists())
        self.assertContains(response, 'Thank you, Carlos Mendez!')
