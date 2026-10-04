from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from catalog.models import Category, Product, SpecificationAttribute, ProductSpecification
from accounts.models import SavedProduct


class CatalogModuleTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='buyer_test', password='TestPassword123!')

        # Category
        self.category = Category.objects.create(
            name='Solar PV Modules',
            slug='solar-panels',
            icon_name='sun'
        )

        # Attribute
        self.attr_power = SpecificationAttribute.objects.create(
            name='Rated Power Output',
            unit='W'
        )
        self.attr_eff = SpecificationAttribute.objects.create(
            name='Maximum Efficiency',
            unit='%'
        )

        # Product
        self.product = Product.objects.create(
            name='SolarMax 550W Bifacial PERC',
            product_code='SM-550-BF',
            category=self.category,
            brand='SolarMax',
            technology_type='Bifacial Mono PERC',
            power_watts=550,
            short_description='High efficiency tier-1 module',
            full_description='Long description for SolarMax 550W',
            is_featured=True,
            in_stock=True
        )

        # EAV Specs
        ProductSpecification.objects.create(
            product=self.product,
            attribute=self.attr_power,
            value='550'
        )
        ProductSpecification.objects.create(
            product=self.product,
            attribute=self.attr_eff,
            value='21.3'
        )

    def test_product_slug_and_display_power(self):
        """Test slug generation and display_power formatting"""
        self.assertTrue(self.product.slug)
        self.assertEqual(self.product.display_power, '550 W')

    def test_catalog_list_view(self):
        """Test catalog listing view renders successfully with products"""
        response = self.client.get(reverse('catalog:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SolarMax 550W Bifacial PERC')
        self.assertContains(response, '550 W')

    def test_catalog_search_filtering(self):
        """Test search query matching SKU, brand, or name"""
        response = self.client.get(reverse('catalog:list'), {'q': 'SM-550'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SM-550-BF')

        # Negative search
        neg_response = self.client.get(reverse('catalog:list'), {'q': 'NonExistentProduct'})
        self.assertEqual(neg_response.status_code, 200)
        self.assertContains(neg_response, 'No matching equipment found')

    def test_catalog_category_and_power_filter(self):
        """Test category and power range filters"""
        response = self.client.get(reverse('catalog:list'), {
            'category': 'solar-panels',
            'power': '500_650'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SolarMax 550W')

    def test_product_detail_view(self):
        """Test product detail view loads specs, category, and action buttons"""
        response = self.client.get(reverse('catalog:detail', kwargs={'slug': self.product.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Rated Power Output')
        self.assertContains(response, '21.3')
        self.assertContains(response, 'Request Commercial Quote')

    def test_toggle_saved_product_authenticated(self):
        """Test buyer can toggle product in wishlist"""
        self.client.login(username='buyer_test', password='TestPassword123!')
        
        # Save product
        resp = self.client.get(reverse('catalog:toggle_saved', kwargs={'product_id': self.product.id}), follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(SavedProduct.objects.filter(user=self.user, product=self.product).exists())

        # Unsave product
        resp2 = self.client.get(reverse('catalog:toggle_saved', kwargs={'product_id': self.product.id}), follow=True)
        self.assertEqual(resp2.status_code, 200)
        self.assertFalse(SavedProduct.objects.filter(user=self.user, product=self.product).exists())
