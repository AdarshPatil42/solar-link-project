from django.test import TestCase, Client
from django.urls import reverse
from exports.models import Country, ShippingTerm, ExportDocument, IncotermCode


class ExportsModuleTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        self.country = Country.objects.create(
            name='United Arab Emirates',
            code='AE',
            region='Middle East & GCC',
            flag_emoji='🇦🇪',
            primary_ports='Jebel Ali Port'
        )

        self.shipping_term = ShippingTerm.objects.create(
            incoterm=IncotermCode.FOB,
            title='Free On Board',
            buyer_responsibility='Ocean Freight and destination customs clearance',
            seller_responsibility='Loading on vessel at port of origin',
            risk_transfer_point='Ship rail at origin port',
            is_recommended=True
        )

        self.doc = ExportDocument.objects.create(
            name='Commercial Invoice',
            code='DOC-CI',
            purpose='Customs clearance and trade tariff settlement',
            issuing_party='SolarLink Finance',
            is_mandatory=True
        )

    def test_exports_info_view(self):
        """Test export info page loads Incoterms, countries, and documents"""
        response = self.client.get(reverse('exports:info'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Incoterms 2020 Commercial Matrix')
        self.assertContains(response, 'United Arab Emirates')
        self.assertContains(response, 'Commercial Invoice')
        self.assertContains(response, 'FOB')
