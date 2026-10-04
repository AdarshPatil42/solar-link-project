from datetime import date
from django.test import TestCase, Client
from django.urls import reverse
from certifications.models import ComplianceStandard, StandardCategory, Certification, LabReport
from catalog.models import Category, Product


class CertificationsModuleTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        self.category = Category.objects.create(name='Inverters', slug='inverters')
        self.product = Product.objects.create(
            name='VoltCore 10k',
            product_code='VC-10K',
            category=self.category,
            brand='VoltCore',
            short_description='Inverter'
        )

        self.standard = ComplianceStandard.objects.create(
            name='IEC 62109',
            category=StandardCategory.ELECTRICAL,
            issuing_body='TÜV Rheinland',
            description='Safety of power converters for use in photovoltaic power systems'
        )

        self.cert = Certification.objects.create(
            certificate_number='TUV-62109-01',
            title='Inverter Safety Certificate',
            standard=self.standard,
            issuing_organization='TÜV Rheinland',
            issue_date=date(2025, 1, 1),
            is_valid=True
        )
        self.cert.products.add(self.product)

        self.report = LabReport.objects.create(
            report_number='LAB-62109-REP',
            product=self.product,
            testing_laboratory='TÜV Cologne Lab',
            test_date=date(2025, 2, 1),
            test_type='High Voltage Insulation & Grounding Test',
            result='Passed'
        )

    def test_certifications_index_view(self):
        """Test certifications directory loads standards and lab reports"""
        response = self.client.get(reverse('certifications:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'IEC 62109')
        self.assertContains(response, 'TUV-62109-01')
        self.assertContains(response, 'LAB-62109-REP')
