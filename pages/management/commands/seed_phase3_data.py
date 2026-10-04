from datetime import date
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from pages.models import TeamMember, TeamDepartment, FAQ, FAQCategory
from enquiries.models import Enquiry, EnquiryItem, EnquiryStatusHistory, EnquiryStatus, ProjectType
from catalog.models import Product


class Command(BaseCommand):
    help = 'Seeds team members, FAQs, and realistic sample enquiry for tracking demonstration'

    def handle(self, *args, **options):
        self.stdout.write('Starting Phase 3 data seeding...')

        # ---------------------------------------------------------
        # 1. Team Members
        # ---------------------------------------------------------
        team_data = [
            (
                'Dr. Henrik Weber',
                'Managing Director & Head of International Trade',
                TeamDepartment.MANAGEMENT,
                'henrik.weber@solarlink.io',
                '+49 30 5544 1100',
                '20+ years of executive leadership in renewable energy equipment export across EMEA and APAC markets.',
                'https://linkedin.com/in/henrik-weber',
                1
            ),
            (
                'Alex Vance',
                'Senior Export Sales Executive',
                TeamDepartment.SALES,
                'alex.vance@solarlink.io',
                '+49 30 5544 1122',
                'Specializes in utility-scale PV module procurement, customized Incoterms structuring, and distributor agreements.',
                'https://linkedin.com/in/alex-vance',
                2
            ),
            (
                'Fatima Al-Husseini',
                'Regional Sales Director (Middle East & GCC)',
                TeamDepartment.SALES,
                'fatima.husseini@solarlink.io',
                '+971 4 800 9988',
                'Leads commercial negotiations and government clean energy tender submissions across GCC countries.',
                'https://linkedin.com/in/fatima-husseini',
                3
            ),
            (
                'Jonas Lindholm',
                'Chief Solar Technical & Quality Engineer',
                TeamDepartment.TECHNICAL,
                'jonas.lindholm@solarlink.io',
                '+49 30 5544 1144',
                'Chartered electrical engineer overseeing IEC/UL compliance, factory flash testing audits, and technical datasheet authoring.',
                'https://linkedin.com/in/jonas-lindholm',
                4
            ),
            (
                'Amara Okafor',
                'Director of Maritime Freight & Export Logistics',
                TeamDepartment.EXPORT,
                'amara.okafor@solarlink.io',
                '+44 20 7946 0192',
                'Manages container vessel allocations, heavy-cargo customs clearance, and global port operations.',
                'https://linkedin.com/in/amara-okafor',
                5
            ),
        ]

        for name, desig, dept, email, phone, bio, linkedin, order in team_data:
            TeamMember.objects.get_or_create(
                name=name,
                defaults={
                    'designation': desig,
                    'department': dept,
                    'email': email,
                    'phone': phone,
                    'bio': bio,
                    'social_linkedin': linkedin,
                    'order': order,
                    'is_active': True,
                }
            )

        self.stdout.write(self.style.SUCCESS(f'{len(team_data)} Team Members seeded.'))

        # ---------------------------------------------------------
        # 2. FAQs
        # ---------------------------------------------------------
        faqs_data = [
            (
                FAQCategory.QUOTATIONS,
                'How quickly can I receive a formal commercial quotation (RFQ)?',
                'Our international sales engineering desk responds to all standard project enquiries within 24 to 48 business hours with an itemized commercial quotation, estimated ocean freight, and confirmed lead time.',
                1
            ),
            (
                FAQCategory.QUOTATIONS,
                'What is the minimum order quantity (MOQ) for export pricing?',
                'For solar PV panels, our standard export MOQ is 1x 20ft container (approx. 280 kW - 340 kW depending on module size). For hybrid inverters and lithium storage batteries, modular orders starting from 10 to 20 units qualify for export tier pricing.',
                2
            ),
            (
                FAQCategory.SHIPPING,
                'Which Incoterms does SolarLink support for international shipments?',
                'We regularly support FOB (Port of Origin), CIF (Destination Seaport), CFR, and DDP (Delivered Duty Paid directly to project jobsite). We provide complete container ocean transport, marine insurance, and customs documentation.',
                3
            ),
            (
                FAQCategory.SHIPPING,
                'How are solar PV modules and inverters packaged for ocean transport?',
                'All equipment is packed in heavy-duty export reinforced wooden crates with internal vertical corner protectors, moisture-barrier vacuum poly film, and exterior tamper-evident tilt sensors to guarantee zero micro-fracturing in transit.',
                4
            ),
            (
                FAQCategory.TECHNICAL,
                'Are individual module flash test reports provided prior to shipping?',
                'Yes. Every container shipment includes a digitized factory flash test data sheet recording STC peak power (Pmax), open circuit voltage (Voc), short circuit current (Isc), and fill factor (FF) for every serial-numbered module.',
                5
            ),
            (
                FAQCategory.WARRANTY,
                'What warranty guarantees accompany tier-1 PV modules?',
                'Our certified PV modules carry a 12-to-15 year manufacturer materials and workmanship warranty, alongside a 25-to-30 year linear power performance warranty guaranteeing minimum 85% to 87.4% nominal power output at year 30.',
                6
            ),
            (
                FAQCategory.GENERAL,
                'Can international buyers track their enquiry status in real time?',
                'Yes! Every submitted enquiry receives an automated tracking number (e.g. ENQ-2026-00125). Buyers can monitor their review progress, sales executive assignment, and quotation status directly on our public tracking portal or personal dashboard.',
                7
            ),
        ]

        for cat, q, a, order in faqs_data:
            FAQ.objects.get_or_create(
                question=q,
                defaults={
                    'category': cat,
                    'answer': a,
                    'order': order,
                    'is_published': True,
                }
            )

        self.stdout.write(self.style.SUCCESS(f'{len(faqs_data)} FAQs seeded.'))

        # ---------------------------------------------------------
        # 3. Demonstration Enquiry (ENQ-2026-00125)
        # ---------------------------------------------------------
        sales_user = User.objects.filter(username='sales_alex').first()
        buyer_user = User.objects.filter(username='buyer_tariq').first()
        panel_product = Product.objects.filter(product_code='SL-PV-550BF').first()
        inverter_product = Product.objects.filter(product_code='SL-INV-50KS').first()

        sample_enq, created = Enquiry.objects.get_or_create(
            enquiry_number='ENQ-2026-00125',
            defaults={
                'buyer': buyer_user,
                'full_name': 'Tariq Al-Mansoor',
                'company_name': 'Gulf Renewable Infrastructure LLC',
                'email': 'tariq@gulfenergy.ae',
                'phone': '+971 4 800 5544',
                'country': 'United Arab Emirates',
                'project_name': '50 MW Al-Dhafra Commercial Solar Farm Extension',
                'project_type': ProjectType.UTILITY,
                'required_capacity': '50 MWp (Approx. 90,000 Modules)',
                'project_location': 'Abu Dhabi, United Arab Emirates',
                'expected_delivery_date': date(2026, 12, 1),
                'shipping_destination': 'Jebel Ali Container Port, Dubai',
                'preferred_incoterm': 'CIF',
                'message': (
                    'Requesting turnkey containerized quotation for 50 MW bifacial dual-glass modules '
                    'and 50kW commercial string inverters. Must include TÜV Rheinland IEC 61215 certification, '
                    'SABER conformity documents, and flash test calibration data.'
                ),
                'status': EnquiryStatus.QUOTATION_SENT,
                'assigned_sales_rep': sales_user,
            }
        )

        if created and panel_product:
            EnquiryItem.objects.create(
                enquiry=sample_enq,
                product=panel_product,
                quantity=90900,
                target_price_usd=0.14,
                notes='HeliosPro 550W Bifacial Dual Glass Modules'
            )
            if inverter_product:
                EnquiryItem.objects.create(
                    enquiry=sample_enq,
                    product=inverter_product,
                    quantity=800,
                    target_price_usd=1650.00,
                    notes='VoltCore 50kW 4-MPPT String Inverters'
                )

            # Audit History
            EnquiryStatusHistory.objects.create(
                enquiry=sample_enq,
                from_status='SUBMITTED',
                to_status=EnquiryStatus.REQUESTED,
                changed_by=buyer_user,
                comment='Initial 50 MW enquiry submitted via SolarLink public web portal.'
            )
            EnquiryStatusHistory.objects.create(
                enquiry=sample_enq,
                from_status=EnquiryStatus.REQUESTED,
                to_status=EnquiryStatus.ASSIGNED,
                changed_by=sales_user,
                comment='Enquiry assigned to Senior Sales Executive Alex Vance.'
            )
            EnquiryStatusHistory.objects.create(
                enquiry=sample_enq,
                from_status=EnquiryStatus.ASSIGNED,
                to_status=EnquiryStatus.UNDER_REVIEW,
                changed_by=sales_user,
                comment='Reviewed technical requirements, shipping destination (Jebel Ali), and IEC standards.'
            )
            EnquiryStatusHistory.objects.create(
                enquiry=sample_enq,
                from_status=EnquiryStatus.UNDER_REVIEW,
                to_status=EnquiryStatus.QUOTATION_PREPARED,
                changed_by=sales_user,
                comment='Commercial quotation prepared with CIF Jebel Ali terms and container packaging.'
            )
            EnquiryStatusHistory.objects.create(
                enquiry=sample_enq,
                from_status=EnquiryStatus.QUOTATION_PREPARED,
                to_status=EnquiryStatus.QUOTATION_SENT,
                changed_by=sales_user,
                comment='Official formal quotation sent to buyer Tariq Al-Mansoor for review.'
            )

        self.stdout.write(self.style.SUCCESS('Demonstration Enquiry ENQ-2026-00125 and status history seeded.'))
        self.stdout.write(self.style.SUCCESS('Phase 3 Data Seeding Completed Successfully!'))
