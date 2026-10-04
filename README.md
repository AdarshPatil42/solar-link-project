# SolarLink — Solar & Renewable Energy Equipment Export Catalog

A centralized, enterprise-grade B2B platform connecting renewable-energy equipment manufacturers and exporters with international buyers, EPC contractors, and global distributors across the Middle East, Africa, and Central Asia.

Built strictly according to the **SolarLink B2B System Specification (v1.0)** with complete Role-Based Access Control (RBAC), dynamic EAV technical specifications, export compliance documentation, multi-currency quotation engines, deal pipeline kanban, executive analytics, and RFC 4180 CSV export pipelines.

---

## 🛠 Technology Stack

- **Backend:** Python 3.14, Django 6.1+, SQLite (`db.sqlite3`), Django ORM & Authentication
- **Frontend:** Vanilla HTML5, Vanilla CSS3 SaaS Design System (No heavy CSS framework overhead), Vanilla JavaScript
- **Visual Identity:** Solar Emerald (`#059669`), Deep Forest Navy (`#064e3b`, `#0f172a`), Warm Sun Amber (`#f59e0b`), ultra-clean typography (`Inter` / `Outfit`), micro-interactions, responsive mobile-first layouts
- **Compliance & International Trade Standards:** IEC 61215, IEC 61730, IEC 62109, UL 1741, CE, ISO 9001/14001, Incoterms® 2020 (FOB, CIF, CFR, DDP, EXW)

---

## 🚀 Quick Start Guide

