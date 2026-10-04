from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile, UserRole, SavedProduct
from catalog.models import Category, Product, SpecificationAttribute, ProductSpecification
from certifications.models import ComplianceStandard, Certification, LabReport, Warranty
from exports.models import Country, ShippingTerm, ExportDocument
from pages.models import TeamMember, FAQ
from enquiries.models import Enquiry, EnquiryItem, EnquiryStatus, ProjectType, Quotation, QuotationItem, EnquiryStatusHistory


class Command(BaseCommand):
    help = 'Master seed command: Populates the complete SolarLink B2B platform with demonstration data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("=== SolarLink Master Database Seeder ==="))

        # ----------------------------------------------------
        # 1. USERS & ROLES
        # ----------------------------------------------------
        self.stdout.write("1. Seeding Users & RBAC Profiles...")
        
        # Admin
        admin_user, _ = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@solarlink-energy.com', 'first_name': 'Chief', 'last_name': 'Administrator', 'is_staff': True, 'is_superuser': True}
        )
        admin_user.set_password('admin123')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        admin_profile = admin_user.profile
        admin_profile.role = UserRole.ADMIN
        admin_profile.company_name = 'SolarLink Global Operations HQ'
        admin_profile.country = 'Germany'
        admin_profile.phone = '+49 30 55441122'
        admin_profile.save()

        # Sales Rep
        sales_alex, _ = User.objects.get_or_create(
            username='sales_alex',
            defaults={'email': 'alex.turner@solarlink-energy.com', 'first_name': 'Alex', 'last_name': 'Turner', 'is_staff': True}
        )
        sales_alex.set_password('solarlink123')
        sales_alex.is_staff = True
        sales_alex.save()
        sales_profile = sales_alex.profile
        sales_profile.role = UserRole.SALES
        sales_profile.company_name = 'SolarLink International Trade Desk'
        sales_profile.country = 'United Arab Emirates'
        sales_profile.phone = '+971 4 800 7652'
        sales_profile.save()

        # Buyer 1: Tariq (Oman)
        buyer_tariq, _ = User.objects.get_or_create(
            username='buyer_tariq',
            defaults={'email': 'tariq.almansoor@gulfcleanenergy.com', 'first_name': 'Tariq', 'last_name': 'Al-Mansoor'}
        )
        buyer_tariq.set_password('solarlink123')
        buyer_tariq.save()
        tariq_profile = buyer_tariq.profile
        tariq_profile.role = UserRole.BUYER
        tariq_profile.company_name = 'Gulf Clean Energy EPC Ltd.'
        tariq_profile.country = 'Oman'
        tariq_profile.phone = '+968 9123 4567'
        tariq_profile.job_title = 'Chief Procurement Director'
        tariq_profile.save()

        # Buyer 2: Hassan (Egypt)
        buyer_hassan, _ = User.objects.get_or_create(
            username='buyer_hassan',
            defaults={'email': 'hassan.kamal@cairosolar.com', 'first_name': 'Hassan', 'last_name': 'Kamal'}
        )
        buyer_hassan.set_password('solarlink123')
        buyer_hassan.save()
        hassan_profile = buyer_hassan.profile
        hassan_profile.role = UserRole.BUYER
        hassan_profile.company_name = 'Cairo Solar Solutions Co.'
        hassan_profile.country = 'Egypt'
        hassan_profile.phone = '+20 100 1234567'
        hassan_profile.job_title = 'Technical Project Manager'
        hassan_profile.save()

        # ----------------------------------------------------
        # 2. CATEGORIES & WARRANTIES
        # ----------------------------------------------------
        self.stdout.write("2. Seeding Categories & Warranties...")
        cat_panels, _ = Category.objects.get_or_create(slug='solar-panels', defaults={'name': 'Solar PV Modules', 'description': 'Monocrystalline, TOPCon, and Bifacial high-efficiency PV modules.'})
        cat_inverters, _ = Category.objects.get_or_create(slug='solar-inverters', defaults={'name': 'Solar Inverters', 'description': 'String, central, and hybrid solar inverters with smart energy management.'})
        cat_batteries, _ = Category.objects.get_or_create(slug='solar-batteries', defaults={'name': 'Lithium Energy Storage', 'description': 'LiFePO4 energy storage systems (BESS) for C&I, residential, and microgrid applications.'})
        cat_mounting, _ = Category.objects.get_or_create(slug='solar-mounting-systems', defaults={'name': 'Mounting Systems & Trackers', 'description': 'Ground mount, rooftop aluminum rails, and solar tracker systems.'})
        cat_pumps, _ = Category.objects.get_or_create(slug='solar-pumps', defaults={'name': 'Solar Water Pumps', 'description': 'Solar agricultural submersible pumps and MPPT VFD controller packages.'})

        # ----------------------------------------------------
        # 3. SPECIFICATION ATTRIBUTES & PRODUCTS
        # ----------------------------------------------------
        self.stdout.write("3. Seeding Equipment Catalog & EAV Specs...")
        attr_power, _ = SpecificationAttribute.objects.get_or_create(name='Max Rated Power (Pmax)', defaults={'unit': 'Wp', 'description': 'Peak nominal DC wattage'})
        attr_eff, _ = SpecificationAttribute.objects.get_or_create(name='Module Efficiency', defaults={'unit': '%', 'description': 'Conversion efficiency percentage'})
        attr_cell, _ = SpecificationAttribute.objects.get_or_create(name='Cell Technology', defaults={'unit': '', 'description': 'Photovoltaic semiconductor technology'})
        attr_volt, _ = SpecificationAttribute.objects.get_or_create(name='Max System Voltage', defaults={'unit': 'V', 'description': 'Maximum DC operating voltage'})
        attr_cycle, _ = SpecificationAttribute.objects.get_or_create(name='Cycle Life', defaults={'unit': 'Cycles', 'description': 'Battery charge/discharge cycle lifetime'})

        # Product 1: 580W TOPCon Panel
        p1, _ = Product.objects.get_or_create(
            slug='solarlink-580w-topcon-bifacial',
            defaults={
                'name': 'SolarLink Pro 580W N-Type TOPCon Bifacial Module',
                'category': cat_panels,
                'brand': 'SolarLink Pro',
                'product_code': 'SL-580-TC',
                'model_number': 'SL-M10-580B',
                'technology_type': 'N-Type TOPCon 16BB',
                'power_watts': 580,
                'short_description': 'Tier-1 dual-glass bifacial solar panel with 22.5% module efficiency and superior low-light generation.',
                'full_description': 'Manufactured using SMBB half-cut cell technology with anti-PID and anti-LID degradation. Double glass construction ensures high mechanical load resistance up to 5400 Pa snow load and 2400 Pa wind load.',
            }
        )
        ProductSpecification.objects.get_or_create(product=p1, attribute=attr_power, defaults={'value': '580'})
        ProductSpecification.objects.get_or_create(product=p1, attribute=attr_eff, defaults={'value': '22.5'})
        ProductSpecification.objects.get_or_create(product=p1, attribute=attr_cell, defaults={'value': 'N-Type TOPCon 16BB'})
        Warranty.objects.get_or_create(
            product=p1,
            defaults={
                'product_warranty_years': 12,
                'performance_warranty_years': 25,
                'coverage_details': '12-year materials & workmanship, 25-year linear power warranty at 84.8% output.',
            }
        )

        # Product 2: 125kW C&I String Inverter
        p2, _ = Product.objects.get_or_create(
            slug='solarlink-125kw-three-phase-string-inverter',
            defaults={
                'name': 'SolarLink Ultra 125kW Three-Phase Grid Inverter',
                'category': cat_inverters,
                'brand': 'SolarLink Ultra',
                'product_code': 'SL-INV-125K',
                'model_number': 'SL-125K-TL',
                'technology_type': '3-Phase Grid-Tied Inverter',
                'power_watts': 125000,
                'short_description': 'High-performance 12 MPPT commercial grid-tied inverter with integrated AFCI and Type II AC/DC surge protection.',
                'full_description': 'Designed for large-scale industrial rooftops and commercial ground arrays. Features maximum efficiency of 98.8%, smart I-V curve scanning, and integrated string monitoring.',
            }
        )
        ProductSpecification.objects.get_or_create(product=p2, attribute=attr_power, defaults={'value': '125000'})
        ProductSpecification.objects.get_or_create(product=p2, attribute=attr_volt, defaults={'value': '1100'})
        Warranty.objects.get_or_create(
            product=p2,
            defaults={
                'product_warranty_years': 10,
                'performance_warranty_years': 10,
                'coverage_details': '10-year manufacturer replacement warranty with optional 15-year extension.',
            }
        )

        # Product 3: 215kWh C&I Battery BESS
        p3, _ = Product.objects.get_or_create(
            slug='solarlink-215kwh-liquid-cooled-bess-container',
            defaults={
                'name': 'SolarLink Megapack 215kWh Liquid-Cooled BESS Storage',
                'category': cat_batteries,
                'brand': 'SolarLink Megapack',
                'product_code': 'SL-BESS-215',
                'model_number': 'SL-ESS-215K-L',
                'technology_type': 'LiFePO4 Liquid-Cooled BESS',
                'power_watts': 100000,
                'short_description': 'Outdoor IP55 liquid-cooled LiFePO4 battery energy storage cabinet for industrial peak shaving and solar microgrids.',
                'full_description': 'All-in-one outdoor energy storage system integrating CATL LiFePO4 cells, BMS, liquid cooling thermal management, and aerosol fire suppression.',
            }
        )
        ProductSpecification.objects.get_or_create(product=p3, attribute=attr_cycle, defaults={'value': '6500'})
        Warranty.objects.get_or_create(
            product=p3,
            defaults={
                'product_warranty_years': 10,
                'performance_warranty_years': 10,
                'coverage_details': '10-year capacity retention warranty or 6000 cycles at 80% DoD.',
            }
        )

        # Product 4: 15kW Solar Agricultural Pump VFD
        p4, _ = Product.objects.get_or_create(
            slug='solarlink-15kw-solar-pumping-inverter-vfd',
            defaults={
                'name': 'SolarLink AquaDrive 15kW Solar Pumping Inverter',
                'category': cat_pumps,
                'brand': 'SolarLink AquaDrive',
                'product_code': 'SL-PUMP-15K',
                'model_number': 'SL-AD-150',
                'technology_type': 'MPPT Solar VFD Controller',
                'power_watts': 15000,
                'short_description': 'IP65 waterproof solar pump inverter with smart dynamic MPPT, dry run sensor, and automated solar/grid bypass.',
                'full_description': 'Heavy-duty agricultural inverter designed for harsh outdoor desert environments. Compatible with deep-well submersible pumps and surface irrigation systems.',
            }
        )
        Warranty.objects.get_or_create(
            product=p4,
            defaults={
                'product_warranty_years': 5,
                'performance_warranty_years': 5,
                'coverage_details': '5-year manufacturer replacement warranty with IP65 outdoor protection.',
            }
        )

        # ----------------------------------------------------
        # 4. COMPLIANCE STANDARDS & CERTIFICATIONS
        # ----------------------------------------------------
        self.stdout.write("4. Seeding Compliance Standards & Certificates...")
        std1, _ = ComplianceStandard.objects.get_or_create(name='IEC 61215', defaults={'issuing_body': 'TÜV Rheinland', 'description': 'Terrestrial PV module design qualification and type approval.'})
        std2, _ = ComplianceStandard.objects.get_or_create(name='IEC 61730', defaults={'issuing_body': 'TÜV Rheinland', 'description': 'Photovoltaic module safety qualification.'})
        std3, _ = ComplianceStandard.objects.get_or_create(name='IEC 62109', defaults={'issuing_body': 'TÜV SÜD', 'description': 'Safety of power converters for use in photovoltaic power systems.'})

        cert1, _ = Certification.objects.get_or_create(
            certificate_number='TUV-PV-2026-9042',
            defaults={
                'standard': std1,
                'title': 'TUV Rheinland IEC 61215:2021 Type Approval',
                'issuing_organization': 'TÜV Rheinland Germany',
                'issue_date': date(2025, 1, 15),
                'expiry_date': date(2030, 1, 15),
                'is_valid': True,
            }
        )
        cert1.products.add(p1)

        # ----------------------------------------------------
        # 5. EXPORT COUNTRIES & LOGISTICS
        # ----------------------------------------------------
        self.stdout.write("5. Seeding Export Logistics & Incoterms...")
        c_oman, _ = Country.objects.get_or_create(code='OM', defaults={'name': 'Oman', 'region': 'Middle East & GCC', 'flag_emoji': '🇴🇲', 'primary_ports': 'Sohar Port, Port Sultan Qaboos'})
        c_uae, _ = Country.objects.get_or_create(code='AE', defaults={'name': 'United Arab Emirates', 'region': 'Middle East & GCC', 'flag_emoji': '🇦🇪', 'primary_ports': 'Jebel Ali Port, Dubai'})
        c_kenya, _ = Country.objects.get_or_create(code='KE', defaults={'name': 'Kenya', 'region': 'East Africa', 'flag_emoji': '🇰🇪', 'primary_ports': 'Mombasa Port'})
        c_sa, _ = Country.objects.get_or_create(code='ZA', defaults={'name': 'South Africa', 'region': 'Southern Africa', 'flag_emoji': '🇿🇦', 'primary_ports': 'Cape Town Port, Durban Port'})
        c_morocco, _ = Country.objects.get_or_create(code='MA', defaults={'name': 'Morocco', 'region': 'North Africa', 'flag_emoji': '🇲🇦', 'primary_ports': 'Casablanca Port, Tanger Med'})

        ShippingTerm.objects.get_or_create(incoterm='CIF', defaults={'title': 'Cost, Insurance & Freight', 'buyer_responsibility': 'Customs duties, import taxes, unloading at destination port.', 'seller_responsibility': 'Ocean freight, marine cargo insurance, export customs.', 'risk_transfer_point': 'Ship rail at port of origin', 'is_recommended': True})
        ShippingTerm.objects.get_or_create(incoterm='FOB', defaults={'title': 'Free On Board', 'buyer_responsibility': 'Ocean freight, marine insurance, import customs, and destination delivery.', 'seller_responsibility': 'Export packaging, inland transport to origin seaport, vessel loading.', 'risk_transfer_point': 'Vessel deck at origin loading port'})
        ShippingTerm.objects.get_or_create(incoterm='DDP', defaults={'title': 'Delivered Duty Paid', 'buyer_responsibility': 'Unloading at destination factory/project site.', 'seller_responsibility': 'Full turnkey freight, import customs tariffs, and door-to-door transit.', 'risk_transfer_point': 'Buyer project site'})

        # ----------------------------------------------------
        # 6. ENQUIRIES & DEALS ACROSS PIPELINE
        # ----------------------------------------------------
        self.stdout.write("6. Seeding Project RFQs across 7 Pipeline Stages...")
        
        # Deal 1: Won / Approved
        e1, _ = Enquiry.objects.get_or_create(
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
                'message': 'Tier-1 TOPCon Bifacial 580W solar modules and three-phase utility string inverters. Scheduled container delivery.',
                'status': EnquiryStatus.APPROVED,
                'assigned_sales_rep': sales_alex,
            }
        )
        e1.status = EnquiryStatus.APPROVED
        e1.assigned_sales_rep = sales_alex
        e1.save()

        EnquiryItem.objects.get_or_create(enquiry=e1, product=p1, defaults={'quantity': 8600, 'target_price_usd': 125.00})
        EnquiryItem.objects.get_or_create(enquiry=e1, product=p2, defaults={'quantity': 15, 'target_price_usd': 8500.00})

        q1, created_q1 = Quotation.objects.get_or_create(
            quote_number='QT-2026-10492',
            defaults={
                'enquiry': e1,
                'sales_rep': sales_alex,
                'total_amount': 1202500.00,
                'currency': 'USD',
                'incoterm': 'CIF',
                'payment_terms': '30% T/T Advance, 70% against B/L',
                'valid_until': date.today() + timedelta(days=30),
                'status': Quotation.QuotationStatus.ACCEPTED,
                'sales_rep_notes': 'CIF Sohar Port commercial offer. Verified TUV certificates and pre-shipment container seal inspection included.',
                'buyer_feedback': 'Offer accepted. Bilateral EPC contract executed.',
            }
        )
        if created_q1:
            QuotationItem.objects.create(quotation=q1, product=p1, quantity=8600, unit_price=125.00, subtotal=1075000.00, specifications_summary='580W TOPCon Modules')
            QuotationItem.objects.create(quotation=q1, product=p2, quantity=15, unit_price=8500.00, subtotal=127500.00, specifications_summary='125kW String Inverters')

        # Deal 2: Negotiation
        e2, _ = Enquiry.objects.get_or_create(
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
                'project_location': 'Nairobi Industrial Area, Kenya',
                'expected_delivery_date': date.today() + timedelta(days=45),
                'shipping_destination': 'Mombasa Port, Kenya',
                'preferred_incoterm': 'CIF',
                'message': 'Seeking commercial rooftop package with rapid shipment for textile factory.',
                'status': EnquiryStatus.NEGOTIATION,
                'assigned_sales_rep': sales_alex,
            }
        )
        e2.status = EnquiryStatus.NEGOTIATION
        e2.assigned_sales_rep = sales_alex
        e2.save()

        q2, created_q2 = Quotation.objects.get_or_create(
            quote_number='QT-2026-10388',
            defaults={
                'enquiry': e2,
                'sales_rep': sales_alex,
                'total_amount': 285000.00,
                'currency': 'USD',
                'incoterm': 'CIF',
                'payment_terms': '100% Irrevocable LC at sight',
                'valid_until': date.today() + timedelta(days=15),
                'status': Quotation.QuotationStatus.NEGOTIATING,
                'sales_rep_notes': 'CIF Mombasa quote with pre-shipment KEBS PVOC inspection included.',
                'buyer_feedback': 'Buyer request: Evaluate 4% volume discount for 100% confirmed LC at sight.',
            }
        )
        if created_q2:
            QuotationItem.objects.create(quotation=q2, product=p1, quantity=1300, unit_price=130.00, subtotal=169000.00, specifications_summary='580W TOPCon Modules')

        # Deal 3: Quotation Sent
        e3, _ = Enquiry.objects.get_or_create(
            enquiry_number='ENQ-2026-00127',
            defaults={
                'buyer': buyer_hassan,
                'full_name': 'Hassan Kamal',
                'company_name': 'Cairo Solar Solutions Co.',
                'email': 'hassan.kamal@cairosolar.com',
                'phone': '+20 100 1234567',
                'country': 'Egypt',
                'project_name': 'Suez Canal Freezone 1.2MW C&I Solar Array',
                'project_type': ProjectType.COMMERCIAL,
                'required_capacity': '1.2 MWp Rooftop System',
                'project_location': 'Ismailia / Suez, Egypt',
                'expected_delivery_date': date.today() + timedelta(days=50),
                'shipping_destination': 'Port Said / Alexandria Port, Egypt',
                'preferred_incoterm': 'CIF',
                'message': 'Tier-1 panels and smart string inverters for logistics warehouse complex.',
                'status': EnquiryStatus.QUOTATION_SENT,
                'assigned_sales_rep': sales_alex,
            }
        )
        e3.status = EnquiryStatus.QUOTATION_SENT
        e3.assigned_sales_rep = sales_alex
        e3.save()

        q3, created_q3 = Quotation.objects.get_or_create(
            quote_number='QT-2026-10512',
            defaults={
                'enquiry': e3,
                'sales_rep': sales_alex,
                'total_amount': 345000.00,
                'currency': 'USD',
                'incoterm': 'CIF',
                'payment_terms': '30% T/T Advance, 70% against B/L',
                'valid_until': date.today() + timedelta(days=28),
                'status': Quotation.QuotationStatus.SENT,
                'sales_rep_notes': 'CIF Port Said quotation with embassy notarized COO and EUR.1 movement certificates.',
            }
        )
        if created_q3:
            QuotationItem.objects.create(quotation=q3, product=p1, quantity=2100, unit_price=125.00, subtotal=262500.00, specifications_summary='580W TOPCon Modules')

        # Deal 4: Under Review
        e4, _ = Enquiry.objects.get_or_create(
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
                'required_capacity': '120 Units (15kW VFD Solar Pumps)',
                'project_location': 'Agadir, Morocco',
                'expected_delivery_date': date.today() + timedelta(days=35),
                'shipping_destination': 'Casablanca Port, Morocco',
                'preferred_incoterm': 'CIF',
                'message': 'Submersible agricultural solar water pumps with remote 4G telemetry modules.',
                'status': EnquiryStatus.UNDER_REVIEW,
                'assigned_sales_rep': sales_alex,
            }
        )
        e4.status = EnquiryStatus.UNDER_REVIEW
        e4.assigned_sales_rep = sales_alex
        e4.save()

        # Deal 5: Assigned
        e5, _ = Enquiry.objects.get_or_create(
            enquiry_number='ENQ-2026-00129',
            defaults={
                'buyer': buyer_tariq,
                'full_name': 'Tariq Al-Mansoor',
                'company_name': 'Gulf Renewable Wholesale LLC',
                'email': 'tariq.almansoor@gulfcleanenergy.com',
                'phone': '+971 50 888 9999',
                'country': 'United Arab Emirates',
                'project_name': 'GCC Regional Distribution Container Assortment',
                'project_type': ProjectType.DISTRIBUTION,
                'required_capacity': '4x 40ft HQ Containers',
                'project_location': 'Jebel Ali Free Zone, Dubai, UAE',
                'expected_delivery_date': date.today() + timedelta(days=20),
                'shipping_destination': 'Jebel Ali Port, Dubai',
                'preferred_incoterm': 'CIF',
                'message': 'Wholesale distribution agreement for DEWA approved hybrid inverters and batteries.',
                'status': EnquiryStatus.ASSIGNED,
                'assigned_sales_rep': sales_alex,
            }
        )
        e5.status = EnquiryStatus.ASSIGNED
        e5.assigned_sales_rep = sales_alex
        e5.save()

        # Wishlist items
        SavedProduct.objects.get_or_create(user=buyer_tariq, product=p1)
        SavedProduct.objects.get_or_create(user=buyer_tariq, product=p3)
        SavedProduct.objects.get_or_create(user=buyer_hassan, product=p2)

        self.stdout.write(self.style.SUCCESS(
            "\nSolarLink Master Database Seed COMPLETE!\n"
            "--------------------------------------------------\n"
            "Roles & Credentials:\n"
            "  - Admin: admin / admin123  -> http://127.0.0.1:8000/dashboard/admin-portal/\n"
            "  - Sales: sales_alex / solarlink123 -> http://127.0.0.1:8000/sales/dashboard/\n"
            "  - Buyer: buyer_tariq / solarlink123 -> http://127.0.0.1:8000/dashboard/\n"
            "  - Buyer: buyer_hassan / solarlink123 -> http://127.0.0.1:8000/dashboard/\n"
            "Data Summary:\n"
            "  - 4 Equipment Products across 5 Categories with EAV Attributes\n"
            "  - 5 Project RFQs across 7 Deal Pipeline Stages\n"
            "  - 3 Commercial Quotations ($1,832,500 total value)\n"
            "  - 5x Instant CSV Exports ready at /dashboard/admin-portal/\n"
            "--------------------------------------------------"
        ))
