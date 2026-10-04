from datetime import date
from django.core.management.base import BaseCommand
from catalog.models import Category, Product, SpecificationAttribute, ProductSpecification
from certifications.models import ComplianceStandard, StandardCategory, Certification, LabReport, Warranty
from exports.models import Country, ShippingTerm, ExportDocument, IncotermCode


class Command(BaseCommand):
    help = 'Seeds industry-realistic catalog products, EAV specifications, compliance standards, and export terms'

    def handle(self, *args, **options):
        self.stdout.write('Starting Phase 2 data seeding...')

        # ---------------------------------------------------------
        # 1. Categories
        # ---------------------------------------------------------
        cat_panels, _ = Category.objects.get_or_create(
            slug='solar-panels',
            defaults={
                'name': 'Solar PV Modules',
                'icon_name': 'sun',
                'description': 'High-efficiency monocrystalline PERC, TOPCon, and bifacial solar photovoltaic modules.',
                'sort_order': 1,
            }
        )

        cat_inverters, _ = Category.objects.get_or_create(
            slug='solar-inverters',
            defaults={
                'name': 'Solar Inverters',
                'icon_name': 'zap',
                'description': 'Commercial string inverters, utility central inverters, and hybrid battery storage inverters.',
                'sort_order': 2,
            }
        )

        cat_batteries, _ = Category.objects.get_or_create(
            slug='solar-batteries',
            defaults={
                'name': 'Lithium Energy Storage',
                'icon_name': 'battery',
                'description': 'High-voltage rack-mount and modular LiFePO4 commercial energy storage systems (BESS).',
                'sort_order': 3,
            }
        )

        cat_mounting, _ = Category.objects.get_or_create(
            slug='solar-mounting-systems',
            defaults={
                'name': 'Mounting Systems & Trackers',
                'icon_name': 'tool',
                'description': 'Anodized aluminum ground-mount racking, rooftop ballasted structures, and single-axis trackers.',
                'sort_order': 4,
            }
        )

        cat_pumps, _ = Category.objects.get_or_create(
            slug='solar-pumps',
            defaults={
                'name': 'Solar Water Pumps',
                'icon_name': 'droplet',
                'description': 'Brushless DC submersible borehole pumps and solar surface irrigation systems.',
                'sort_order': 5,
            }
        )

        self.stdout.write(self.style.SUCCESS('Categories created successfully.'))

        # ---------------------------------------------------------
        # 2. Specification Attributes
        # ---------------------------------------------------------
        specs_data = [
            ('Rated Power Output', 'W', 'Nominal power under Standard Test Conditions (STC)'),
            ('Maximum Efficiency', '%', 'Module or system conversion efficiency'),
            ('Cell Technology', '', 'Semiconductor wafer type and cell architecture'),
            ('Open Circuit Voltage (Voc)', 'V', 'Maximum voltage under zero current'),
            ('Short Circuit Current (Isc)', 'A', 'Current produced when the circuit is shorted'),
            ('Max Power Voltage (Vmp)', 'V', 'Operating voltage at peak power point'),
            ('Max Power Current (Imp)', 'A', 'Operating current at peak power point'),
            ('Dimensions', 'mm', 'Physical length x width x frame height'),
            ('Weight', 'kg', 'Gross physical product weight'),
            ('Operating Temperature', '°C', 'Safe operating temperature spectrum'),
            ('Inverter Max DC Input Voltage', 'V', 'Maximum permissible DC array input voltage'),
            ('MPPT Voltage Range', 'V', 'Operating voltage range for maximum power point tracker'),
            ('Number of MPPT Trackers', '', 'Dedicated independent maximum power tracking circuits'),
            ('Inverter Max AC Output', 'kW', 'Continuous nominal AC electrical output power'),
            ('Battery Nominal Capacity', 'kWh', 'Gross energy storage capacity rating'),
            ('Battery Usable Capacity', 'kWh', 'Net usable capacity at 90% Depth of Discharge'),
            ('Battery Chemistry', '', 'Electrochemical cell structure (e.g. Lithium Iron Phosphate)'),
            ('Battery Cycle Life', 'Cycles', 'Cycle count to 80% original retention capacity'),
            ('Ingress Protection', 'IP', 'Dust, solid, and moisture sealing rating (e.g. IP65, IP68)'),
            ('Product Warranty Period', 'Years', 'Manufacturer physical materials and build guarantee'),
        ]

        attr_map = {}
        for name, unit, desc in specs_data:
            attr, _ = SpecificationAttribute.objects.get_or_create(
                name=name,
                defaults={'unit': unit, 'description': desc}
            )
            attr_map[name] = attr

        self.stdout.write(self.style.SUCCESS(f'{len(attr_map)} Technical Attributes initialized.'))

        # ---------------------------------------------------------
        # 3. Products
        # ---------------------------------------------------------
        # Product 1: HeliosPro 550W
        p1, _ = Product.objects.get_or_create(
            product_code='SL-PV-550BF',
            defaults={
                'name': 'HeliosPro 550W Tier-1 Bifacial Dual-Glass PV Module',
                'category': cat_panels,
                'brand': 'Helios Solar',
                'model_number': 'HP-M550-BDG',
                'technology_type': 'Bifacial Mono PERC',
                'power_watts': 550,
                'short_description': 'Tier-1 144-half-cell bifacial dual-glass module delivering up to 25% additional rear-side energy yield.',
                'full_description': (
                    'The HeliosPro 550W Bifacial Dual-Glass Module is engineered for high-yield utility and large commercial installations. '
                    'Featuring advanced 182mm 144-half-cut monocrystalline PERC cells enclosed between 2.0mm heat-strengthened glass panels, '
                    'it minimizes micro-cracking and PID degradation while generating up to 25% bifacial gain from ground albedo reflection.'
                ),
                'is_featured': True,
                'in_stock': True,
            }
        )

        p1_specs = [
            ('Rated Power Output', '550'),
            ('Maximum Efficiency', '21.3'),
            ('Cell Technology', '182mm 144-Half-Cell Monocrystalline PERC'),
            ('Open Circuit Voltage (Voc)', '49.8'),
            ('Short Circuit Current (Isc)', '13.98'),
            ('Max Power Voltage (Vmp)', '41.95'),
            ('Max Power Current (Imp)', '13.12'),
            ('Dimensions', '2278 x 1134 x 35'),
            ('Weight', '28.5'),
            ('Operating Temperature', '-40 to +85'),
            ('Ingress Protection', 'IP68 Junction Box'),
            ('Product Warranty Period', '12'),
        ]
        for idx, (attr_name, val) in enumerate(p1_specs, start=1):
            if attr_name in attr_map:
                ProductSpecification.objects.update_or_create(
                    product=p1,
                    attribute=attr_map[attr_name],
                    defaults={'value': val, 'order': idx}
                )

        # Product 2: AstraMax 670W
        p2, _ = Product.objects.get_or_create(
            product_code='SL-PV-670N',
            defaults={
                'name': 'AstraMax 670W Ultra-High Output Utility PV Module',
                'category': cat_panels,
                'brand': 'Astra Solar',
                'model_number': 'AM-670-TOPCON',
                'technology_type': 'N-Type TOPCon Bifacial',
                'power_watts': 670,
                'short_description': 'Ultra-high power 210mm G12 cell architecture with N-Type TOPCon technology and 22.8% module efficiency.',
                'full_description': (
                    'Designed specifically for multi-megawatt utility scale solar farms, the AstraMax 670W leverages cutting-edge N-Type TOPCon cells. '
                    'With lower temperature coefficients (-0.30%/°C) and virtually zero Light Induced Degradation (LID), it ensures optimal LCOE and accelerated project ROI.'
                ),
                'is_featured': True,
                'in_stock': True,
            }
        )

        p2_specs = [
            ('Rated Power Output', '670'),
            ('Maximum Efficiency', '22.8'),
            ('Cell Technology', '210mm G12 132-Half-Cell N-Type TOPCon'),
            ('Open Circuit Voltage (Voc)', '45.6'),
            ('Short Circuit Current (Isc)', '18.52'),
            ('Max Power Voltage (Vmp)', '38.4'),
            ('Max Power Current (Imp)', '17.45'),
            ('Dimensions', '2384 x 1303 x 35'),
            ('Weight', '34.2'),
            ('Operating Temperature', '-40 to +85'),
            ('Product Warranty Period', '15'),
        ]
        for idx, (attr_name, val) in enumerate(p2_specs, start=1):
            if attr_name in attr_map:
                ProductSpecification.objects.update_or_create(
                    product=p2,
                    attribute=attr_map[attr_name],
                    defaults={'value': val, 'order': idx}
                )

        # Product 3: VoltCore 10kW Hybrid Inverter
        p3, _ = Product.objects.get_or_create(
            product_code='SL-INV-10KH',
            defaults={
                'name': 'VoltCore 10kW 3-Phase Commercial Hybrid Storage Inverter',
                'category': cat_inverters,
                'brand': 'VoltCore Power',
                'model_number': 'VC-HYB-10K3P',
                'technology_type': '3-Phase Hybrid Storage',
                'power_watts': 10000,
                'short_description': 'Dual MPPT 3-phase hybrid inverter with built-in EPS backup power and high-voltage battery interface.',
                'full_description': (
                    'The VoltCore 10kW 3-Phase Hybrid Inverter provides seamless solar generation, battery charging, and grid interaction. '
                    'Equipped with 2 independent MPPT trackers and <10ms emergency power switching, it guarantees uninterrupted operation for commercial facilities.'
                ),
                'is_featured': True,
                'in_stock': True,
            }
        )

        p3_specs = [
            ('Rated Power Output', '10000'),
            ('Inverter Max AC Output', '10'),
            ('Inverter Max DC Input Voltage', '1000'),
            ('MPPT Voltage Range', '200 - 850'),
            ('Number of MPPT Trackers', '2 Trackers (2 Inputs)'),
            ('Maximum Efficiency', '98.2'),
            ('Ingress Protection', 'IP65 Water & Dust Resistant'),
            ('Dimensions', '516 x 415 x 180'),
            ('Weight', '25.0'),
            ('Product Warranty Period', '10'),
        ]
        for idx, (attr_name, val) in enumerate(p3_specs, start=1):
            if attr_name in attr_map:
                ProductSpecification.objects.update_or_create(
                    product=p3,
                    attribute=attr_map[attr_name],
                    defaults={'value': val, 'order': idx}
                )

        # Product 4: VoltCore 50kW String Inverter
        p4, _ = Product.objects.get_or_create(
            product_code='SL-INV-50KS',
            defaults={
                'name': 'VoltCore 50kW C&I Grid-Tied String Inverter',
                'category': cat_inverters,
                'brand': 'VoltCore Power',
                'model_number': 'VC-STR-50K4P',
                'technology_type': 'Commercial Grid-Tied String',
                'power_watts': 50000,
                'short_description': 'Heavy-duty 4-MPPT string inverter delivering 98.8% max efficiency and smart IV-curve diagnostic scanning.',
                'full_description': (
                    'Tailored for large commercial rooftops, carports, and distributed ground arrays. '
                    'Supports 150% DC oversizing, integrated DC disconnect switches, Type II AC/DC surge protection, and cloud fleet telemetry.'
                ),
                'is_featured': False,
                'in_stock': True,
            }
        )

        p4_specs = [
            ('Rated Power Output', '50000'),
            ('Inverter Max AC Output', '50'),
            ('Inverter Max DC Input Voltage', '1100'),
            ('MPPT Voltage Range', '200 - 1000'),
            ('Number of MPPT Trackers', '4 Trackers (8 String Inputs)'),
            ('Maximum Efficiency', '98.8'),
            ('Ingress Protection', 'IP66 Industrial Rating'),
            ('Dimensions', '650 x 530 x 280'),
            ('Weight', '52.0'),
            ('Product Warranty Period', '10'),
        ]
        for idx, (attr_name, val) in enumerate(p4_specs, start=1):
            if attr_name in attr_map:
                ProductSpecification.objects.update_or_create(
                    product=p4,
                    attribute=attr_map[attr_name],
                    defaults={'value': val, 'order': idx}
                )

        # Product 5: AetherCell 15kWh Battery Rack
        p5, _ = Product.objects.get_or_create(
            product_code='SL-BAT-15HV',
            defaults={
                'name': 'AetherCell 15kWh High-Voltage LiFePO4 Energy Storage Rack',
                'category': cat_batteries,
                'brand': 'AetherCell Energy',
                'model_number': 'AC-HV-15360',
                'technology_type': 'LiFePO4 Modular High-Voltage',
                'power_watts': 15000,
                'short_description': 'Tier-1 automotive-grade prismatic lithium iron phosphate battery stack with 6000+ cycle life.',
                'full_description': (
                    'The AetherCell 15kWh High-Voltage system is an ultra-reliable LiFePO4 commercial energy storage unit. '
                    'Features integrated multi-level aerosol fire suppression, active balancing BMS, and modular scalability up to 150kWh in parallel.'
                ),
                'is_featured': True,
                'in_stock': True,
            }
        )

        p5_specs = [
            ('Battery Nominal Capacity', '15.36'),
            ('Battery Usable Capacity', '14.2'),
            ('Battery Chemistry', 'Prismatic Lithium Iron Phosphate (LiFePO4)'),
            ('Battery Cycle Life', '6000 Cycles @ 80% DoD'),
            ('Maximum Efficiency', '96.5 Round-trip Efficiency'),
            ('Ingress Protection', 'IP55 Outdoor Enclosure'),
            ('Dimensions', '600 x 850 x 250'),
            ('Weight', '138.0'),
            ('Operating Temperature', '-10 to +50'),
            ('Product Warranty Period', '10'),
        ]
        for idx, (attr_name, val) in enumerate(p5_specs, start=1):
            if attr_name in attr_map:
                ProductSpecification.objects.update_or_create(
                    product=p5,
                    attribute=attr_map[attr_name],
                    defaults={'value': val, 'order': idx}
                )

        # Product 6: TerraMount Racking 4x2
        p6, _ = Product.objects.get_or_create(
            product_code='SL-MNT-GR04',
            defaults={
                'name': 'TerraMount Utility Ground-Mount Aluminum Racking Structure (4x2)',
                'category': cat_mounting,
                'brand': 'TerraMount Structures',
                'model_number': 'TM-ALU-GR42',
                'technology_type': 'Anodized AL6005-T5 Aluminum',
                'power_watts': 0,
                'short_description': 'Corrosion-resistant anodized aluminum ground mounting system engineered for extreme wind and snow loads.',
                'full_description': (
                    'Engineered for rapid field assembly with pre-assembled clamp modules and ramming steel posts. '
                    'Tested to withstand up to 60 m/s wind speeds and corrosive coastal environments with marine-grade anodization.'
                ),
                'is_featured': False,
                'in_stock': True,
            }
        )

        p6_specs = [
            ('Cell Technology', 'Anodized AL6005-T5 Aluminum & SUS304 Fasteners'),
            ('Ingress Protection', 'Wind Load 60 m/s • Snow Load 1.6 kN/m²'),
            ('Operating Temperature', '-40 to +85'),
            ('Product Warranty Period', '15'),
        ]
        for idx, (attr_name, val) in enumerate(p6_specs, start=1):
            if attr_name in attr_map:
                ProductSpecification.objects.update_or_create(
                    product=p6,
                    attribute=attr_map[attr_name],
                    defaults={'value': val, 'order': idx}
                )

        # Product 7: HydroSolar 7.5kW Submersible Pump
        p7, _ = Product.objects.get_or_create(
            product_code='SL-PMP-75DC',
            defaults={
                'name': 'HydroSolar 7.5kW Solar Deep-Well Submersible Pump System',
                'category': cat_pumps,
                'brand': 'HydroSolar Tech',
                'model_number': 'HS-SUB-7500DC',
                'technology_type': 'Permanent Magnet Brushless DC',
                'power_watts': 7500,
                'short_description': 'High-efficiency deep-well submersible solar water pump with smart MPPT controller for agricultural irrigation.',
                'full_description': (
                    'The HydroSolar 7.5kW Submersible Pump provides reliable water delivery for rural irrigation, livestock, and community water supply. '
                    'Capable of pumping up to 280 meters head and 45 m³/hour flow rate using direct solar DC power without grid or generator fuel dependency.'
                ),
                'is_featured': True,
                'in_stock': True,
            }
        )

        p7_specs = [
            ('Rated Power Output', '7500'),
            ('Inverter Max DC Input Voltage', '800'),
            ('MPPT Voltage Range', '350 - 650'),
            ('Ingress Protection', 'IP68 Hermetically Sealed Stainless 304'),
            ('Weight', '42.0'),
            ('Product Warranty Period', '5'),
        ]
        for idx, (attr_name, val) in enumerate(p7_specs, start=1):
            if attr_name in attr_map:
                ProductSpecification.objects.update_or_create(
                    product=p7,
                    attribute=attr_map[attr_name],
                    defaults={'value': val, 'order': idx}
                )

        self.stdout.write(self.style.SUCCESS('Products and EAV dynamic specifications loaded.'))

        # ---------------------------------------------------------
        # 4. Compliance Standards & Certifications
        # ---------------------------------------------------------
        std_iec61215, _ = ComplianceStandard.objects.get_or_create(
            name='IEC 61215:2021',
            defaults={
                'category': StandardCategory.INTERNATIONAL,
                'issuing_body': 'TÜV Rheinland / IEC',
                'description': 'Terrestrial photovoltaic (PV) modules — Design qualification and type approval under environmental stress.',
                'sort_order': 1,
            }
        )

        std_iec61730, _ = ComplianceStandard.objects.get_or_create(
            name='IEC 61730-1/2',
            defaults={
                'category': StandardCategory.ELECTRICAL,
                'issuing_body': 'TÜV Rheinland / Intertek',
                'description': 'Photovoltaic (PV) module safety qualification covering electric shock, fire hazard, and personal injury protection.',
                'sort_order': 2,
            }
        )

        std_ul1741, _ = ComplianceStandard.objects.get_or_create(
            name='UL 1741 & IEEE 1547',
            defaults={
                'category': StandardCategory.ELECTRICAL,
                'issuing_body': 'Underwriters Laboratories (UL Solutions)',
                'description': 'Standard for Inverters, Converters, Controllers and Interconnection System Equipment for use with Distributed Energy Resources.',
                'sort_order': 3,
            }
        )

        std_ce, _ = ComplianceStandard.objects.get_or_create(
            name='CE — LVD & EMC Directive',
            defaults={
                'category': StandardCategory.QUALITY,
                'issuing_body': 'European Commission Notified Bodies',
                'description': 'European Union health, electrical safety, and electromagnetic compatibility harmonized compliance.',
                'sort_order': 4,
            }
        )

        std_iso, _ = ComplianceStandard.objects.get_or_create(
            name='ISO 9001:2015 & ISO 14001:2015',
            defaults={
                'category': StandardCategory.QUALITY,
                'issuing_body': 'SGS / DNV GL',
                'description': 'Quality Management Systems and Environmental Management Standards for automated solar manufacturing facilities.',
                'sort_order': 5,
            }
        )

        # Attach Certifications
        c1, _ = Certification.objects.get_or_create(
            certificate_number='TUV-PV-2026-88902',
            defaults={
                'title': 'TÜV Rheinland Design Qualification Certificate',
                'standard': std_iec61215,
                'issuing_organization': 'TÜV Rheinland Product Safety GmbH, Cologne',
                'issue_date': date(2025, 4, 15),
                'expiry_date': date(2030, 4, 14),
                'is_valid': True,
            }
        )
        c1.products.set([p1, p2])

        c2, _ = Certification.objects.get_or_create(
            certificate_number='UL-INV-2025-44211',
            defaults={
                'title': 'UL 1741 Grid Interconnection & Anti-Islanding Certification',
                'standard': std_ul1741,
                'issuing_organization': 'UL Solutions North America',
                'issue_date': date(2025, 6, 10),
                'expiry_date': date(2029, 6, 9),
                'is_valid': True,
            }
        )
        c2.products.set([p3, p4])

        c3, _ = Certification.objects.get_or_create(
            certificate_number='CE-EU-2025-99381',
            defaults={
                'title': 'CE Declaration of Conformity (EMC & Low Voltage)',
                'standard': std_ce,
                'issuing_organization': 'Intertek Testing Services Europe',
                'issue_date': date(2025, 1, 20),
                'expiry_date': date(2028, 1, 19),
                'is_valid': True,
            }
        )
        c3.products.set([p1, p2, p3, p4, p5, p7])

        # Lab Reports
        LabReport.objects.get_or_create(
            report_number='LAB-TUV-2026-PID99',
            defaults={
                'product': p1,
                'testing_laboratory': 'TÜV Rheinland Solar Test Lab Cologne',
                'test_date': date(2025, 8, 12),
                'test_type': 'Potential Induced Degradation (PID) 96h Test',
                'result': 'Passed — Power loss < 0.9% (Standard threshold < 5%)',
                'status': LabReport.ReportStatus.EXCEEDS,
            }
        )

        LabReport.objects.get_or_create(
            report_number='LAB-PVEL-2025-HAIL35',
            defaults={
                'product': p2,
                'testing_laboratory': 'PVEL Solar Reliability Lab (USA)',
                'test_date': date(2025, 9, 5),
                'test_type': 'Hail Impact Stress Test (35mm ice projectile @ 27.2 m/s)',
                'result': 'Passed — Zero micro-fractures, dual glass integrity sustained',
                'status': LabReport.ReportStatus.VERIFIED,
            }
        )

        LabReport.objects.get_or_create(
            report_number='LAB-UL-2025-INV98',
            defaults={
                'product': p3,
                'testing_laboratory': 'UL Distributed Energy Test Facility',
                'test_date': date(2025, 7, 22),
                'test_type': 'Grid Disconnect & Anti-Islanding Response Time (<10ms)',
                'result': 'Passed — Full compliance with IEEE 1547.1 grid codes',
                'status': LabReport.ReportStatus.VERIFIED,
            }
        )

        # Warranties
        Warranty.objects.get_or_create(
            product=p1,
            defaults={
                'product_warranty_years': 12,
                'performance_warranty_years': 30,
                'coverage_details': (
                    '12-year full material and manufacturing defects replacement warranty. '
                    '30-year linear power warranty: year 1 power output >= 98.0%, years 2-30 maximum annual degradation <= 0.45%, '
                    'guaranteeing minimum 85.0% rated power output at year 30.'
                ),
                'exclusions': 'Improper grounding, mechanical impact exceeding 5400Pa, unapproved junction box tampering.',
                'operating_conditions': '-40°C to +85°C ambient, compatible with transformerless inverters.',
            }
        )

        Warranty.objects.get_or_create(
            product=p2,
            defaults={
                'product_warranty_years': 15,
                'performance_warranty_years': 30,
                'coverage_details': (
                    '15-year materials and workmanship warranty. '
                    '30-year N-Type TOPCon linear output warranty with 87.4% retention at year 30.'
                ),
                'exclusions': 'Acts of God, external chemical corrosion exceeding IEC 61701 limits.',
                'operating_conditions': 'Compatible with tracking and fixed tilt utility setups.',
            }
        )

        Warranty.objects.get_or_create(
            product=p3,
            defaults={
                'product_warranty_years': 10,
                'performance_warranty_years': 10,
                'coverage_details': '10-year factory advance replacement warranty covering electronics, firmware, and MPPT controllers.',
                'exclusions': 'Water submersion, installation without AC/DC surge protection, unauthorized chassis opening.',
                'operating_conditions': 'Wall mount, natural convective cooling, indoor or shaded outdoor IP65 placement.',
            }
        )

        Warranty.objects.get_or_create(
            product=p5,
            defaults={
                'product_warranty_years': 10,
                'performance_warranty_years': 10,
                'coverage_details': '10-year warranty or 6000 cycles at 80% Depth of Discharge, maintaining minimum 70% capacity.',
                'exclusions': 'Operation outside specified BMS thermal thresholds (-10°C to 50°C), unapproved inverter pairing.',
                'operating_conditions': 'Air-conditioned or ventilated battery container / electrical room.',
            }
        )

        self.stdout.write(self.style.SUCCESS('Standards, Certifications, Lab Reports, and Warranties loaded.'))

        # ---------------------------------------------------------
        # 5. Export Countries & Regional Logistics
        # ---------------------------------------------------------
        countries_data = [
            ('United Arab Emirates', 'AE', 'Middle East & GCC', '🇦🇪', 'Jebel Ali Port (Dubai), Port Khalifa (Abu Dhabi)', 'Customs fast-track for clean energy imports. Free-zone re-export clearance available.'),
            ('Saudi Arabia', 'SA', 'Middle East & GCC', '🇸🇦', 'King Abdulaziz Port (Dammam), Jeddah Islamic Port', 'SASO / SABER energy efficiency conformity certificates required. SolarLink provides pre-cleared SABER documentation.'),
            ('Germany', 'DE', 'Europe', '🇩🇪', 'Port of Hamburg, Port of Bremen', 'Complies with EU CE and WEEE recycling directives. Zero-customs tariff under solar component exemptions.'),
            ('Australia', 'AU', 'Asia-Pacific', '🇦🇺', 'Port of Melbourne, Sydney Port Botany, Fremantle', 'Clean Energy Council (CEC) approved listing and AS/NZS 5033 compliance documents provided.'),
            ('Kenya', 'KE', 'Africa', '🇰🇪', 'Port of Mombasa', 'PVoC (Pre-Export Verification of Conformity) and KEBS clearance supported.'),
            ('Nigeria', 'NG', 'Africa', '🇳🇬', 'Apapa Port (Lagos), Tin Can Island', 'SONCAP certification pre-arranged for expedited off-grid solar equipment clearance.'),
            ('South Africa', 'ZA', 'Africa', '🇿🇦', 'Durban Container Terminal, Cape Town', 'NRCS Letter of Authority (LOA) and SABS safety certificate compliance included.'),
            ('Oman', 'OM', 'Middle East & GCC', '🇴🇲', 'Port of Sohar, Port of Salalah', 'GCC unified customs union clearance with exemption on renewable energy equipment.'),
            ('Qatar', 'QA', 'Middle East & GCC', '🇶🇦', 'Hamad Port (Doha)', 'QASO compliance and commercial invoice attestation provided.'),
            ('India', 'IN', 'Asia-Pacific', '🇮🇳', 'Jawaharlal Nehru Port (Nhava Sheva), Mundra Port', 'ALMM and BIS compliance documentation provided for project developers.'),
        ]

        for idx, (c_name, c_code, c_reg, c_flag, c_ports, c_notes) in enumerate(countries_data, start=1):
            Country.objects.get_or_create(
                code=c_code,
                defaults={
                    'name': c_name,
                    'region': c_reg,
                    'flag_emoji': c_flag,
                    'primary_ports': c_ports,
                    'customs_notes': c_notes,
                    'is_active': True,
                    'sort_order': idx,
                }
            )

        self.stdout.write(self.style.SUCCESS(f'{len(countries_data)} Export Countries loaded.'))

        # ---------------------------------------------------------
        # 6. Shipping Terms & Incoterms
        # ---------------------------------------------------------
        incoterms_data = [
            (
                IncotermCode.FOB,
                'Free On Board (Named Port of Origin)',
                'Buyer arranges ocean freight, destination customs clearance, import tariffs, and inland transport.',
                'SolarLink delivers goods on board the carrier vessel at origin port (Shanghai / Hamburg / Jebel Ali) and handles export customs clearance.',
                'When goods pass the ship rail / loaded on board the vessel at port of origin.',
                True,
                1
            ),
            (
                IncotermCode.CIF,
                'Cost, Insurance and Freight (Named Destination Port)',
                'Buyer handles destination port terminal unloading, customs import declaration, local VAT/duties, and on-carriage to site.',
                'SolarLink pays for ocean freight carriage and procures Institute Cargo Clauses (A) marine cargo insurance to the buyer specified destination port.',
                'Risk transfers to buyer once loaded on board; SolarLink covers the financial cost of freight and insurance to destination port.',
                True,
                2
            ),
            (
                IncotermCode.CFR,
                'Cost and Freight (Named Destination Port)',
                'Buyer arranges cargo insurance and manages import customs clearance, duties, and port handling.',
                'SolarLink handles origin export documentation and pays for maritime container freight to destination seaport.',
                'Loaded on board the vessel at origin port.',
                False,
                3
            ),
            (
                IncotermCode.DDP,
                'Delivered Duty Paid (Direct to Project Site / Warehouse)',
                'Buyer only provides unloading equipment and site reception at project location.',
                'SolarLink assumes all risk, ocean freight, destination import clearance, payment of customs duties, and direct doorstep container delivery.',
                'Upon physical delivery to project site ready for unloading.',
                True,
                4
            ),
            (
                IncotermCode.DAP,
                'Delivered At Place (Destination Terminal / Jobsite)',
                'Buyer manages and pays destination customs clearance, import taxes, and VAT. Unloads containers upon arrival.',
                'SolarLink manages full international logistics and trucking to buyer site without paying local import customs taxes.',
                'Placed at buyer disposal ready for unloading at named destination point.',
                False,
                5
            ),
            (
                IncotermCode.EXW,
                'Ex Works (Factory Warehouse Floor)',
                'Buyer bears all costs and risks from factory collection, export clearance, ocean shipping, and final delivery.',
                'SolarLink makes goods available packaged and palletized at factory loading dock.',
                'When goods are made available for pickup at factory floor.',
                False,
                6
            ),
        ]

        for code, title, b_resp, s_resp, risk_pt, is_rec, sort_o in incoterms_data:
            ShippingTerm.objects.get_or_create(
                incoterm=code,
                defaults={
                    'title': title,
                    'buyer_responsibility': b_resp,
                    'seller_responsibility': s_resp,
                    'risk_transfer_point': risk_pt,
                    'is_recommended': is_rec,
                    'sort_order': sort_o,
                }
            )

        self.stdout.write(self.style.SUCCESS('Incoterms and Shipping Terms loaded.'))

        # ---------------------------------------------------------
        # 7. Export Documentation
        # ---------------------------------------------------------
        docs_data = [
            ('Commercial Invoice', 'DOC-CI', 'Itemized billing listing product codes, HS Codes (8541.40 for PV), unit pricing, currency, and trade Incoterm.', 'SolarLink Export Finance Dept', True, 1),
            ('Packing List', 'DOC-PL', 'Detailed breakdown of container numbers, gross/net weight, pallet dimensions, and serial number registries.', 'SolarLink Warehouse Logistics', True, 2),
            ('Certificate of Origin', 'DOC-COO', 'Official government/Chamber of Commerce verified certificate proving origin for preferential duty calculation.', 'Chamber of Commerce & Industry', True, 3),
            ('Ocean Bill of Lading (B/L)', 'DOC-BOL', 'Multimodal negotiable transport document issued by shipping line acknowledging receipt of containers.', 'Maersk / MSC / Hapag-Lloyd Carriers', True, 4),
            ('Factory Flash Test Data Sheet', 'DOC-FLS', 'Individual module flash test curves (Pmax, Voc, Isc, FF) calibrated under standard STC conditions.', 'Automated Manufacturing QA System', True, 5),
            ('TÜV / IEC Compliance Certificate', 'DOC-IEC', 'Notified body certificate verifying module design qualification and electrical safety.', 'TÜV Rheinland / UL Solutions', True, 6),
            ('Manufacturer Warranty Deed', 'DOC-WRN', 'Legally binding signed deed guaranteeing materials, workmanship, and linear output.', 'SolarLink Global Legal Counsel', True, 7),
            ('Pre-Shipment Inspection Report', 'DOC-PSI', 'Independent 3rd-party container loading and seal verification audit report.', 'SGS / Bureau Veritas (Upon Buyer Request)', False, 8),
        ]

        for name, code, purp, iss, is_m, sort_o in docs_data:
            ExportDocument.objects.get_or_create(
                name=name,
                defaults={
                    'code': code,
                    'purpose': purp,
                    'issuing_party': iss,
                    'is_mandatory': is_m,
                    'sort_order': sort_o,
                }
            )

        self.stdout.write(self.style.SUCCESS('Export Documentation Checklist loaded.'))
        self.stdout.write(self.style.SUCCESS('Phase 2 Data Seeding Completed Successfully!'))
