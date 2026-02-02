# Grambazaar – Rural SHG Marketplace (Django)

Grambazaar is a demo Django project showcasing a rural e‑commerce marketplace for Self Help Groups (SHGs).
It includes:

- Public marketplace with live products
- SHG registration & dashboard
- Admin dashboard (separate from Django admin)
- DigiLearner micro‑courses
- Smart rule‑based demand forecasting
- InstaBrand mock AI branding endpoint

---

## 1. Setup & Run Instructions

### Prerequisites

- Python 3.10+
- Virtualenv recommended

### Installation

```bash
cd grambazaar
python -m venv venv
venv\Scripts\activate   # On Windows
pip install django==5.2
```

### Apply migrations & create superuser (optional)

```bash
python manage.py migrate
python manage.py createsuperuser  # optional, for Django admin
```

### Load demo data

```bash
python seed_demo.py
```

This will create:

- 4 SHGs with different trust badges (bronze / silver / gold)
- 10 products with various categories
- 2 DigiLearner demo courses
- 1 sample order + ledger entry

### Run dev server

```bash
python manage.py runserver
```

Open: http://127.0.0.1:8000/

---

## 2. Demo Logins

### Django Admin (optional)

Use the superuser you created via `createsuperuser`.

### SHG Demo Logins

From `seed_demo.py`:

- Username: `shg1`  Password: `password123`
- Username: `shg2`  Password: `password123`
- Username: `shg3`  Password: `password123`
- Username: `shg4`  Password: `password123`

### Secret Admin Login

For the hackathon demo, use Django superuser or any user **without** an SHG profile via `/login/`. Non‑SHG users are treated as Grambazaar admins and redirected to `/admin/dashboard/`.

---

## 3. Key URLs & Flows

### Public Marketplace

- `/` – Home page (featured products)
- `/marketplace/` – All live products
- `/product/<slug>/` – Product detail page
- `/product/<slug>/order/` – Buyer demo checkout

### SHG Flows

- `/signup/` – SHG registration
- `/login/` – SHG / Admin login
- `/shg/dashboard/` – SHG dashboard
- `/shg/submit-product/` – Submit product request (status = pending)
- `/shg/wallet/` – Wallet & ledger view + CSV download

### Admin Dashboard (Custom, not Django admin)

- `/admin/dashboard/` – Overview metrics
- `/admin/pending-products/` – Approve/reject products
- `/admin/orders/` – Approve buyer orders
- `/admin/forecast/` – Simple rule‑based smart forecast

### InstaBrand Mock API

- `/instabrand/` –
  - GET: returns UI page
  - POST: returns mock JSON:

```json
{
  "title": "Handmade Cotton Bag",
  "description": "Crafted by SHG artisans with love and care.",
  "hashtags": "#handmade #SHG #Grambazaar #sustainable",
  "poster_url": "/static/sample_poster.jpg"
}
```

### Notifications Polling

- `/api/notifications/` – Used by SHG dashboard JS to poll forecast notifications

---

## 4. Smart Demand Forecast (Rule‑based)

Implemented in `market/views.py::generate_forecast`:

- If `product.inventory < 5` → Recommend increasing production
- If `product.category == 'food'` → Mark as seasonal demand (demo rule)
- Forecasts are displayed in `/admin/forecast/`.

(You can extend this to store data into `ForecastNotification` and show more complex insights.)

---

## 5. Hackathon Demo Flow (Suggested)

1. **Intro (1–2 min)**
   - Explain Grambazaar: digital marketplace for SHGs.
   - Show the home page & marketplace.

2. **SHG Story (2–3 min)**
   - Log in as `shg1`.
   - Show SHG dashboard: badge, wallet, notifications, DigiLearner courses.
   - Submit a new product request.

3. **Admin View (2–3 min)**
   - Log in as admin (non‑SHG user).
   - Show `/admin/dashboard/` metrics.
   - Approve pending product, show it go live in marketplace.
   - Open `/admin/forecast/` to display smart rule‑based suggestions.

4. **Buyer Journey (2–3 min)**
   - From marketplace, open a live product.
   - Click "Buy (Demo Checkout)", fill buyer form.
   - As admin, approve order in `/admin/orders/`.
   - Show SHG wallet/ledger updated (for demo order).

5. **InstaBrand Mock (1–2 min)**
   - Open `/instabrand/`.
   - Submit sample image URL + category.
   - Show JSON response with title, caption, hashtags, and mock poster URL.

---

## 6. Project Structure (Key Parts)

- `market/models.py` – SHG, Product, LedgerEntry, Order, DigiCourse, DigiProgress, ForecastNotification
- `market/forms.py` – SHG registration, product submission, buyer order
- `market/views.py` – Public views, SHG dashboard, admin dashboard, InstaBrand, forecasting
- `market/templates/market/` – All HTML templates
- `market/static/market/` – CSS & JS
- `seed_demo.py` – Populates demo data

You can extend this base for production‑grade features like payments, logistics integration, advanced analytics, and real ML‑driven forecasting.