### 1. Activate Virtual Environment
```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (CMD)
.venv\Scripts\activate.bat

# Linux / macOS
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Database Migrations
```bash
python manage.py migrate
```

### 4. Seed Complete Master Demonstration Data
SolarLink includes a master seeder that populates the database with realistic Tier-1 solar equipment, technical EAV specs, TUV test certificates, export destinations, buyer dossiers, active RFQs, and commercial quotations:
```bash
python manage.py seed_solarlink
```

### 5. Run the Automated Test Suite (44 Tests)
```bash
python manage.py test
```

### 6. Start the Development Server
```bash
python manage.py runserver 127.0.0.1:8000
```
Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## 🔐 Demonstration Accounts & Role Portals

| Role | Username | Password | Dedicated Portal URL | Key Capabilities |
| :--- | :--- | :--- | :--- | :--- |
| **System Administrator** | `admin` | `admin123` | `/dashboard/admin-portal/` | Executive KPI dashboard, conversion analytics, deal velocity, 5x CSV exports, user governance |
| **Sales Representative** | `sales_alex` | `solarlink123` | `/sales/dashboard/` | 7-stage Deal Kanban pipeline, Enquiry assignment, Quotation builder, revision history |
| **International Buyer (Oman)** | `buyer_tariq` | `solarlink123` | `/dashboard/` | RFQ status tracking (`ENQ-YYYY-XXXXX`), Commercial quote review, saved equipment bookmarking |
| **International Buyer (Egypt)** | `buyer_hassan` | `solarlink123` | `/dashboard/` | EPC contractor dashboard, battery storage RFQs, quotation acceptance |

---

## 🏗 Complete Architecture & Features

```
solar-link/
├── accounts/          # User authentication, UserProfile, role decorators, saved equipment
├── catalog/           # Categories, Tier-1 Products, EAV dynamic specifications, multi-images
├── certifications/    # IEC/UL/CE standards, accredited lab reports, manufacturer warranties
├── exports/           # Incoterms 2020, destination countries, port logistics, export documents
├── enquiries/         # Lead engine, multi-step RFQs, unique ENQ references, Quotation engine
├── pages/             # High-conversion Homepage, About Us, Team directory, Contact desk & FAQ
├── dashboard/         # Role-based Buyer/Sales/Admin Portals, 5x CSV data exporters, seeder
├── config/            # Master Django settings, routing, media/static configuration
├── templates/         # Master layouts, semantic includes, custom 404/500 error pages
└── static/            # Curated Vanilla CSS3 design system and interactive ES6 scripts
```

### 1. Catalog & Dynamic EAV Specification Engine (`catalog`)
- Hierarchical categories (Solar PV Panels, Hybrid & String Inverters, Energy Storage Batteries, Mounting Systems, Balance of System).
- Dynamic Entity-Attribute-Value (EAV) specification engine storing precise electrical and physical metrics (Efficiency %, Voc, Isc, MPPT range, Cycle life, Cell chemistry).
- Search, filter by brand, category, power output, and instant product bookmarking.

### 2. Certifications & Export Intelligence (`certifications` & `exports`)
- Accredited test standards (IEC, UL, CE, ISO) with issuing authority verification.
- Downloadable technical datasheets, lab reports, and warranty certificates (12-year product / 25-year performance warranties).
- International logistics profiles: Destination seaports, Incoterms® 2020 rules, transit times, and customs documentation requirements.

### 3. Enquiry & Lead Engine (`enquiries`)
- Direct product enquiries and multi-step Project RFQ generator with automated lead reference generation: `ENQ-YYYY-XXXXX`.
- Granular tracking across 7 stages: `New`, `Assigned`, `Under Review`, `Quote Sent`, `Negotiation`, `Won`, and `Lost`.
- Automatic buyer association for authenticated users and guest lead capture with automatic dossier creation.

### 4. Multi-Currency Quotation Builder & Sales Pipeline (`dashboard` / `enquiries`)
- Commercial proforma quotation engine with automatic expiry dates, payment terms, and freight inclusion.
- 7-Stage visual Deal Kanban board with real-time stage progression.
- Buyer quotation review portal with interactive Accept/Decline actions and status notifications.

### 5. Admin Control Center & Analytics Hub (`dashboard`)
- Executive KPI metrics: Total catalog assets, buyer accounts, active pipeline value, won revenue, and win rates.
- Interactive distribution bars: Demand by application type (Utility, C&I, Residential, Off-Grid), catalog volume, and top export destination markets.
- **5x Universal CSV Export Engines:**
  1. `Products Catalog Export` (`/dashboard/export/products/`)
  2. `Project Enquiries Export` (`/dashboard/export/enquiries/`)
  3. `Verified Buyers Export` (`/dashboard/export/buyers/`)
  4. `Commercial Quotations Export` (`/dashboard/export/quotations/`)
  5. `Sales Pipeline Export` (`/dashboard/export/pipeline/`)

---

## 🧪 Automated Test Suite

All 44 automated tests pass cleanly across every subsystem:
```bash
python manage.py test
```
- `accounts`: User authentication, profile roles, saved products API
- `catalog`: Product creation, category filtering, EAV attribute values
- `certifications`: Standard models, warranty relations
- `exports`: Country shipping routes, Incoterms 2020 rules
- `enquiries`: RFQ submission, ENQ number format validation, quotation generation
- `dashboard`: Role access controls, sales kanban pipeline, admin metrics, and all 5 CSV export downloads

---

## 📋 5-Phase Implementation Summary

- [x] **Phase 1: Foundation, UI Design System & Authentication**
  - Django core setup, custom UserProfile model, RBAC decorators, Vanilla CSS SaaS design system, base layouts.
- [x] **Phase 2: Catalog, Dynamic EAV Specs, Certifications & Export Intelligence**
  - Product catalog, EAV attributes, certification standards, country shipping profiles, logistics explorer.
- [x] **Phase 3: Public Presence, Lead Generation & Enquiry Engine**
  - High-conversion homepage, About Us, Team directory, Contact desk, FAQ, RFQ submission workflow, ENQ generator.
- [x] **Phase 4: Buyer & Sales Executive Portals + Quotation Engine**
  - Buyer RFQ and quote review workspace, Sales Executive Kanban pipeline, Commercial quotation generator.
- [x] **Phase 5: Admin Control Center, Analytics, 5x CSV Export & Production Polish**
  - Admin executive dashboard, market distribution analytics, 5x RFC 4180 CSV export pipelines, master data seeder (`seed_solarlink`), custom 404/500 templates, and full test suite verification.
