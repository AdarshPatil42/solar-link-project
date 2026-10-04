# SolarLink — Solar & Renewable Energy Equipment Export Catalog

A centralized, web-based B2B platform connecting renewable-energy equipment manufacturers and exporters with international buyers, EPC contractors, and global distributors.

---

## 🛠 Technology Stack
- **Backend:** Python 3.14, Django 6.1+, SQLite (`db.sqlite3`), Django ORM & Authentication
- **Frontend:** Vanilla HTML5, Modern CSS3 Design System, Vanilla JavaScript
- **Aesthetic:** Clean SaaS theme with Solar Emerald (`#059669`) and Warm Sun Amber (`#F59E0B`) accents, rounded cards, soft drop shadows, and micro-interactions

---

## 🚀 Quick Start

### 1. Activate Virtual Environment
```bash
# Windows
.venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Database Migrations
```bash
python manage.py migrate
```

### 4. Seed Demonstration Users
```bash
python manage.py setup_phase1_users
```

### 5. Start Development Server
```bash
python manage.py runserver 127.0.0.1:8000
```
Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## 🔐 Demonstration Credentials

| Role | Username | Password | Purpose |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `admin123` | Full system access, catalog & user governance, analytics |
| **Sales Executive** | `sales_alex` | `solarlink123` | Lead assignment, quotation generation, pipeline management |
| **International Buyer** | `buyer_tariq` | `solarlink123` | Product saving, enquiry tracking (`ENQ-YYYY-XXXXX`), RFQ review |

---

## 📂 Modular Architecture
```
Solar Link/
├── accounts/          # User authentication, UserProfile, SavedProducts, RBAC decorators
├── catalog/           # Categories, Products, Images, EAV dynamic specifications
├── certifications/    # IEC/UL/CE/ISO compliance standards, lab reports, warranties
├── exports/           # Incoterms (FOB, CIF, DDP, etc.), destination countries, export docs
├── enquiries/         # Project enquiry forms, bulk RFQs, ENQ tracking, quotations
├── pages/             # Home, About Us, Team directory, Contact & FAQ
├── dashboard/         # Role-specific workspaces (Buyer, Sales, Admin) and CSV exports
├── config/            # Django project settings and master URL routing
├── templates/         # Master layouts, reusable includes, and app views
└── static/            # Design system CSS and interactive JavaScript
```

---

## 📋 5-Phase Roadmap Status
- [x] **Phase 1: Foundation, UI Design System & Authentication**
- [ ] **Phase 2: Catalog, Dynamic EAV Specs, Certifications & Export Intelligence**
- [ ] **Phase 3: Public Presence, Lead Generation & Enquiry Engine**
- [ ] **Phase 4: Buyer & Sales Executive Portals + Quotation Engine**
- [ ] **Phase 5: Admin Control Center, Analytics, CSV Export & Production Polish**
