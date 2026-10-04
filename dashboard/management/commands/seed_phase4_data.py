from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile, UserRole, SavedProduct
from catalog.models import Product, Category
from enquiries.models import Enquiry, EnquiryItem, EnquiryStatus, ProjectType, Quotation, QuotationItem, EnquiryStatusHistory


class Command(BaseCommand):
    help = 'Seeds realistic demonstration leads, quotations, and pipeline deals for Phase 4'

    def handle(self, *args, **options):
        self.stdout.write("Seeding Phase 4 leads, quotations, and pipeline deals...")

        # 1. Ensure users exist
        sales_alex, _ = User.objects.get_or_create(
            username='sales_alex',
            defaults={
                'email': 'alex.turner@solarlink-energy.com',
                'first_name': 'Alex',
                'last_name': 'Turner',
                'is_staff': True,
            }
        )
        sales_alex.set_password('solarlink123')
        sales_alex.save()
        UserProfile.objects.update_or_create(
            user=sales_alex,
            defaults={
                'role': UserRole.SALES,
                'company_name': 'SolarLink International Trade Desk',
                'country': 'United Arab Emirates',
                'phone_number': '+971 4 800 7652',
            }
        )

        buyer_tariq, _ = User.objects.get_or_create(
            username='buyer_tariq',
            defaults={
                'email': 'tariq.almansoor@gulfcleanenergy.com',
                'first_name': 'Tariq',
                'last_name': 'Al-Mansoor',
            }
        )
        buyer_tariq.set_password('solarlink123')
        buyer_tariq.save()
        UserProfile.objects.update_or_create(
            user=buyer_tariq,
            defaults={
                'role': UserRole.BUYER,
                'company_name': 'Gulf Clean Energy EPC Ltd.',
                'country': 'Oman',
                'phone_number': '+968 9123 4567',
                'job_title': 'Chief Procurement Director',
            }
        )

        products = list(Product.objects.all())
        p_panel = products[0] if products else None
        p_inverter = products[1] if len(products) > 1 else p_panel
        p_battery = products[2] if len(products) > 2 else p_panel

        # Ensure wishlist item
        if p_panel:
            SavedProduct.objects.get_or_create(user=buyer_tariq, product=p_panel)
        if p_battery:
            SavedProduct.objects.get_or_create(user=buyer_tariq, product=p_battery)

        # 2. Lead 1: 5MW Oman Solar Farm (Stage: QUOTATION_SENT)
        enq1, _ = Enquiry.objects.get_or_create(
            enquiry_number='ENQ-2026-00125',
            defaults={
                'buyer': buyer_tariq,
                'full_name': 'Tariq Al-Mansoor',
                'company_name': 'Gulf Clean Energy EPC Ltd.',
                'email': 'tariq.almansoor@gulfcleanenergy.com',
                'phone': '+968 9123 4567',
                'country': 'Oman',
                'project_name': 'Al-Batinah 5MW Utility Solar Park',
                'project_type': ProjectType.UTILITY,
                'required_capacity': '5 MWp (Utility PV Ground Mount)',
                'project_location': 'Sohar Industrial Zone, Oman',
                'expected_delivery_date': date.today() + timedelta(days=60),
                'shipping_destination': 'Sohar Port, Oman',
                'preferred_incoterm': 'CIF',
                'message': 'Full procurement of Tier-1 TOPCon Bifacial 580W solar panels and 350kW central/string inverters. Delivery scheduled across 8x 40ft HQ containers.',
                'status': EnquiryStatus.QUOTATION_SENT,
                'assigned_sales_rep': sales_alex,
            }
        )
        enq1.status = EnquiryStatus.QUOTATION_SENT
        enq1.assigned_sales_rep = sales_alex
        enq1.save()

        if p_panel:
            EnquiryItem.objects.get_or_create(
                enquiry=enq1,
                product=p_panel,
                defaults={'quantity': 8600, 'target_price_usd': 125.00, 'notes': 'TOPCon Bifacial modules with anti-PID certification'}
            )
        if p_inverter:
            EnquiryItem.objects.get_or_create(
                enquiry=enq1,
                product=p_inverter,
                defaults={'quantity': 15, 'target_price_usd': 8500.00, 'notes': 'Utility grid-tie string inverters with IEC 62109 compliance'}
            )

        # Create Quotation 1
        quote1, created1 = Quotation.objects.get_or_create(
            quote_number='QT-2026-10492',
            defaults={
                'enquiry': enq1,
                'sales_rep': sales_alex,
                'total_amount': 1202500.00,
                'currency': 'USD',
                'incoterm': 'CIF',
                'payment_terms': '30% T/T Advance on Order Confirmation, 70% against Bill of Lading (B/L)',
                'valid_until': date.today() + timedelta(days=25),
                'status': Quotation.QuotationStatus.SENT,
                'sales_rep_notes': 'Official CIF Sohar Port commercial offer. Ocean freight and marine insurance included. Factory inspection certificates provided prior to container loading.',
            }
        )
        if created1 and p_panel:
            QuotationItem.objects.create(
                quotation=quote1,
                product=p_panel,
                quantity=8600,
                unit_price=125.00,
                subtotal=1075000.00,
                specifications_summary=f"{p_panel.brand} 580W TOPCon Bifacial Solar Module"
            )
            if p_inverter:
                QuotationItem.objects.create(
                    quotation=quote1,
                    product=p_inverter,
                    quantity=15,
                    unit_price=8500.00,
                    subtotal=127500.00,
                    specifications_summary=f"{p_inverter.brand} Utility Solar Inverter"
                )

        EnquiryStatusHistory.objects.get_or_create(
            enquiry=enq1,
            from_status=EnquiryStatus.QUOTATION_PREPARED,
            to_status=EnquiryStatus.QUOTATION_SENT,
            defaults={
                'changed_by': sales_alex,
                'comment': 'Commercial Quotation QT-2026-10492 dispatched to buyer for formal review.'
            }
        )

        # 3. Lead 2: Kenya C&I Rooftop (Stage: NEGOTIATION)
        enq2, _ = Enquiry.objects.get_or_create(
            enquiry_number='ENQ-2026-00126',
            defaults={
                'buyer': buyer_tariq,
                'full_name': 'Tariq Al-Mansoor',
                'company_name': 'East Africa Green EPC',
                'email': 'tariq.almansoor@gulfcleanenergy.com',
                'phone': '+254 700 123456',
                'country': 'Kenya',
                'project_name': 'Nairobi Industrial Hub 750kWp C&I Rooftop',
                'project_type': ProjectType.COMMERCIAL,
                'required_capacity': '750 kWp Commercial Rooftop',
                'project_location': 'Industrial Area, Nairobi, Kenya',
                'expected_delivery_date': date.today() + timedelta(days=45),
                'shipping_destination': 'Mombasa Port, Kenya',
                'preferred_incoterm': 'CIF',
                'message': 'Seeking Tier-1 equipment package with rapid dispatch for commercial textile factory rooftop.',
                'status': EnquiryStatus.NEGOTIATION,
                'assigned_sales_rep': sales_alex,
            }
        )
        enq2.status = EnquiryStatus.NEGOTIATION
        enq2.assigned_sales_rep = sales_alex
        enq2.save()

        quote2, created2 = Quotation.objects.get_or_create(
            quote_number='QT-2026-10388',
            defaults={
                'enquiry': enq2,
                'sales_rep': sales_alex,
                'total_amount': 285000.00,
                'currency': 'USD',
                'incoterm': 'CIF',
                'payment_terms': '100% Irrevocable Letter of Credit (LC) at sight',
                'valid_until': date.today() + timedelta(days=15),
                'status': Quotation.QuotationStatus.NEGOTIATING,
                'sales_rep_notes': 'CIF Mombasa Port quote. Includes pre-shipment KEBS PVOC inspection and certificate of conformity.',
                'buyer_feedback': 'Buyer request: Please evaluate if a 4% volume discount can be applied on panel pricing for 100% confirmed LC.',
            }
        )
        if created2 and p_panel:
            QuotationItem.objects.create(
                quotation=quote2,
                product=p_panel,
                quantity=1300,
                unit_price=130.00,
                subtotal=169000.00,
                specifications_summary=f"{p_panel.brand} High-Efficiency Mono PERC / TOPCon"
            )

        # 4. Lead 3: South Africa Microgrid (Stage: APPROVED / WON)
        enq3, _ = Enquiry.objects.get_or_create(
            enquiry_number='ENQ-2026-00127',
            defaults={
                'buyer': buyer_tariq,
                'full_name': 'Tariq Al-Mansoor',
                'company_name': 'Cape Renewable Power',
                'email': 'tariq.almansoor@gulfcleanenergy.com',
                'phone': '+27 21 555 7890',
                'country': 'South Africa',
                'project_name': 'Western Cape 2.5MW Hybrid Microgrid',
                'project_type': ProjectType.OFF_GRID,
                'required_capacity': '2.5 MW Solar + 5 MWh BESS Storage',
                'project_location': 'Worcester, Western Cape, South Africa',
                'expected_delivery_date': date.today() + timedelta(days=90),
                'shipping_destination': 'Cape Town Port, South Africa',
                'preferred_incoterm': 'DDP',
                'message': 'Complete hybrid solar PV + energy storage BESS container integration. High cycle life LiFePO4 chemistry.',
                'status': EnquiryStatus.APPROVED,
                'assigned_sales_rep': sales_alex,
            }
        )
        enq3.status = EnquiryStatus.APPROVED
        enq3.assigned_sales_rep = sales_alex
        enq3.save()

        quote3, created3 = Quotation.objects.get_or_create(
            quote_number='QT-2026-10214',
            defaults={
                'enquiry': enq3,
                'sales_rep': sales_alex,
                'total_amount': 890000.00,
                'currency': 'USD',
                'incoterm': 'DDP',
                'payment_terms': '20% Advance, 50% against Shipping Docs, 30% on Commissioning',
                'valid_until': date.today() + timedelta(days=10),
                'status': Quotation.QuotationStatus.ACCEPTED,
                'sales_rep_notes': 'DDP Cape Town turnkey container delivery. Full customs clearance and NRCS / SABS compliance managed.',
                'buyer_feedback': 'Quotation accepted on agreed milestone schedule. Proceeding with bilateral contract execution.',
            }
        )
        if created3 and p_battery:
            QuotationItem.objects.create(
                quotation=quote3,
                product=p_battery,
                quantity=10,
                unit_price=89000.00,
                subtotal=890000.00,
                specifications_summary=f"{p_battery.brand} Commercial BESS Storage Container"
            )

        # 5. Lead 4: Morocco Solar Pumping (Stage: UNDER_REVIEW)
        enq4, _ = Enquiry.objects.get_or_create(
            enquiry_number='ENQ-2026-00128',
            defaults={
                'buyer': buyer_tariq,
                'full_name': 'Tariq Al-Mansoor',
                'company_name': 'Maghreb Agri-Tech Solutions',
                'email': 'tariq.almansoor@gulfcleanenergy.com',
                'phone': '+212 522 334455',
                'country': 'Morocco',
                'project_name': 'Souss-Massa Solar Water Pumping Project',
                'project_type': ProjectType.AGRICULTURE,
                'required_capacity': '120 Units (5.5kW to 15kW VFD Solar Pumps)',
                'project_location': 'Agadir, Souss-Massa, Morocco',
                'expected_delivery_date': date.today() + timedelta(days=35),
                'shipping_destination': 'Casablanca Port, Morocco',
                'preferred_incoterm': 'CIF',
                'message': 'High-reliability solar pump inverters with MPPT, dry-run protection, and remote 4G telemetry modules.',
                'status': EnquiryStatus.UNDER_REVIEW,
                'assigned_sales_rep': sales_alex,
            }
        )
        enq4.status = EnquiryStatus.UNDER_REVIEW
        enq4.assigned_sales_rep = sales_alex
        enq4.save()

        # 6. Lead 5: UAE Distribution (Stage: ASSIGNED)
        enq5, _ = Enquiry.objects.get_or_create(
            enquiry_number='ENQ-2026-00129',
            defaults={
                'buyer': buyer_tariq,
                'full_name': 'Tariq Al-Mansoor',
                'company_name': 'Gulf Renewable Wholesale LLC',
                'email': 'tariq.almansoor@gulfcleanenergy.com',
                'phone': '+971 50 888 9999',
                'country': 'United Arab Emirates',
                'project_name': 'GCC Regional Distribution Container Supply',
                'project_type': ProjectType.DISTRIBUTION,
                'required_capacity': '4x 40ft HQ Container Assortment',
                'project_location': 'Jebel Ali Free Zone, Dubai, UAE',
                'expected_delivery_date': date.today() + timedelta(days=20),
                'shipping_destination': 'Jebel Ali Port, Dubai',
                'preferred_incoterm': 'CIF',
                'message': 'Wholesale distribution supply agreement for DEWA approved inverters and bifacial solar modules.',
                'status': EnquiryStatus.ASSIGNED,
                'assigned_sales_rep': sales_alex,
            }
        )
        enq5.status = EnquiryStatus.ASSIGNED
        enq5.assigned_sales_rep = sales_alex
        enq5.save()

        self.stdout.write(self.style.SUCCESS(
            "Phase 4 demonstration data seeded successfully!\n"
            "- Sales Executive: sales_alex (solarlink123)\n"
            "- International Buyer: buyer_tariq (solarlink123)\n"
            "- 5 Enquiries across stages: QUOTATION_SENT, NEGOTIATION, APPROVED, UNDER_REVIEW, ASSIGNED\n"
            "- 3 Quotations: QT-2026-10492 (Sent), QT-2026-10388 (Negotiating), QT-2026-10214 (Accepted)\n"
            "- Wishlist & BOM items populated"
        ))
